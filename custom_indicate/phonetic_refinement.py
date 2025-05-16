"""
Phonetic Rule Refinement module for Hindi/Marathi transliteration.
This module refines phonetic rules for more accurate transliteration.
"""

import re
import json
import os.path
from collections import defaultdict

class PhoneticRuleRefiner:
    """
    Class to refine phonetic rules for Hindi/Marathi transliteration.
    Implements advanced rule detection, weighting, and application
    to improve transliteration accuracy.
    """
    
    def __init__(self, language='hindi', rules_file=None):
        """
        Initialize the phonetic rule refiner
        
        Args:
            language: 'hindi' or 'marathi'
            rules_file: Path to store/load refined rules (JSON format)
        """
        self.language = language
        self.rules_file = rules_file or f"{language}_refined_rules.json"
        
        # Default phonetic rules
        self.default_rules = {
            # Consonant patterns
            'consonant_clusters': [
                # Format: (pattern, replacement)
                (r'ksh', 'kṣ'),     # क्ष
                (r'gj?[nñ]', 'jñ'),  # ज्ञ
                (r'[dt][rṛ]', 'ṭr'),  # ट्र/ड्र
                (r'[dt][hḥ]', 'dh'),  # ध
            ],
            
            # Vowel patterns
            'vowel_rules': [
                (r'aa', 'ā'),
                (r'ee', 'ī'),
                (r'oo', 'ū'),
                (r'ai', 'ai'),
                (r'au', 'au'),
            ],
            
            # Nasalization rules
            'nasalization': [
                (r'n([kgcjṭḍtdpb])', 'ṃ\\1'),  # Convert n to anusvara before consonants
            ],
            
            # Aspiration rules
            'aspiration': [
                (r'([kgcjṭḍtdpb])h', '\\1ʰ'),  # Mark aspirated consonants
            ]
        }
        
        # Refined rules (will be loaded from file if available)
        self.refined_rules = self.load_rules() or self.default_rules.copy()
        
        # Rule weights (for determining which rules take precedence)
        self.rule_weights = defaultdict(float)
        
        # Rule application statistics (track how often each rule is used)
        self.rule_stats = defaultdict(int)
        
        # Special phonetic contexts for contextual rule application
        self.phonetic_contexts = {
            'word_initial': r'^\W*',     # Word-initial position
            'word_final': r'\W*$',      # Word-final position
            'before_vowel': r'(?=[aeiouāīūṛḷ])', # Before vowel
            'after_vowel': r'(?<=[aeiouāīūṛḷ])', # After vowel
            'between_vowels': r'(?<=[aeiouāīūṛḷ])(?=[aeiouāīūṛḷ])', # Between vowels
        }
    
    def load_rules(self):
        """Load refined rules from file if it exists"""
        if os.path.exists(self.rules_file):
            try:
                with open(self.rules_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error loading refined rules: {e}")
                return None
        return None
    
    def save_rules(self):
        """Save refined rules to file"""
        try:
            with open(self.rules_file, 'w', encoding='utf-8') as f:
                json.dump(self.refined_rules, f, ensure_ascii=False, indent=2)
        except IOError as e:
            print(f"Error saving refined rules: {e}")
    
    def add_rule(self, category, pattern, replacement, context=None, weight=1.0):
        """
        Add or update a phonetic rule
        
        Args:
            category: Rule category (e.g., 'consonant_clusters', 'vowel_rules')
            pattern: Regex pattern to match
            replacement: Replacement text
            context: Optional phonetic context for contextual rules
            weight: Rule weight (higher takes precedence)
        """
        # Create context-specific pattern if context is provided
        if context and context in self.phonetic_contexts:
            pattern = f"{self.phonetic_contexts[context]}{pattern}"
        
        # Add or update rule
        rule = (pattern, replacement)
        
        if category not in self.refined_rules:
            self.refined_rules[category] = []
        
        # Check if rule already exists
        for i, existing_rule in enumerate(self.refined_rules[category]):
            if existing_rule[0] == pattern:
                # Update existing rule
                self.refined_rules[category][i] = rule
                self.rule_weights[(category, pattern)] = weight
                return
        
        # Add new rule
        self.refined_rules[category].append(rule)
        self.rule_weights[(category, pattern)] = weight
        
        # Save updated rules
        self.save_rules()
    
    def remove_rule(self, category, pattern):
        """Remove a phonetic rule"""
        if category in self.refined_rules:
            original_len = len(self.refined_rules[category])
            self.refined_rules[category] = [r for r in self.refined_rules[category] if r[0] != pattern]
            
            # If a rule was removed, save changes
            if len(self.refined_rules[category]) < original_len:
                if (category, pattern) in self.rule_weights:
                    del self.rule_weights[(category, pattern)]
                self.save_rules()
                return True
        return False
    
    def apply_rules(self, text, categories=None):
        """
        Apply refined phonetic rules to text
        
        Args:
            text: Input text to process
            categories: List of rule categories to apply (None for all)
            
        Returns:
            Processed text with phonetic rules applied
        """
        result = text
        
        # Get categories to apply
        if categories is None:
            categories = self.refined_rules.keys()
        
        # Apply rules from each category
        for category in categories:
            if category in self.refined_rules:
                for pattern, replacement in sorted(
                    self.refined_rules[category],
                    key=lambda x: self.rule_weights.get((category, x[0]), 0.0),
                    reverse=True
                ):
                    # Apply the rule and track usage
                    prev_result = result
                    result = re.sub(pattern, replacement, result)
                    
                    # Update statistics if rule was applied
                    if prev_result != result:
                        self.rule_stats[(category, pattern)] += 1
        
        return result
    
    def refine_rules_from_examples(self, examples, update_weights=True):
        """
        Refine rules based on example pairs (input, expected output)
        
        Args:
            examples: List of (input, expected_output) pairs
            update_weights: Whether to update rule weights based on examples
            
        Returns:
            Number of rules updated/refined
        """
        if not examples:
            return 0
        
        updated_rules = 0
        rule_effectiveness = defaultdict(lambda: {'correct': 0, 'total': 0})
        
        # Process each example
        for input_text, expected_output in examples:
            # Try applying each rule category separately to measure effectiveness
            for category in self.refined_rules:
                # Apply only this category's rules
                result = self.apply_rules(input_text, [category])
                
                # Check if the result matches the expected output
                if result == expected_output:
                    # This rule category was effective
                    for rule in self.refined_rules[category]:
                        rule_id = (category, rule[0])
                        rule_effectiveness[rule_id]['correct'] += 1
                        rule_effectiveness[rule_id]['total'] += 1
                else:
                    # This rule category was not fully effective
                    for rule in self.refined_rules[category]:
                        rule_id = (category, rule[0])
                        rule_effectiveness[rule_id]['total'] += 1
        
        # Update rule weights based on effectiveness
        if update_weights:
            for rule_id, stats in rule_effectiveness.items():
                if stats['total'] > 0:
                    effectiveness = stats['correct'] / stats['total']
                    # Update rule weight using exponential moving average
                    current_weight = self.rule_weights.get(rule_id, 1.0)
                    self.rule_weights[rule_id] = 0.7 * current_weight + 0.3 * effectiveness
                    updated_rules += 1
        
        # Try to derive new rules from examples
        new_rules = self.derive_rules_from_examples(examples)
        updated_rules += len(new_rules)
        
        # Save updated rules and weights
        if updated_rules > 0:
            self.save_rules()
        
        return updated_rules
    
    def derive_rules_from_examples(self, examples):
        """
        Try to derive new phonetic rules from examples
        
        Args:
            examples: List of (input, expected_output) pairs
            
        Returns:
            List of newly derived rules as (category, pattern, replacement) tuples
        """
        new_rules = []
        
        for input_text, expected_output in examples:
            # Skip examples that already match with current rules
            result = self.apply_rules(input_text)
            if result == expected_output:
                continue
            
            # Look for consistent differences between input and expected output
            if len(input_text) == len(expected_output):
                # Character-by-character analysis for same length strings
                for i in range(len(input_text)):
                    if input_text[i] != expected_output[i]:
                        # Found a difference - look for patterns
                        context_size = 2  # chars before/after
                        
                        # Extract context around the difference
                        start = max(0, i - context_size)
                        end = min(len(input_text), i + context_size + 1)
                        
                        pattern_text = input_text[start:end]
                        replacement_text = expected_output[start:end]
                        
                        # Determine rule category
                        if input_text[i].lower() in 'aeiou' and expected_output[i].lower() in 'aeiou':
                            category = 'vowel_rules'
                        elif input_text[i].lower() in 'bcdfghjklmnpqrstvwxyz' and expected_output[i].lower() in 'bcdfghjklmnpqrstvwxyz':
                            category = 'consonant_clusters'
                        else:
                            # Skip if not clearly vowel or consonant
                            continue
                        
                        # Create candidate rule
                        pattern = re.escape(pattern_text)
                        
                        # Don't create overly specific rules
                        if len(pattern) <= 3:
                            continue
                        
                        self.add_rule(category, pattern, replacement_text, weight=0.5)
                        new_rules.append((category, pattern, replacement_text))
            else:
                # For different length strings, look for common substrings
                # This is more complex and would require sophisticated diff algorithms
                # For now, we'll skip these cases
                pass
        
        return new_rules
    
    def get_rule_stats(self):
        """Get statistics about rule usage"""
        stats = {}
        for (category, pattern), count in self.rule_stats.items():
            if category not in stats:
                stats[category] = []
            
            # Find the replacement for this pattern
            replacement = None
            for rule in self.refined_rules.get(category, []):
                if rule[0] == pattern:
                    replacement = rule[1]
                    break
            
            if replacement:
                weight = self.rule_weights.get((category, pattern), 1.0)
                stats[category].append({
                    'pattern': pattern,
                    'replacement': replacement,
                    'usage_count': count,
                    'weight': weight
                })
        
        return stats


def apply_refined_phonetic_rules(text, language='hindi'):
    """
    Apply refined phonetic rules to text
    
    Args:
        text: Input text to process
        language: 'hindi' or 'marathi'
        
    Returns:
        Processed text with phonetic rules applied
    """
    refiner = PhoneticRuleRefiner(language)
    return refiner.apply_rules(text)

def refine_rules_from_corpus(input_texts, expected_outputs, language='hindi'):
    """
    Refine rules based on a corpus of examples
    
    Args:
        input_texts: List of input texts
        expected_outputs: List of expected outputs
        language: 'hindi' or 'marathi'
        
    Returns:
        Number of rules updated/refined
    """
    refiner = PhoneticRuleRefiner(language)
    examples = list(zip(input_texts, expected_outputs))
    return refiner.refine_rules_from_examples(examples)
