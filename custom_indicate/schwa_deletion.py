"""
Statistical schwa deletion module
Implements a more sophisticated approach to inherent vowel deletion in Hindi/Marathi
"""

import re

# Statistical patterns for schwa deletion based on word endings and syllable structure
SCHWA_DELETION_PATTERNS = [
    # Pattern format: (regex, replacement)
    # These patterns implement common schwa deletion rules
    
    # 1. Word-final schwa deletion
    (r'([kgcjtdnpbmyrlvshz])a$', r'\1'),
    
    # 2. Schwa deletion in consonant clusters with specific endings
    (r'([kgcjtdnpbmyrlvshz])a([kgcjtdnpbmyrlvshz])a$', r'\1\2'),
    
    # 3. Schwa retention in certain syllable structures
    (r'([kgcjtdnpbmyrlvshz])a([kgcjtdnpbmyrlvshz]{2})a$', r'\1a\2'),
    
    # 4. Common word endings (-mana, -vana, etc.)
    (r'([kgcjtdnpbmyrlvshz])a([mn])a$', r'\1\2'),
    
    # 5. Special case for -aya endings
    (r'aya$', r'ay'),
]

# Syllable structure patterns for schwa deletion probability
# Format: (pattern, probability_delete)
SYLLABLE_PATTERNS = [
    # Two-syllable words
    (r'^C?V(C)$', 0.9),  # High probability of deletion in final position
    (r'^C?VC?V$', 0.2),  # Low probability in penultimate position of CVCV
    
    # Three syllable words - will simplify with C = consonant, V = vowel notation
    (r'^C?VC?VC?V$', [0.1, 0.8, 0.0]),  # Probability for each syllable
    (r'^C?VC?VCV$', [0.1, 0.9, 0.0]),  
]

# Exceptions table - words that don't follow regular schwa deletion rules
# These are in addition to the exceptions in exceptions.py
SCHWA_EXCEPTIONS_TABLE = {
    # Words where schwa is deleted in unexpected positions
    'abnormal_deletion': [
        'सहायता',  # sa-haa-ya-ta (not sa-haa-ya-ta-a)
        'अनुभव',   # a-nu-bhav (not a-nu-bha-va)
        'विशेषज्ञ', # vi-she-sha-gya (not vi-she-sha-gya-a)
    ],
    
    # Words where schwa is retained in unexpected positions
    'abnormal_retention': [
        'कमल',     # ka-ma-l (not ka-ml)
        'नमक',     # na-mak (not na-mk)
        'धरती',    # dha-ra-ti (not dhar-ti)
    ]
}

# Syllable weight table (for determining schwa deletion)
SYLLABLE_WEIGHTS = {
    # Format: syllable structure -> weight
    # Higher weight increases likelihood of schwa deletion
    'CV': 1,    # Light syllable (Consonant + Vowel)
    'CVC': 2,   # Heavy syllable (Consonant + Vowel + Consonant)
    'CVCC': 3,  # Extra heavy syllable
    'VC': 1.5,  # Vowel + Consonant
    'V': 0.5,   # Single vowel syllable
}

def syllabify(word):
    """
    Break a word into syllables to aid in schwa deletion decisions
    This is a simplified syllabification for Hindi/Marathi
    """
    syllables = []
    i = 0
    current_syllable = ""
    
    while i < len(word):
        # Start with a consonant or consonant cluster
        if is_consonant(word[i]):
            current_syllable += word[i]
            i += 1
            
            # Collect consonant cluster
            while i < len(word) and is_consonant(word[i]):
                current_syllable += word[i]
                i += 1
        
        # Add vowel (if present)
        if i < len(word) and is_vowel(word[i]):
            current_syllable += word[i]
            i += 1
            
            # Include vowel modifiers
            if i < len(word) and is_vowel_modifier(word[i]):
                current_syllable += word[i]
                i += 1
        
        # Save completed syllable
        if current_syllable:
            syllables.append(current_syllable)
            current_syllable = ""
    
    # Add any remaining characters
    if current_syllable:
        syllables.append(current_syllable)
    
    return syllables

def get_syllable_weight(syllable):
    """Calculate the weight of a syllable for schwa deletion determination"""
    # Simplified: Convert the syllable to a CV pattern
    cv_pattern = ""
    for char in syllable:
        if is_consonant(char):
            cv_pattern += 'C'
        elif is_vowel(char) or is_vowel_modifier(char):
            cv_pattern += 'V'
    
    # Look up the weight
    for pattern, weight in SYLLABLE_WEIGHTS.items():
        if cv_pattern == pattern:
            return weight
    
    # Default weight for unknown patterns
    return 1.0

def is_consonant(char):
    """Check if a character is a Devanagari consonant"""
    # Unicode range for Devanagari consonants
    return '\u0915' <= char <= '\u0939'

def is_vowel(char):
    """Check if a character is a Devanagari vowel"""
    # Unicode range for Devanagari vowels
    return '\u0904' <= char <= '\u0914' 

def is_vowel_modifier(char):
    """Check if a character is a Devanagari vowel modifier (matra)"""
    # Unicode range for Devanagari vowel signs (matras)
    return '\u093E' <= char <= '\u094C' or char == '\u0902' or char == '\u0903'

def calculate_schwa_deletion_probability(word, position):
    """
    Calculate the probability of schwa deletion at a specific position in a word
    This uses a combination of syllable structure, position, and learned patterns
    
    Args:
        word: The word being processed
        position: The position in the word to check for schwa deletion
    
    Returns:
        float: Probability between 0.0 (no deletion) and 1.0 (definite deletion)
    """
    syllables = syllabify(word)
    
    # Word-final position almost always deletes schwa
    if position == len(syllables) - 1:
        return 0.95
    
    # Default probabilities based on position
    position_prob = {
        0: 0.05,  # First syllable rarely deletes schwa
        -1: 0.95, # Last syllable almost always deletes schwa
        -2: 0.7,  # Second to last often deletes schwa in longer words
    }
    
    # Get probability for this position
    prob = position_prob.get(position, 0.5)
    
    # Adjust based on syllable weight
    weight = get_syllable_weight(syllables[position]) if position < len(syllables) else 1.0
    prob *= weight
    
    # Cap probability between 0 and 1
    return max(0, min(prob, 1))

def apply_statistical_schwa_deletion(transliterated_word, original_word=None):
    """
    Apply statistical schwa deletion rules to a transliterated word
    
    Args:
        transliterated_word: The word after basic transliteration
        original_word: The original Devanagari word (if available)
    
    Returns:
        str: Word with appropriate schwa deletion applied
    """
    # If the original word is in the exceptions list, use predefined treatment
    if original_word:
        if original_word in SCHWA_EXCEPTIONS_TABLE['abnormal_deletion']:
            # Apply aggressive schwa deletion
            return re.sub(r'a\b', '', transliterated_word)
        elif original_word in SCHWA_EXCEPTIONS_TABLE['abnormal_retention']:
            # Preserve schwas
            return transliterated_word
    
    # Apply the statistical patterns
    result = transliterated_word
    
    # Apply each pattern in order
    for pattern, replacement in SCHWA_DELETION_PATTERNS:
        result = re.sub(pattern, replacement, result)
    
    return result

def apply_schwa_rules(text, original_text=None):
    """
    Apply all schwa deletion rules to a transliterated text
    
    Args:
        text: Transliterated text
        original_text: Original Devanagari text (if available)
    
    Returns:
        str: Text with improved schwa deletion
    """
    words = text.split()
    original_words = original_text.split() if original_text else [None] * len(words)
    
    # Process each word
    for i, (word, original) in enumerate(zip(words, original_words)):
        words[i] = apply_statistical_schwa_deletion(word, original)
    
    return ' '.join(words)
