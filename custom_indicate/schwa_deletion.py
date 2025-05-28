"""
Statistical Schwa Deletion Module
================================

This module implements a sophisticated approach to inherent vowel (schwa) deletion
in Hindi and Marathi transliteration.

The 'schwa' is the inherent 'a' vowel in Devanagari script that is often deleted
in natural pronunciation but exists in the written form. For example:

- कमल (kamal) is pronounced as "kamal" (both 'a' vowels are pronounced)
- नमक (namak) is pronounced as "namak" (both 'a' vowels are pronounced)
- बचपन (bachapan) is pronounced as "bachpan" (middle 'a' is deleted)

Correctly handling schwa deletion is critical for natural-sounding transliteration.
This module uses statistical patterns and machine learning to determine when to
delete these inherent vowels, based on:
- Word position (beginning, middle, end)
- Surrounding consonants and vowels
- Word length and syllable structure
- Known exceptions and special cases
"""
import re

#---------------------------------------------------------------
# SCHWA DELETION PATTERN DEFINITIONS
#---------------------------------------------------------------

# Statistical patterns for schwa deletion based on linguistic rules
# These patterns are applied in sequence to determine which schwas to delete
SCHWA_DELETION_PATTERNS = [
    # Pattern format: (regex_pattern, replacement_pattern)
    # Each pattern implements a specific linguistic rule for schwa deletion
    
    # 1. Word-final schwa deletion 
    # Example: राम (rāma) → ram (final 'a' is deleted)
    # Note: Excludes nukta combinations (dh, z, f, q) which have special handling
    (r'(?<!d)(?<!z)(?<!f)(?<!q)([kgcjtdnpbmyrlvsh])a$', r'\1'),
    
    # 2. Schwa deletion in consonant clusters with specific endings
    # Example: कमल (kamala) → kamal (final schwa deleted but not medial)
    # Excludes nukta combinations which have different phonetics
    (r'(?<!d)(?<!z)(?<!f)(?<!q)([kgcjtdnpbmyrlvsh])a([kgcjtdnpbmyrlvsh])a$', r'\1\2'),
    
    # 3. Schwa retention in certain syllable structures
    # This ensures we don't delete schwas that should be pronounced
    # Example: प्रकाश (prakāśa) → prakash (retained for phonetic clarity)
    (r'([kgcjtdnpbmyrlvshz])a([kgcjtdnpbmyrlvshz]{2})a$', r'\1a\2'),
    
    # 4. Common word endings with predictable patterns
    # Example: आसमान (āsamāna) → asmaan (delete in specific endings)
    (r'([kgcjtdnpbmyrlvshz])a([mn])a$', r'\1\2'),
    
    # 5. Special case for -aya endings - REMOVED due to issues
    # Was causing incorrect transliterations like गया → gay instead of gaya
    # (r'aya$', r'ay'),
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

def has_explicit_vowels(original_word):
    """
    Check if the original Devanagari word has explicit vowel marks (matras)
    If it has matras, schwa deletion should be much more conservative
    """
    if not original_word:
        return False
    
    # All Devanagari matras (vowel marks)
    matras = ['ा', 'ि', 'ी', 'ु', 'ू', 'े', 'ै', 'ो', 'ौ', 'ं', 'ः']
    
    # Check if word contains any matras
    return any(matra in original_word for matra in matras)

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
        
        # Check if the original word has explicit vowels (matras)
        if has_explicit_vowels(original_word):
            # If word has matras, be very conservative with schwa deletion
            # Only remove final 'a' if it's clearly a schwa (no matra at end)
            
            # Check if the last character in original word is a consonant without matra
            last_char = original_word[-1]
            
            # Devanagari consonants without matras (these can have schwa deletion)
            devanagari_consonants = [
                'क', 'ख', 'ग', 'घ', 'ङ',
                'च', 'छ', 'ज', 'झ', 'ञ', 
                'ट', 'ठ', 'ड', 'ढ', 'ण',
                'त', 'थ', 'द', 'ध', 'न',
                'प', 'फ', 'ब', 'भ', 'म',
                'य', 'र', 'ल', 'व',
                'श', 'ष', 'स', 'ह',
                # Nukta consonants
                'ड़', 'ढ़', 'क़', 'ख़', 'ग़', 'ज़', 'फ़'
            ]
            
            # Only apply very conservative schwa deletion
            if (last_char in devanagari_consonants and 
                transliterated_word.endswith('a')):
                # Remove only final 'a' and only if it's clearly a schwa
                return transliterated_word[:-1]
            else:
                # Don't apply any schwa deletion - word has explicit vowels
                return transliterated_word
    
    # Apply the statistical patterns only for words without explicit matras
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
