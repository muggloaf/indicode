# INDICODE - Hindi/Marathi to English Transliteration

A sophisticated web application that transliterates Hindi and Marathi text to English, maintaining phonetic accuracy with advanced linguistic features.

## Features

- **Accurate Transliteration**: Convert Hindi and Marathi text to English while preserving pronunciation
- **Context-aware Processing**: Analyzes surrounding words for improved accuracy
- **Statistical Schwa Deletion**: Intelligently handles inherent vowels using linguistic rules
- **Auto-Capitalization**: Properly capitalizes sentences, names, and titles
- **Machine Learning**: Learns from user corrections to improve over time
- **Document Processing**: Process .txt, .docx, and .pdf files
- **User Accounts**: Save transliteration history and access advanced features
- **Responsive Design**: Works on desktop and mobile devices

## Project Structure

```
app.py                  # Main Flask application file
requirements.txt        # Python dependencies
custom_indicate/        # Custom transliteration engine
    __init__.py         # Package initialization
    transliterate.py    # Basic character mappings
    enhanced_transliteration.py  # Advanced transliteration features
    schwa_deletion.py   # Inherent vowel handling
    context_aware.py    # Context-aware processing
    exception_detection.py  # Exception handling
    auto_capitalization.py  # Capitalization rules
database/               # SQLite database directory
    transliterate.db    # User data and history
static/                 # Static assets
    css/                # Stylesheets
    js/                 # JavaScript files
    favicon.ico         # Site favicon
templates/              # HTML templates
    base.html           # Base template
    index.html          # Home page
    dashboard.html      # User dashboard
    history.html        # Transliteration history
    login.html          # Login page
    register.html       # Registration page
    settings.html       # User settings
```

## Technology Stack

- **Backend**: Python, Flask
- **Frontend**: HTML, CSS, JavaScript, Bootstrap 5
- **Database**: SQLite with SQLAlchemy ORM
- **Authentication**: Flask-Login
- **NLP**: Custom transliteration algorithms with ML capabilities
- **Document Processing**: python-docx, PyPDF2

## Setup and Installation

1. Clone the repository
2. Create a virtual environment:
   ```
   python -m venv venv
   venv\Scripts\activate  # On Windows
   source venv/bin/activate  # On Mac/Linux
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Run the application:
   ```
   python app.py
   ```
5. Access the application at http://127.0.0.1:5000

## Transliteration Features

The application uses several advanced techniques for accurate transliteration:

1. **Character Mapping**: Basic conversion of Devanagari characters to Roman alphabet
2. **Schwa Deletion**: Handling of inherent vowels based on linguistic rules
3. **Context-aware Processing**: Analyzing surrounding words for better accuracy
4. **Exception Handling**: Detecting known exceptions and special cases
5. **Auto-capitalization**: Properly capitalizing proper nouns, sentence beginnings
6. **User Feedback Loop**: Learning from user corrections to improve over time

## Contributing

Contributions to improve the transliteration engine or add new features are welcome. Please follow these steps:

1. Fork the repository
2. Create a new branch
3. Make your changes
4. Submit a pull request

## License

[Include your license information here]

## Authors

[Your names and contact information]
