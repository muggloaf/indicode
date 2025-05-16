"""
Integrated transliteration engine combining all enhanced features.
This module serves as the main entry point for the enhanced transliteration system.
"""

import re
from .transliterate import hindi2english, marathi2english, preprocess_text, postprocess_text
from .context_aware import apply_context_aware_transliteration
from .schwa_deletion import apply_schwa_rules
from .exception_detection import ExceptionDetector
from .auto_capitalization import capitalize_text
from .exceptions import get_exception, get_named_entity, is_schwa_exception

class EnhancedTransliterator:
    """
    Enhanced transliteration engine that combines all the advanced features.
    """
    def __init__(self, language='hindi'):
        """
        Initialize the enhanced transliterator
        
        Args:
            language: 'hindi' or 'marathi'
        """
        self.language = language
        self.exception_detector = ExceptionDetector(language)
          # Feature flags to enable/disable specific enhancements
        self.enable_context_aware = True
        self.enable_statistical_schwa = True
        self.enable_auto_exceptions = True
        self.enable_phonetic_refinement = False  # Phonetic refinement disabled
        self.enable_auto_capitalization = True
    
    def transliterate(self, text, enable_features=None):
        """
        Perform enhanced transliteration with all active features
        
        Args:
            text: Input text in Hindi/Marathi
            enable_features: Dict of feature flags to override defaults
                            {'context_aware': True/False, 
                             'statistical_schwa': True/False,
                             'auto_exceptions': True/False,
                             'phonetic_refinement': True/False}
        
        Returns:
            Transliterated text with all enhancements applied
        """
        if not text:
            return ""
        # Set feature flags
        if enable_features is not None:
            context_aware = enable_features.get('context_aware', self.enable_context_aware)
            statistical_schwa = enable_features.get('statistical_schwa', self.enable_statistical_schwa)
            auto_exceptions = enable_features.get('auto_exceptions', self.enable_auto_exceptions)
            phonetic_refinement = enable_features.get('phonetic_refinement', self.enable_phonetic_refinement)
            auto_capitalization = enable_features.get('auto_capitalization', self.enable_auto_capitalization)
        else:
            context_aware = self.enable_context_aware
            statistical_schwa = self.enable_statistical_schwa
            auto_exceptions = self.enable_auto_exceptions
            phonetic_refinement = self.enable_phonetic_refinement
            auto_capitalization = self.enable_auto_capitalization
        
        # Preprocess input text
        text = preprocess_text(text)
        
        # Split into words for word-level processing
        words = text.split()
        transliterated_words = []
        
        # Process each word
        for word in words:
            # Step 1: Check for known exceptions first
            exception = get_exception(word, self.language) if auto_exceptions else None
            
            if exception:
                transliterated_words.append(exception)
                continue
            
            # Step 2: Check for named entities
            named_entity = get_named_entity(word) if auto_exceptions else None
            
            if named_entity:
                transliterated_words.append(named_entity)
                continue
            
            # Step 3: Check for automatically detected exceptions
            auto_exception = self.exception_detector.get_exception(word) if auto_exceptions else None
            
            if auto_exception:
                transliterated_words.append(auto_exception)
                continue
            
            # Step 4: Basic transliteration
            if self.language == 'hindi':
                transliterated = hindi2english(word)
            else:  # marathi
                transliterated = marathi2english(word)
            # Step 5: Apply statistical schwa deletion if enabled
            if statistical_schwa:
                transliterated = apply_schwa_rules(transliterated, word)
            
            # Phonetic refinement step removed
            
            transliterated_words.append(transliterated)
        # Join words back into text
        transliterated_text = ' '.join(transliterated_words)
        
        # Apply context-aware fixes if enabled
        if context_aware:
            transliterated_text = apply_context_aware_transliteration(text, transliterated_text, self.language)
        
        # Final postprocessing
        transliterated_text = postprocess_text(transliterated_text)          # Apply auto-capitalization if enabled
        if auto_capitalization:
            # Detect if this might be a title (short text, no sentence endings)
            is_title = len(transliterated_text) < 100 and not any(char in transliterated_text for char in '.!?')
            transliterated_text = capitalize_text(transliterated_text, self.language, is_title)
        
        # Always ensure the first letter is capitalized, even when auto-capitalization is disabled
        if transliterated_text and len(transliterated_text) > 0:
            # Find the first letter (skipping any leading spaces or punctuation)
            match = re.search(r'[a-z]', transliterated_text, re.IGNORECASE)
            if match:
                index = match.start()
                transliterated_text = transliterated_text[:index] + transliterated_text[index].upper() + transliterated_text[index+1:]
        
        return transliterated_text
    
    def learn_from_correction(self, original_text, auto_transliteration, corrected_transliteration):
        """
        Learn from manual corrections to improve future transliterations
        
        Args:
            original_text: Original Hindi/Marathi text
            auto_transliteration: Automatic transliteration produced by the system
            corrected_transliteration: Manually corrected transliteration
            
        Returns:
            Number of improvements learned
        """
        improvements = 0
        # Learn exceptions
        if self.enable_auto_exceptions:
            exceptions = self.exception_detector.analyze_transliteration(
                original_text, auto_transliteration, corrected_transliteration)
            improvements += len(exceptions)
            
            # Phonetic rule refinement removed
            
        return improvements
        
        def set_feature_flags(self, context_aware=None, statistical_schwa=None, 
                              auto_exceptions=None, phonetic_refinement=None, auto_capitalization=None):
            """Set feature flags to enable/disable specific enhancements"""
            if context_aware is not None:
                self.enable_context_aware = context_aware
            if statistical_schwa is not None:
                self.enable_statistical_schwa = statistical_schwa
            if auto_exceptions is not None:
                self.enable_auto_exceptions = auto_exceptions
            # Phonetic refinement parameter ignored as feature is removed
            if auto_capitalization is not None:
                self.enable_auto_capitalization = auto_capitalization

# Convenience functions

def enhanced_hindi2english(text, features=None):
    """
    Enhanced Hindi to English transliteration with all improvements
    
    Args:
        text: Input Hindi text
        features: Dict of feature flags to enable/disable specific enhancements
    
    Returns:
        Enhanced transliteration
    """
    transliterator = EnhancedTransliterator('hindi')
    return transliterator.transliterate(text, features)

def enhanced_marathi2english(text, features=None):
    """
    Enhanced Marathi to English transliteration with all improvements
    
    Args:
        text: Input Marathi text
        features: Dict of feature flags to enable/disable specific enhancements
    
    Returns:
        Enhanced transliteration
    """
    transliterator = EnhancedTransliterator('marathi')
    return transliterator.transliterate(text, features)
