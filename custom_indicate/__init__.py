"""
Custom Indicate - Hindi/Marathi to English Transliteration
An enhanced implementation with context-aware processing, 
statistical schwa deletion, automatic exception detection,
and auto-capitalization.
"""

# Basic transliteration
from .transliterate import hindi2english, marathi2english

# Enhanced transliteration with all improvements
from .enhanced_transliteration import (
    EnhancedTransliterator, 
    enhanced_hindi2english, 
    enhanced_marathi2english
)

# Individual components if needed separately
from .context_aware import apply_context_aware_transliteration
from .schwa_deletion import apply_schwa_rules
from .exception_detection import identify_exceptions, learn_from_corrections
from .auto_capitalization import capitalize_text

__version__ = '0.2.0'