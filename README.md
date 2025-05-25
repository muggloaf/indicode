# INDICODE - Hindi/Marathi to English Transliteration

A sophisticated web application that transliterates Hindi and Marathi text to English with high accuracy, maintaining phonetic precision through advanced linguistic algorithms, exhaustive phonetic mapping and user feedbacks.

## 🌟 Features

### Core Functionality
- **Accurate Transliteration**: Convert Hindi and Marathi text to English while preserving pronunciation
- **Multi-Language Support**: Currently supports Hindi and Marathi with plans for Bengali, Tamil, and more
- **Real-time Processing**: Instant transliteration as you type
- **Document Processing**: Upload and process `.txt`, `.docx`, and `.pdf` files (up to 2MB)

### Advanced Linguistic Features
- **Context-Aware Processing**: Analyzes surrounding words for improved accuracy
- **Statistical Schwa Deletion**: Intelligently handles inherent vowels using linguistic rules
- **Auto-Capitalization**: Properly capitalizes sentences, names, and titles
- **Exception Handling**: Built-in dictionary of exceptions and special cases
- **Adaptive Learning**: Learns from user corrections to improve over time

### User Experience
- **User Accounts**: Secure registration and login system
- **History Tracking**: Save and manage your transliteration history
- **CSV Export**: Export your transliteration history as CSV files
- - **Batch Processing**: Upload .txt, .docx and .pdf files to get a transliterated .txt
- **Preview Mode**: Preview document processing before download
- **Responsive Design**: Works seamlessly on desktop and mobile devices
- **Translation Support**: Basic Hindi/Marathi to English translation via Google Translate

## 📋 Prerequisites

- Python 3.8 or higher
- pip package manager
- Virtual environment (recommended)

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/indicode.git
   cd indicode
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Access the application**
   Open your browser and navigate to `http://127.0.0.1:5000`

## 📁 Project Structure

```
indicode/
├── app.py                      # Main Flask application
├── requirements.txt            # Python dependencies
├── README.md                   # Project documentation
├── hindi_exceptions.json       # Hindi language exceptions
├── marathi_exceptions.json     # Marathi language exceptions
├── nukta_exceptions.json       # Nukta character exceptions
├── custom_indicate/            # Custom transliteration engine
│   ├── __init__.py            # Package initialization
│   ├── transliterate.py       # Basic character mappings
│   ├── enhanced_transliteration.py  # Advanced features
│   ├── schwa_deletion.py      # Inherent vowel handling
│   ├── context_aware.py       # Context-aware processing
│   ├── exception_detection.py # Exception handling
│   ├── auto_capitalization.py # Capitalization rules
│   ├── exceptions.py          # Exception management
│   └── nukta_exceptions.py    # Nukta handling
├── database/                   # Database files
│   └── transliterate.db       # SQLite database
├── static/                     # Static assets
│   ├── css/                   # Stylesheets
│   ├── js/                    # JavaScript files
│   └── favicon.ico            # Site favicon
└── templates/                  # HTML templates
    ├── base.html              # Base template
    ├── index.html             # Home page
    ├── dashboard.html         # User dashboard
    ├── history.html           # Transliteration history
    ├── login.html             # Login page
    ├── register.html          # Registration page
    └── settings.html          # User settings
```

## 🔧 Technology Stack

- **Backend**: Python 3.10.9, Flask 2.0.1
- **Frontend**: HTML5, CSS3, JavaScript (ES6+), Bootstrap 5
- **Database**: SQLite with SQLAlchemy ORM
- **Authentication**: Flask-Login with session management
- **Document Processing**: python-docx, PyPDF2
- **Translation**: Google Translate API integration
- **Security**: Flask-Bcrypt for password hashing

## 🎯 Usage

### Basic Transliteration
1. Visit the homepage or dashboard
2. Select your input language (Hindi/Marathi)
3. Type or paste text in the input field
4. Click "Transliterate" to see the English output
5. Use "Copy" to copy results to clipboard

### Document Processing
1. Go to the Dashboard
2. Upload a file (TXT, DOCX, or PDF)
3. Select the input language
4. Preview the processing if desired
5. Download the transliterated document

### History Management
1. View your transliteration history
2. Export history as CSV
3. Reuse previous transliterations
4. Clear history when needed

## 🧠 Transliteration Algorithm

The application employs several sophisticated techniques:

1. **Character Mapping**: Direct conversion using comprehensive Devanagari-to-Roman mappings
2. **Schwa Deletion**: Statistical analysis for inherent vowel handling
3. **Context Analysis**: Surrounding word analysis for disambiguation
4. **Exception Detection**: Automatic recognition of known exceptions
5. **Phonetic Refinement**: Sound-based adjustments for better pronunciation
6. **Learning System**: Continuous improvement from user feedback

## 📊 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Home page |
| `/transliterate` | POST | Transliterate text |
| `/translate` | POST | Translate text |
| `/process_file` | POST | Process uploaded files |
| `/history` | GET | View transliteration history |
| `/export_history` | GET | Export history as CSV |
| `/feedback` | POST | Submit corrections/feedback |

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Development Guidelines
- Follow PEP 8 coding standards
- Add unit tests for new features
- Update documentation as needed
- Test on multiple browsers and devices

## 🐛 Bug Reports

Found a bug? Please open an issue with:
- Clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Screenshots if applicable
- Browser/OS information

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Authors

- **Alesha Mulla** - [muggloaf](https://github.com/muggloaf)
- **Ajinkya Ghule** - [GhuleAjikya](https://github.com/GhuleAjinkya)
- **Aliza Kundal**

## 🙏 Acknowledgments

- Inspiration from various transliteration libraries 
- Hindi/Marathi linguistic research papers
- Open source community for tools and libraries
- Beta testers and feedback providers

---

⭐ **Star this repository if you found it helpful!**
```

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/Flask-2.0+-green.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

