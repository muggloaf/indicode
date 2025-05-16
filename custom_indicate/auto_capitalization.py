"""
Auto-capitalization module for Hindi/Marathi to English transliteration.
This module handles proper capitalization of text based on language rules.
"""

import re
from typing import List, Dict, Set, Tuple, Optional
from .exceptions import NAMED_ENTITIES, get_named_entity

# Common English capitalization words (like months, days, languages, titles)
COMMON_CAPITALIZED_WORDS = {
    # Days of the week
    'sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday',
    
    # Months
    'january', 'february', 'march', 'april', 'may', 'june', 'july',
    'august', 'september', 'october', 'november', 'december',
    
    # Common titles
    'mr', 'mrs', 'ms', 'dr', 'prof', 'sir', 'madam', 'lord', 'lady',
    
    # Languages and nationalities
    'hindi', 'marathi', 'english', 'urdu', 'bengali', 'gujarati', 'punjabi', 
    'tamil', 'telugu', 'malayalam', 'kannada', 'indian', 'american', 'british'
}

# Words that should not be capitalized in titles
# (except at the beginning of the title)
LOWERCASE_IN_TITLES = {
    'a', 'an', 'the', 'and', 'but', 'or', 'for', 'nor', 'on', 'at', 'to', 'from', 
    'by', 'of', 'in', 'with', 'within', 'about', 'into', 'between'
}

# Regex patterns for sentence detection
SENTENCE_ENDINGS = r'[.!?][\s]+[\'"\)\]]*'
QUOTATION_START = r'[\s]*[\'"]'
ABBREVIATIONS = r'\b(?:[A-Z]\.){2,}|\b(?:[A-Z][a-z]*\.){1,}|[A-Z]\.'

class AutoCapitalizer:
    def __init__(self, language: str = 'hindi'):
        """
        Initialize the auto-capitalizer
        
        Args:
            language: The source language ('hindi' or 'marathi')
        """
        self.language = language
        self.named_entities_map = NAMED_ENTITIES
        self.common_capitalized = COMMON_CAPITALIZED_WORDS
        
        # Cache of words already processed
        self.capitalization_cache: Dict[str, str] = {}
    
    def add_capitalized_word(self, word: str) -> None:
        """Add a word to the common capitalized words list"""
        self.common_capitalized.add(word.lower())
    
    def add_named_entity(self, original: str, capitalized: str) -> None:
        """Add a named entity to the named entities map"""
        self.named_entities_map[original] = capitalized
    
    def capitalize_first_letter(self, text: str) -> str:
        """Capitalize just the first letter of a word"""
        if not text:
            return ""
        return text[0].upper() + text[1:]
    
    def is_common_capitalized(self, word: str) -> bool:
        """Check if a word is commonly capitalized"""
        return word.lower() in self.common_capitalized
    
    def apply_sentence_capitalization(self, text: str) -> str:
        """
        Capitalize the first letter of each sentence
        
        Args:
            text: The text to process
        
        Returns:
            Text with sentence beginnings capitalized
        """
        # Split by sentence endings but keep the delimiters
        parts = re.split(f'({SENTENCE_ENDINGS})', text)
        result = []
        
        for i, part in enumerate(parts):
            # If this is the first part or follows a sentence ending
            if i == 0 or (i > 0 and re.match(SENTENCE_ENDINGS, parts[i-1])):
                # Find the first word character and capitalize it
                match = re.search(r'[a-zA-Z]', part)
                if match:
                    index = match.start()
                    part = part[:index] + part[index].upper() + part[index+1:]
            
            result.append(part)
        
        return ''.join(result)
    
    def apply_title_case(self, text: str) -> str:
        """
        Apply title case to a text string
        
        Args:
            text: The text to process
        
        Returns:
            Text in title case
        """
        words = text.split()
        result = []
        
        for i, word in enumerate(words):
            # Always capitalize the first and last word
            if i == 0 or i == len(words) - 1:
                result.append(self.capitalize_first_letter(word))
            # Don't capitalize articles, conjunctions, prepositions unless they're 5+ letters
            elif word.lower() in LOWERCASE_IN_TITLES and len(word) < 5:
                result.append(word.lower())
            else:
                result.append(self.capitalize_first_letter(word))
        
        return ' '.join(result)
    
    def capitalize_named_entities(self, text: str) -> str:
        """
        Capitalize named entities in the text
        
        Args:
            text: The text to process
        
        Returns:
            Text with named entities capitalized
        """
        # Split text into words while keeping separators
        parts = re.split(r'(\W+)', text)
        result = []
        
        for part in parts:
            # Skip non-word parts
            if not part.strip() or not re.search(r'\w', part):
                result.append(part)
                continue
                
            # Check if this word is a known named entity in our database
            capitalized = get_named_entity(part)
            if capitalized:
                result.append(capitalized)
            else:
                # Only capitalize days, months, languages, and proper nouns, avoid over-capitalization
                if part.lower() in self.common_capitalized:
                    result.append(self.capitalize_first_letter(part.lower()))
                else:
                    # Preserve existing capitalization instead of forcing lowercase
                    result.append(part)
        
        return ''.join(result)
    
    def capitalize_proper_nouns(self, text: str) -> str:
        """
        Attempt to capitalize proper nouns based on context and rules
        
        Args:
            text: The text to process
        
        Returns:
            Text with proper nouns capitalized
        """
        # This is a simplified implementation
        # In a real-world scenario, this would use NLP for named entity recognition
        
        # Heuristics for proper noun detection
        # 1. Words following titles (Mr., Dr., etc.)
        text = re.sub(
            r'\b(Mr\.|Mrs\.|Ms\.|Dr\.|Prof\.)\s+([a-z])',
            lambda m: m.group(1) + ' ' + m.group(2).upper(),
            text,
            flags=re.IGNORECASE
        )
        
        # 2. Names of places (simplified approach)
        place_indicators = ['nagar', 'pur', 'garh', 'pattan', 'bad']
        for place in place_indicators:
            text = re.sub(
                fr'\b([a-z]+{place})\b',
                lambda m: self.capitalize_first_letter(m.group(1)),
                text,
                flags=re.IGNORECASE
            )
        
        # 3. Known proper nouns for Hindi/Marathi contexts
        # Common Indian proper names that should be capitalized
        indian_names = ['ram', 'shyam', 'krishna', 'radha', 'sita', 'lakshman', 
                       'bharat', 'shatrughan', 'hanuman', 'ravan', 'arjun', 
                       'bheem', 'yudhishthir', 'nakul', 'sahadev', 'dronacharya', 'soor']
        
        # Create a pattern to match these names
        name_pattern = '|'.join(fr'\b{name}\b' for name in indian_names)
        if name_pattern:
            text = re.sub(
                name_pattern,
                lambda m: self.capitalize_first_letter(m.group(0)),
                text,
                flags=re.IGNORECASE
            )
        
        return text
    
    def apply_auto_capitalization(self, text: str, is_title: bool = False) -> str:
        """
        Apply all capitalization rules to the text
        
        Args:
            text: The text to process
            is_title: Whether to treat the text as a title
        
        Returns:
            Properly capitalized text
        """
        # First convert all text to lowercase to start with a clean slate
        text = text.lower()
        
        # Ensure the very first letter is always capitalized, regardless of other rules
        if text and len(text) > 0:
            # Find the first letter (skipping any leading spaces or punctuation)
            match = re.search(r'[a-z]', text, re.IGNORECASE)
            if match:
                index = match.start()
                text = text[:index] + text[index].upper() + text[index+1:]
        
        # Apply sentence capitalization (first letter of each sentence)
        if not is_title:
            text = self.apply_sentence_capitalization(text)
        else:
            # Apply title case if requested
            text = self.apply_title_case(text)
        
        # Then apply named entity capitalization for specific terms
        text = self.capitalize_named_entities(text)
        
        # Finally apply proper noun capitalization for specific contexts
        text = self.capitalize_proper_nouns(text)
        
        return text


def capitalize_text(text: str, language: str = 'hindi', is_title: bool = False) -> str:
    """
    Apply automatic capitalization to transliterated text
    
    Args:
        text: The text to process
        language: Source language ('hindi' or 'marathi')
        is_title: Whether to treat the text as a title
        
    Returns:
        Properly capitalized text
    """
    # Don't process empty strings
    if not text:
        return ""
        
    capitalizer = AutoCapitalizer(language)
    return capitalizer.apply_auto_capitalization(text, is_title)
