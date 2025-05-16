"""
Automatic exception detection module for Hindi/Marathi transliteration.
This module helps identify and handle exceptions to standard transliteration rules.
"""

import re
import json
import os.path
from collections import Counter
from .transliterate import hindi2english, marathi2english, preprocess_text
from .schwa_deletion import apply_schwa_rules

class ExceptionDetector:
    """
    Class to detect and manage exceptions in transliteration.
    Uses statistical analysis of transliteration patterns to identify
    potential exceptions that don't follow regular rules.
    """
    
    def __init__(self, language='hindi', exception_file=None):
        """
        Initialize the exception detector
        
        Args:
            language: 'hindi' or 'marathi'
            exception_file: Path to store/load exceptions (JSON format)
        """
        self.language = language
        self.exception_file = exception_file or f"{language}_exceptions.json"
        self.exceptions = {}
        self.load_exceptions()
        
        # Track word frequency for confidence scoring
        self.word_frequency = Counter()
        
        # Track rule violations for identifying potential exceptions
        self.rule_violations = {}
        
        # Define common patterns that may need special handling
        self.common_patterns = {
            'ending_vowel': r'[aeiou]$',
            'consonant_cluster': r'([bcdfghjklmnpqrstvwxyz])\1',  # Double consonants
            'unusual_cluster': r'[bcdfghjklmnpqrstvwxyz]{3,}',    # 3+ consonants in a row
        }
    
    def load_exceptions(self):
        """Load exceptions from file if it exists"""
        if os.path.exists(self.exception_file):
            try:
                with open(self.exception_file, 'r', encoding='utf-8') as f:
                    self.exceptions = json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error loading exceptions: {e}")
                self.exceptions = {}
    
    def save_exceptions(self):
        """Save exceptions to file"""
        try:
            with open(self.exception_file, 'w', encoding='utf-8') as f:
                json.dump(self.exceptions, f, ensure_ascii=False, indent=2)
        except IOError as e:
            print(f"Error saving exceptions: {e}")
    
    def analyze_transliteration(self, original_text, transliterated_text, expected_text=None):
        """
        Analyze transliteration and identify potential exceptions
        
        Args:
            original_text: Original Hindi/Marathi text
            transliterated_text: The transliterated result
            expected_text: Expected transliteration (if available for training)
            
        Returns:
            Dictionary of detected exceptions
        """
        # Preprocess texts
        original_text = preprocess_text(original_text)
        transliterated_words = transliterated_text.split()
        original_words = original_text.split()
        expected_words = expected_text.split() if expected_text else None
        
        detected_exceptions = {}
        
        # Process each word if lengths match
        if len(original_words) == len(transliterated_words):
            for i, (orig, trans) in enumerate(zip(original_words, transliterated_words)):
                # Update word frequency
                self.word_frequency[orig] += 1
                
                # Check if expected text is available and differs from transliteration
                if expected_words and i < len(expected_words) and trans != expected_words[i]:
                    detected_exceptions[orig] = expected_words[i]
                    continue
                
                # Detect rule violations or unusual patterns
                violations = self.detect_rule_violations(orig, trans)
                if violations:
                    if orig not in self.rule_violations:
                        self.rule_violations[orig] = []
                    self.rule_violations[orig].append(violations)
        
        # Analyze rule violations to detect consistent exceptions
        new_exceptions = self.analyze_rule_violations()
        detected_exceptions.update(new_exceptions)
        
        # Update the exceptions dictionary
        self.exceptions.update(detected_exceptions)
        
        return detected_exceptions
    
    def detect_rule_violations(self, original_word, transliterated_word):
        """
        Detect potential rule violations in transliteration
        
        Returns:
            List of rule violation types or None
        """
        violations = []
        
        # Check for consonant handling issues
        if re.search(self.common_patterns['consonant_cluster'], transliterated_word):
            violations.append('consonant_cluster')
        
        # Check for unusual consonant clusters
        if re.search(self.common_patterns['unusual_cluster'], transliterated_word):
            violations.append('unusual_cluster')
        
        # Analyze schwa deletion patterns
        # Try both with and without schwa deletion
        with_schwa = transliterated_word
        without_schwa = apply_schwa_rules(transliterated_word)
        
        if with_schwa != without_schwa:
            violations.append('schwa_deletion')
        
        return violations if violations else None
    
    def analyze_rule_violations(self, min_frequency=3, confidence_threshold=0.75):
        """
        Analyze collected rule violations to detect consistent exceptions
        
        Returns:
            Dictionary of detected exceptions
        """
        new_exceptions = {}
        
        for word, violations_list in self.rule_violations.items():
            # Only consider words that appear frequently enough
            if self.word_frequency[word] < min_frequency:
                continue
            
            # Count violation types
            violation_counts = Counter()
            for violations in violations_list:
                for v in violations:
                    violation_counts[v] += 1
            
            # Calculate confidence for each violation type
            for violation_type, count in violation_counts.items():
                confidence = count / self.word_frequency[word]
                
                # If confidence is high enough, mark as an exception
                if confidence >= confidence_threshold:
                    # Re-transliterate with special handling based on violation type
                    fixed_transliteration = self.apply_special_handling(word, violation_type)
                    if fixed_transliteration:
                        new_exceptions[word] = fixed_transliteration
        
        return new_exceptions
    
    def apply_special_handling(self, original_word, violation_type):
        """
        Apply special handling for a specific rule violation type
        
        Returns:
            Fixed transliteration or None if no special handling available
        """
        # Get default transliteration first
        if self.language == 'hindi':
            default_transliteration = hindi2english(original_word)
        else:  # marathi
            default_transliteration = marathi2english(original_word)
        
        # Apply specific fixes based on violation type
        if violation_type == 'consonant_cluster':
            # Special handling for consonant clusters
            # For example, handle gemination (double consonants)
            return re.sub(r'([bcdfghjklmnpqrstvwxyz])\1+', r'\1\1', default_transliteration)
            
        elif violation_type == 'unusual_cluster':
            # Break up unusual consonant clusters with vowels
            return re.sub(r'([bcdfghjklmnpqrstvwxyz]{3,})', 
                         lambda m: m.group(0)[0] + 'a' + m.group(0)[1:], 
                         default_transliteration)
            
        elif violation_type == 'schwa_deletion':
            # Force aggressive schwa deletion for this word
            return apply_schwa_rules(default_transliteration, original_word)
        
        return None
    
    def get_exception(self, word):
        """Get exception for a word if it exists"""
        return self.exceptions.get(word)
    
    def add_exception(self, original_word, correct_transliteration):
        """Manually add an exception"""
        self.exceptions[original_word] = correct_transliteration
        self.save_exceptions()
    
    def remove_exception(self, original_word):
        """Remove an exception"""
        if original_word in self.exceptions:
            del self.exceptions[original_word]
            self.save_exceptions()
            return True
        return False
    
    def batch_analyze(self, corpus_pairs):
        """
        Analyze a batch of original-transliteration pairs
        
        Args:
            corpus_pairs: List of (original, transliteration, [expected]) tuples
        
        Returns:
            Dictionary of detected exceptions
        """
        all_exceptions = {}
        
        for pair in corpus_pairs:
            if len(pair) == 2:
                original, transliteration = pair
                expected = None
            else:
                original, transliteration, expected = pair
            
            exceptions = self.analyze_transliteration(original, transliteration, expected)
            all_exceptions.update(exceptions)
        
        self.save_exceptions()
        return all_exceptions


# Helper functions for automatic exception detection

def identify_exceptions(text, transliterated_text, expected_text=None, language='hindi'):
    """
    Identify potential exceptions in transliteration
    
    Args:
        text: Original text in Hindi/Marathi
        transliterated_text: Automatically transliterated text
        expected_text: Manually corrected transliteration (optional)
        language: 'hindi' or 'marathi'
    
    Returns:
        Dictionary of potential exceptions
    """
    detector = ExceptionDetector(language)
    return detector.analyze_transliteration(text, transliterated_text, expected_text)

def learn_from_corrections(original_texts, transliterated_texts, corrected_texts, language='hindi'):
    """
    Learn exceptions from user corrections
    
    Args:
        original_texts: List of original Hindi/Marathi texts
        transliterated_texts: List of automatically transliterated texts
        corrected_texts: List of manually corrected transliterations
        language: 'hindi' or 'marathi'
    
    Returns:
        Dictionary of learned exceptions
    """
    detector = ExceptionDetector(language)
    corpus_pairs = list(zip(original_texts, transliterated_texts, corrected_texts))
    return detector.batch_analyze(corpus_pairs)
