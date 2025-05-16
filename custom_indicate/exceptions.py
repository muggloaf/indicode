"""
Word-level exceptions database for Hindi/Marathi transliteration.
This module contains exceptions and special cases that the general rules may not handle properly.
"""

# Words that need custom transliteration due to non-standard pronunciation
HINDI_EXCEPTIONS = {
    'अच्छा': 'accha',       # Instead of achchha
    'बच्चा': 'baccha',       # Instead of bachchha
    'कम्प्यूटर': 'computer',  # Instead of kampyootar
    'इंटरनेट': 'internet',    # Instead of intaranet
    'टेलीविजन': 'television', # Instead of teleevijon
    'रिक्शा': 'rickshaw',     # Instead of riksha
    'बैंक': 'bank',          # Instead of baink
    'स्कूल': 'school',       # Instead of skool
    'राष्ट्र': 'rashtra',     # Instead of raashtra
    'विश्व': 'vishwa',       # Instead of vishva
    'दृष्टि': 'drishti',     # Instead of drshti
    'शिक्षा': 'shiksha',     # Instead of shikshaa
    'कार्य': 'karya',        # Instead of kaary
    'सूर्य': 'surya',        # Instead of soorya
    'पत्नी': 'patni',        # Instead of patnee
    'मित्र': 'mitra',        # Instead of mitr
    'क्या': 'kya',          # Instead of kyaa
    'पूर्ण': 'poorna',       # Instead of poorn
    'कृपया': 'kripaya',      # Instead of krpaya
    'धन्यवाद': 'dhanyavaad', # Instead of dhanyavaada
    'कृष्ण': 'krishna',      # Instead of krshna
    'सरकार': 'sarkar',       # Instead of sarakaar
    'क्रिकेट': 'cricket',     # Instead of kriket
    'फ्रिज': 'fridge',        # Instead of frij
    'वॉटर': 'water',         # Instead of wotar
    'कॉफी': 'coffee',        # Instead of kofi
    'में': 'mein',          # Instead of me
    'है': 'hain',           # Instead of hai
    'कितना' : 'kitna',        # Instead of kitanaa
    'कितनी' : 'kitni',        # Instead of kitanee
    'कितने' : 'kitne',        # Instead of kitane
    'किसने' : 'kisne',        # Instead of kisane
    'किसका' : 'kiska',        # Instead of kisake
    'किसकी' : 'kiski',        # Instead of kisakee
    'किसके' : 'kiske',        # Instead of kisake
    # Add more exceptions as needed
}

MARATHI_EXCEPTIONS = {
    # Inherit Hindi exceptions
    **HINDI_EXCEPTIONS,
    
    # Marathi specific exceptions
    'वाट': 'vaat',           # Instead of vat
    'बोलतो': 'bolto',        # Instead of bolato
    'त्याला': 'tyala',        # Instead of tyaalaa
    'काय': 'kay',            # Instead of kaay
    'मराठी': 'marathi',      # Instead of maraathee
    'महाराष्ट्र': 'maharashtra', # Instead of mahaaraashtra
    # Add more exceptions as needed
}

# Special case handling for words with inherent vowels that need special treatment
SCHWA_EXCEPTIONS = [
    'राम', 'श्याम', 'कृष्ण', 'विष्णु', 'महेश', 'सूरज', 'चंद्र', 'सोम'
]

# Named entities that need proper capitalization
NAMED_ENTITIES = {
    'भारत': 'Bharat',       # India
    'हिन्दी': 'Hindi',       # Hindi language
    'मराठी': 'Marathi',      # Marathi language
    'मुंबई': 'Mumbai',       # Mumbai city
    'दिल्ली': 'Delhi',       # Delhi city
    'गंगा': 'Ganga',        # Ganges river
    'हिमालय': 'Himalaya',    # Himalaya mountains
    'रामायण': 'Ramayana',    # Ramayana epic
    'महाभारत': 'Mahabharata', # Mahabharata epic
    # Add more named entities as needed
}

def get_exception(word, language='hindi'):
    """Get the exception for a word if it exists"""
    exceptions = HINDI_EXCEPTIONS if language == 'hindi' else MARATHI_EXCEPTIONS
    return exceptions.get(word)

def get_named_entity(word):
    """Get the proper capitalized form for named entities"""
    return NAMED_ENTITIES.get(word)

def is_schwa_exception(word):
    """Check if a word has special schwa deletion rules"""
    return word in SCHWA_EXCEPTIONS
