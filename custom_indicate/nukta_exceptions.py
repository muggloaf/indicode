import json
import os

def load_nukta_exceptions():
    """Load nukta exceptions from JSON file"""
    current_dir = os.path.dirname(__file__)
    json_path = os.path.join(os.path.dirname(current_dir), 'nukta_exceptions.json')
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Warning: nukta_exceptions.json not found at {json_path}")
        return {}
    except json.JSONDecodeError:
        print("Warning: Error parsing nukta_exceptions.json")
        return {}

def check_nukta_exceptions(text):
    """Check if the input text is in nukta exceptions and return the transliteration"""
    exceptions = load_nukta_exceptions()
    
    # Check all categories of nukta words
    for category, words in exceptions.items():
        if text in words:
            return words[text]
    
    return None

def has_nukta_characters(text):
    """
    Check if text contains nukta characters or represents a nukta word
    
    Args:
        text: Text to check for nukta characters
        
    Returns:
        True if the text contains nukta characters or likely represents a nukta word
    """
    # These are the standard nukta characters in Devanagari
    nukta_chars = ['ड़', 'ढ़', 'क़', 'ख़', 'ग़', 'ज़', 'फ़']
    
    # First check actual nukta characters in the text
    if any(char in text for char in nukta_chars):
        return True
    
    # Check for clues that this might be a transliterated nukta word
    # Words starting with z, q, f are almost always from nukta characters
    if text and len(text) > 0 and text[0] in 'zqf':
        return True
    
    # Check for other nukta transliteration patterns
    if 'gh' in text or 'kh' in text or 'zh' in text:
        return True
        
    return False
