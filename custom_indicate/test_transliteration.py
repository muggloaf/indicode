"""
Testing framework for the enhanced transliteration system.
This implements the concepts described in testing_framework_explanation.py
"""

import unittest
import json
import os
from pathlib import Path

# Import the enhanced transliteration module
from custom_indicate.enhanced_transliteration import (
    EnhancedTransliterator,
    enhanced_hindi2english,
    enhanced_marathi2english
)

class TransliterationTestDataset:
    """Class to manage test datasets for transliteration testing"""
    
    def __init__(self, name, language='hindi'):
        """
        Initialize a test dataset
        
        Args:
            name: Name of the dataset
            language: Language of the dataset ('hindi' or 'marathi')
        """
        self.name = name
        self.language = language
        self.test_cases = []
        self.metadata = {}
    
    def add_test_case(self, original, expected_transliteration, category=None, 
                      difficulty=None, tags=None):
        """
        Add a test case to the dataset
        
        Args:
            original: Original text in Hindi/Marathi
            expected_transliteration: Expected transliteration output
            category: Category of the test case (e.g., 'names', 'technical')
            difficulty: Difficulty level ('easy', 'medium', 'hard')
            tags: List of tags for the test case
        """
        self.test_cases.append({
            'original': original,
            'expected': expected_transliteration,
            'category': category or 'general',
            'difficulty': difficulty or 'medium',
            'tags': tags or []
        })
    
    def load_from_file(self, file_path):
        """
        Load test cases from a JSON file
        
        Args:
            file_path: Path to the JSON file containing test cases
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            if 'metadata' in data:
                self.metadata = data['metadata']
            
            if 'test_cases' in data:
                self.test_cases = data['test_cases']
                
            return True
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"Error loading test dataset: {e}")
            return False
    
    def save_to_file(self, file_path):
        """
        Save test cases to a JSON file
        
        Args:
            file_path: Path to save the JSON file
        """
        try:
            data = {
                'metadata': self.metadata,
                'test_cases': self.test_cases
            }
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                
            return True
        except Exception as e:
            print(f"Error saving test dataset: {e}")
            return False
    
    def filter_by_category(self, category):
        """
        Filter test cases by category
        
        Args:
            category: Category to filter by
            
        Returns:
            List of filtered test cases
        """
        return [tc for tc in self.test_cases if tc['category'] == category]


class TransliterationEvaluator:
    """Class to evaluate transliteration results"""
    
    def __init__(self):
        """Initialize the evaluator"""
        self.metrics = {}
    
    def calculate_character_accuracy(self, actual, expected):
        """
        Calculate character-level accuracy
        
        Args:
            actual: Actual transliteration
            expected: Expected transliteration
            
        Returns:
            Float between 0 and 1 representing accuracy
        """
        if not actual or not expected:
            return 0.0
            
        # Calculate Levenshtein distance (character-level edit distance)
        m, n = len(actual), len(expected)
        
        # Create distance matrix
        distance = [[0 for _ in range(n + 1)] for _ in range(m + 1)]
        
        for i in range(m + 1):
            distance[i][0] = i
        for j in range(n + 1):
            distance[0][j] = j
            
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if actual[i-1] == expected[j-1]:
                    distance[i][j] = distance[i-1][j-1]
                else:
                    distance[i][j] = min(
                        distance[i-1][j] + 1,    # deletion
                        distance[i][j-1] + 1,    # insertion
                        distance[i-1][j-1] + 1   # substitution
                    )
        
        # Calculate accuracy as 1 - normalized edit distance
        max_len = max(m, n)
        if max_len == 0:
            return 1.0
            
        accuracy = 1.0 - (distance[m][n] / max_len)
        return accuracy
    
    def calculate_word_accuracy(self, actual, expected):
        """
        Calculate word-level accuracy
        
        Args:
            actual: Actual transliteration
            expected: Expected transliteration
            
        Returns:
            Float between 0 and 1 representing accuracy
        """
        if not actual or not expected:
            return 0.0
            
        # Split into words
        actual_words = actual.split()
        expected_words = expected.split()
        
        # Count exact word matches
        matches = sum(1 for a, e in zip(actual_words, expected_words) if a == e)
        
        # Calculate accuracy
        total_words = max(len(actual_words), len(expected_words))
        if total_words == 0:
            return 1.0
            
        return matches / total_words


class TransliterationTestRunner:
    """Class to run transliteration tests"""
    
    def __init__(self, transliterator, datasets=None):
        """
        Initialize the test runner
        
        Args:
            transliterator: Transliterator instance to test
            datasets: List of TransliterationTestDataset instances
        """
        self.transliterator = transliterator
        self.datasets = datasets or []
        self.evaluator = TransliterationEvaluator()
        self.results = {}
    
    def add_dataset(self, dataset):
        """
        Add a dataset to test
        
        Args:
            dataset: TransliterationTestDataset instance
        """
        self.datasets.append(dataset)
    
    def run_tests(self, dataset_name=None, feature_flags=None):
        """
        Run tests on specified dataset or all datasets
        
        Args:
            dataset_name: Optional name of dataset to test
            feature_flags: Dict of feature flags to pass to transliterator
            
        Returns:
            Dict of test results
        """
        results = {}
        
        for dataset in self.datasets:
            if dataset_name and dataset.name != dataset_name:
                continue
                
            dataset_results = []
            for test_case in dataset.test_cases:
                # Run the transliteration
                actual_result = self.transliterator.transliterate(
                    test_case['original'],
                    enable_features=feature_flags
                )
                
                # Evaluate results
                char_accuracy = self.evaluator.calculate_character_accuracy(
                    actual_result, test_case['expected'])
                word_accuracy = self.evaluator.calculate_word_accuracy(
                    actual_result, test_case['expected'])
                
                # Determine if test passed (80% word accuracy is passing)
                passed = word_accuracy >= 0.8
                
                dataset_results.append({
                    'test_case': test_case,
                    'actual_result': actual_result,
                    'evaluation': {
                        'char_accuracy': char_accuracy,
                        'word_accuracy': word_accuracy
                    },
                    'passed': passed
                })
            
            # Calculate overall statistics
            results[dataset.name] = {
                'total_cases': len(dataset.test_cases),
                'passed_cases': sum(1 for r in dataset_results if r['passed']),
                'detailed_results': dataset_results,
                'average_char_accuracy': sum(r['evaluation']['char_accuracy'] 
                                         for r in dataset_results) / max(len(dataset_results), 1),
                'average_word_accuracy': sum(r['evaluation']['word_accuracy'] 
                                         for r in dataset_results) / max(len(dataset_results), 1),
            }
        
        self.results = results
        return results
    
    def generate_report(self, output_format='text'):
        """
        Generate a detailed test report
        
        Args:
            output_format: Format of report ('text' or 'html')
            
        Returns:
            Report string
        """
        if not self.results:
            return "No test results available. Run tests first."
        
        if output_format == 'text':
            report = []
            report.append("=" * 60)
            report.append("TRANSLITERATION TEST REPORT")
            report.append("=" * 60)
            
            for dataset_name, dataset_results in self.results.items():
                report.append(f"\nDataset: {dataset_name}")
                report.append("-" * 40)
                report.append(f"Total test cases: {dataset_results['total_cases']}")
                report.append(f"Passed test cases: {dataset_results['passed_cases']}")
                report.append(f"Success rate: {dataset_results['passed_cases'] / max(dataset_results['total_cases'], 1) * 100:.1f}%")
                report.append(f"Average character accuracy: {dataset_results['average_char_accuracy'] * 100:.1f}%")
                report.append(f"Average word accuracy: {dataset_results['average_word_accuracy'] * 100:.1f}%")
                
                report.append("\nDetailed Results:")
                for i, result in enumerate(dataset_results['detailed_results']):
                    report.append(f"\n  Test Case {i+1}: " + ("PASSED" if result['passed'] else "FAILED"))
                    report.append(f"  Original: {result['test_case']['original']}")
                    report.append(f"  Expected: {result['test_case']['expected']}")
                    report.append(f"  Actual: {result['actual_result']}")
                    report.append(f"  Character Accuracy: {result['evaluation']['char_accuracy'] * 100:.1f}%")
                    report.append(f"  Word Accuracy: {result['evaluation']['word_accuracy'] * 100:.1f}%")
            
            return "\n".join(report)
        else:
            # HTML report could be implemented here
            return "HTML report not implemented yet"


# Test cases for each feature
class TestTransliterationFeatures(unittest.TestCase):
    """Unit tests for enhanced transliteration features"""
    
    def setUp(self):
        """Set up test environment"""
        self.hindi_transliterator = EnhancedTransliterator('hindi')
        self.marathi_transliterator = EnhancedTransliterator('marathi')
        
    def test_basic_transliteration(self):
        """Test basic transliteration works"""
        hindi_text = "नमस्ते"
        result = self.hindi_transliterator.transliterate(hindi_text)
        self.assertEqual(result, "Namaste")
        
    def test_auto_capitalization(self):
        """Test auto-capitalization feature"""
        # Test with capitalization enabled
        hindi_text = "नमस्ते दुनिया। मेरा नाम राहुल है।"
        result_with_caps = self.hindi_transliterator.transliterate(
            hindi_text, 
            enable_features={'auto_capitalization': True}
        )
        
        # Test with capitalization disabled
        result_without_caps = self.hindi_transliterator.transliterate(
            hindi_text, 
            enable_features={'auto_capitalization': False}
        )
        
        # Check that capitalization is correctly applied
        self.assertTrue(result_with_caps[0].isupper(), 
                        f"First letter not capitalized in: {result_with_caps}")
        
        # Check sentence capitalization
        sentences_with_caps = result_with_caps.split('. ')
        if len(sentences_with_caps) > 1:
            self.assertTrue(sentences_with_caps[1][0].isupper(), 
                            f"Second sentence not capitalized in: {result_with_caps}")
        
        # Check names are capitalized
        self.assertIn("Rahul", result_with_caps)
        
        # Check that with capitalization disabled, text isn't automatically capitalized
        if result_without_caps != result_with_caps:
            self.assertTrue(any(c.islower() for c in result_without_caps[0]), 
                           f"Text still capitalized even with feature disabled: {result_without_caps}")
    
    def test_context_aware_transliteration(self):
        """Test context-aware transliteration feature"""
        # Test with context aware enabled vs disabled
        hindi_text = "श्री नरेंद्र मोदी भारत के प्रधान मंत्री हैं"
        
        result_with_context = self.hindi_transliterator.transliterate(
            hindi_text, 
            enable_features={'context_aware': True}
        )
        
        result_without_context = self.hindi_transliterator.transliterate(
            hindi_text, 
            enable_features={'context_aware': False}
        )
        
        # Verify we get different results (context should improve transliteration)
        self.assertIn("Shri", result_with_context, 
                     f"Expected honorific 'Shri' in context-aware result: {result_with_context}")
    
    def test_schwa_deletion(self):
        """Test statistical schwa deletion"""
        hindi_text = "कमल"  # Should be "Kamal" not "Kamala"
        
        result_with_schwa = self.hindi_transliterator.transliterate(
            hindi_text, 
            enable_features={'statistical_schwa': True}
        )
        
        result_without_schwa = self.hindi_transliterator.transliterate(
            hindi_text, 
            enable_features={'statistical_schwa': False}
        )
        
        # With schwa deletion, should be shorter
        self.assertLess(len(result_with_schwa), len(result_without_schwa), 
                       f"Schwa deletion should result in shorter text: {result_with_schwa} vs {result_without_schwa}")
        
        # The schwa-deleted version should be "Kamal"
        self.assertEqual(result_with_schwa.lower(), "kamal", 
                        f"Expected 'Kamal' with schwa deletion, got: {result_with_schwa}")
    
    def test_all_features_together(self):
        """Test all features working together"""
        hindi_text = "नमस्ते दुनिया। मेरा नाम राहुल है। मैं भारत से हूँ।"
          # All features enabled
        result_all_features = self.hindi_transliterator.transliterate(hindi_text)
        
        # All features disabled
        result_no_features = self.hindi_transliterator.transliterate(
            hindi_text, 
            enable_features={
                'context_aware': False, 
                'statistical_schwa': False,
                'auto_exceptions': False,
                'auto_capitalization': False
            }
        )
        
        # Should get different results
        self.assertNotEqual(result_all_features, result_no_features, 
                          "Expected different results with all features on vs off")
        
        # With all features, should be properly capitalized
        self.assertTrue(result_all_features[0].isupper(), 
                      f"First letter should be capitalized with all features: {result_all_features}")


# Create and run a sample dataset
def create_sample_test_dataset():
    """Create and return a sample test dataset"""
    dataset = TransliterationTestDataset("hindi_sample", "hindi")
    
    # Add test cases for each feature
    
    # Basic transliteration
    dataset.add_test_case(
        "नमस्ते", 
        "Namaste", 
        category="basic"
    )
    
    # Auto capitalization
    dataset.add_test_case(
        "नमस्ते दुनिया।", 
        "Namaste duniya.", 
        category="capitalization"
    )
    
    # Schwa deletion
    dataset.add_test_case(
        "कमल", 
        "Kamal", 
        category="schwa"
    )
    
    # Context awareness
    dataset.add_test_case(
        "श्री नरेंद्र मोदी", 
        "Shri Narendra Modi", 
        category="context"
    )
    
    # Combined features
    dataset.add_test_case(
        "मेरा नाम राहुल है। मैं भारत से हूँ।", 
        "Mera naam Rahul hai. Main Bharat se hoon.", 
        category="combined"
    )
    
    return dataset


def run_sample_tests():
    """Run tests on a sample dataset and print results"""
    # Create dataset
    dataset = create_sample_test_dataset()
    
    # Create transliterator
    transliterator = EnhancedTransliterator('hindi')
    
    # Create test runner
    test_runner = TransliterationTestRunner(transliterator)
    test_runner.add_dataset(dataset)
    
    # Run tests with all features enabled
    print("Running tests with all features enabled...")
    results_all = test_runner.run_tests()
    print(test_runner.generate_report())
    
    # Run tests with features selectively disabled
    print("\nRunning tests with auto-capitalization disabled...")
    results_no_caps = test_runner.run_tests(
        feature_flags={'auto_capitalization': False}
    )
    print(test_runner.generate_report())


if __name__ == "__main__":
    # Run the unit tests
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
    
    # Run the sample test dataset
    print("\n" + "=" * 60)
    print("RUNNING SAMPLE DATASET TESTS")
    print("=" * 60)
    run_sample_tests()
