"""
Context-aware transliteration utilities
This module enhances transliteration by considering surrounding context
"""

import re
from .exceptions import get_exception, get_named_entity

# Rules for context-aware transliteration
CONTEXT_RULES = [
    # Rule format: (pattern, replacement_func)
    # Each rule consists of a regex pattern and a function to handle the replacement
    
    # Rule for handling words followed by numbers (like dates)
    (r'(\b[^\s]+)(\s+\d+\b)', lambda match, text, lang: 
        handle_word_with_number(match.group(1), match.group(2), lang)),
    
    # Rule for handling honorifics (श्री, डॉ, etc.)
    (r'(श्री|डॉ|श्रीमती|पंडित|प्रो)\.?\s+([^\s]+)', lambda match, text, lang: 
        handle_honorific(match.group(1), match.group(2), lang)),
    
    # Rule for handling compound words
    (r'([^\s]+)-([^\s]+)', lambda match, text, lang:
        handle_compound_words(match.group(1), match.group(2), lang)),
]

# Context disambiguation mappings
CONTEXT_DISAMBIGUATIONS = {
    # Words that need different transliterations based on surrounding context
    'कल': {
        'default': 'kal',
        'past': 'kal',     # yesterday
        'future': 'kal',   # tomorrow
        # The context detection will determine if it refers to past or future
    },
    'और': {
        'default': 'aur',
        'conjunction': 'aur',  # and
        'more': 'aur',         # more
    },
    'पर': {
        'default': 'par', 
        'on': 'par',           # on
        'but': 'par',          # but
    },
}

def handle_word_with_number(word, number, language='hindi'):
    """Special handling for words followed by numbers"""
    # For dates, cardinal/ordinal numbers, etc.
    from .transliterate import transliterate_text
    
    # Custom handling
    translit_word = transliterate_text(word, language)
    
    # Keep the number as is
    return translit_word + number

def handle_honorific(honorific, name, language='hindi'):
    """Special handling for honorifics followed by names"""
    from .transliterate import transliterate_text
    
    # Transliterate the honorific
    honorific_map = {
        'श्री': 'Shri',
        'डॉ': 'Dr',
        'श्रीमती': 'Smt',
        'पंडित': 'Pt',
        'प्रो': 'Prof'
    }
    
    # Use the mapping if available, otherwise transliterate
    h_translit = honorific_map.get(honorific, transliterate_text(honorific, language))
    
    # Always capitalize the name following an honorific
    name_translit = transliterate_text(name, language)
    if name_translit and name_translit[0].islower():
        name_translit = name_translit[0].upper() + name_translit[1:]
    
    return f"{h_translit} {name_translit}"

def handle_compound_words(word1, word2, language='hindi'):
    """Special handling for compound words joined by hyphen"""
    from .transliterate import transliterate_text
    
    # Transliterate each part separately
    part1 = transliterate_text(word1, language)
    part2 = transliterate_text(word2, language)
    
    # Join with hyphen
    return f"{part1}-{part2}"

def detect_word_context(word, prev_word=None, next_word=None, full_text=None, language='hindi'):
    """Detect the context of a word based on surrounding words"""
    # Default context
    context = 'default'
    
    # Specific word context detection
    if word == 'कल':
        # Time indicators
        past_indicators = ['गया', 'था', 'थी', 'गये', 'गयी', 'बीता', 'पिछला']
        future_indicators = ['आएगा', 'होगा', 'होगी', 'आने वाला', 'अगला']
        
        # Check surrounding words for tense indicators
        if prev_word in past_indicators or next_word in past_indicators:
            context = 'past'
        elif prev_word in future_indicators or next_word in future_indicators:
            context = 'future'
        elif full_text:
            # Look for tense indicators in the full text
            if any(indicator in full_text for indicator in past_indicators):
                context = 'past'
            elif any(indicator in full_text for indicator in future_indicators):
                context = 'future'
    
    # Add more word-specific context detection rules here
    
    return context

def apply_context_aware_transliteration(text, transliterated_text, language='hindi'):
    """Apply context-aware fixes to the transliterated text"""
    # First apply general rules
    for pattern, replacement_func in CONTEXT_RULES:
        def replace_match(match):
            return replacement_func(match, text, language)
        
        transliterated_text = re.sub(pattern, replace_match, transliterated_text)
    
    # Apply word-by-word context disambiguation
    words = text.split()
    transliterated_words = transliterated_text.split()
    
    # Ensure we have the same number of words (a basic validation)
    if len(words) == len(transliterated_words):
        for i, (orig_word, trans_word) in enumerate(zip(words, transliterated_words)):
            # Check if this word needs context disambiguation
            if orig_word in CONTEXT_DISAMBIGUATIONS:
                prev_word = words[i-1] if i > 0 else None
                next_word = words[i+1] if i < len(words)-1 else None
                
                # Detect context
                context = detect_word_context(orig_word, prev_word, next_word, text, language)
                
                # Apply context-specific transliteration
                context_map = CONTEXT_DISAMBIGUATIONS[orig_word]
                if context in context_map:
                    transliterated_words[i] = context_map[context]
        
        # Reconstruct the text
        transliterated_text = ' '.join(transliterated_words)
    
    return transliterated_text
