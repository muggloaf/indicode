"""
# Custom Indicate - Hindi/Marathi to English Transliteration
# =========================================================
#
# A sophisticated transliteration engine that converts Hindi and Marathi text 
# to English, maintaining phonetic accuracy with advanced linguistic features:
#
# Key Features:
# - Context-aware processing: Analyzes surrounding words for accurate transliteration
# - Statistical schwa deletion: Intelligently removes inherent vowels using statistical models
# - Automatic exception handling: Detects and handles special cases and known exceptions
# - Auto-capitalization: Properly capitalizes sentences, proper nouns, and titles
# - Machine learning capabilities: Learns from user corrections to improve over time
# - Support for multiple languages: Currently Hindi and Marathi, with more planned
"""

#---------------------------------------------------------------
# BASIC TRANSLITERATION (core character mapping functionality)
#---------------------------------------------------------------
from .transliterate import hindi2english, marathi2english

#---------------------------------------------------------------
# ENHANCED TRANSLITERATION (with all improvements and features)
#---------------------------------------------------------------
from .enhanced_transliteration import (
    EnhancedTransliterator,  # Main transliteration class
    enhanced_hindi2english,  # Function for Hindi transliteration
    enhanced_marathi2english  # Function for Marathi transliteration
)

#---------------------------------------------------------------
# INDIVIDUAL COMPONENTS (can be used separately if needed)
#---------------------------------------------------------------
from .context_aware import apply_context_aware_transliteration  # Contextual analysis
from .schwa_deletion import apply_schwa_rules  # Inherent vowel deletion rules
from .exception_detection import identify_exceptions, learn_from_corrections  # Exception handling
from .auto_capitalization import capitalize_text  # Smart capitalization features

__version__ = '0.2.0'