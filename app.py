###############################################################################
# INDICODE - Hindi/Marathi to English Transliteration Application
# 
# This Flask application provides a web interface for transliterating text from 
# Hindi and Marathi to English, with features for user accounts, history tracking,
# feedback collection, and document processing.
###############################################################################

# Core Flask and extension imports
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session, send_file
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_sqlalchemy import SQLAlchemy  # Database ORM
from flask_cors import CORS  # Cross-Origin Resource Sharing support
from werkzeug.security import generate_password_hash, check_password_hash  # Password handling
from werkzeug.utils import secure_filename  # Secure file uploads

# Document handling libraries
from reportlab.pdfgen import canvas  # PDF generation
from reportlab.lib.pagesizes import letter
from docx import Document  # Word document processing
from PyPDF2 import PdfReader  # PDF reading

# Standard library imports
from datetime import datetime
import os
import json
from io import BytesIO

# Custom transliteration engine imports
from custom_indicate import enhanced_hindi2english, enhanced_marathi2english  # Core transliteration functions
from custom_indicate.exception_detection import learn_from_corrections  # Feedback learning system
from googletrans import Translator  # For translation (as opposed to transliteration)

#---------------------------------------------------------------
# APPLICATION INITIALIZATION & CONFIGURATION
#---------------------------------------------------------------

# Initialize Flask application
app = Flask(__name__)

# Configure maximum file upload size (2MB) to prevent DoS attacks
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024

# Enable CORS (Cross-Origin Resource Sharing) with proper configuration for local development
# This allows API requests from the frontend when running in development mode
CORS(app, resources={
    r"/*": {
        "origins": ["http://127.0.0.1:5000", "http://localhost:5000"],  # Allowed origins
        "methods": ["GET", "POST", "OPTIONS"],  # Allowed HTTP methods
        "allow_headers": ["Content-Type", "Accept"],  # Allowed headers
        "supports_credentials": True,  # Allow cookies to be sent
        "expose_headers": ["Content-Disposition"]  # Allow frontend to read filename for downloads
    }
})

# Set cache control for file downloads - disable caching for development
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

# Application secret key used for sessions, CSRF protection, etc.
# SECURITY WARNING: Change this to a random value in production!
app.secret_key = 'your_super_secret_key_change_in_production'

# Ensure database directory exists - create if not present
db_path = os.path.join(os.path.dirname(__file__), 'database')
if not os.path.exists(db_path):
    os.makedirs(db_path)

# Configure SQLite database connection
db_file = os.path.join(db_path, 'transliterate.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_file}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Disable modification tracking to improve performance

# Initialize database
db = SQLAlchemy(app)
login_manager = LoginManager()
#---------------------------------------------------------------
# USER AUTHENTICATION & DATABASE MODELS
#---------------------------------------------------------------

# Initialize Flask-Login
login_manager.init_app(app)
login_manager.login_view = 'login'  # Redirect unauthorized users to login page

#---------------------------------------------------------------
# DATABASE MODELS
#---------------------------------------------------------------

class User(UserMixin, db.Model):
    """
    User model for authentication and account management.
    
    Attributes:
        id (int): Primary key for the user
        email (str): User's email address, must be unique
        password (str): Hashed password for security
        name (str): User's display name
        history (relationship): One-to-many relationship with TransliterationHistory
    """
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)  # Stores hashed passwords only
    name = db.Column(db.String(100))
    history = db.relationship('TransliterationHistory', backref='user', lazy=True)  # User's history entries


class TransliterationHistory(db.Model):
    """
    Model to store user's transliteration history.
    
    Attributes:
        id (int): Primary key
        user_id (int): Foreign key linking to User model
        input_text (text): Original text submitted for transliteration
        output_text (text): Resulting transliterated text
        language (str): Source language code ('hindi', 'marathi', etc.)
        created_at (datetime): Timestamp when the transliteration was performed
    """
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    input_text = db.Column(db.Text, nullable=False)
    output_text = db.Column(db.Text, nullable=False)
    language = db.Column(db.String(10), nullable=False)  # Language identifier (hindi, marathi)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # Automatically set to current time


@login_manager.user_loader
def load_user(user_id):
    """
    Flask-Login user loader function.
    Loads a user from the database based on their ID.
    
    Args:
        user_id (str): The user ID to load
        
    Returns:
        User: The user object or None if not found
    """
    return User.query.get(int(user_id))


# Create database tables if they don't exist
with app.app_context():
    db.create_all()

# Add datetime utility for templates
@app.context_processor
def utility_processor():
    def now():
        return datetime.utcnow()
    return dict(now=now)

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        name = request.form.get('name')
        
        # Check if email already exists
        user = User.query.filter_by(email=email).first()
        
        if user:
            flash('Email address already exists')
            return redirect(url_for('register'))
        
        # Create new user
        new_user = User(
            email=email,
            password=generate_password_hash(password, method='pbkdf2:sha256'),
            name=name
        )
        
        # Add user to database
        db.session.add(new_user)
        db.session.commit()
        
        flash('Account created successfully! Please login.')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Please check your login details and try again.')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    history = TransliterationHistory.query.filter_by(user_id=current_user.id).order_by(TransliterationHistory.created_at.desc()).limit(10).all()
    return render_template('dashboard.html', history=history)

#---------------------------------------------------------------
# TRANSLITERATION API ENDPOINTS
#---------------------------------------------------------------

@app.route('/transliterate', methods=['POST'])
def transliterate_text():
    """
    Main transliteration API endpoint.
    
    This function handles transliteration requests from the frontend,
    processes the input text using the appropriate transliteration function
    based on the selected language, and returns the transliterated text.
    
    Request parameters:
        - input_text: The text to be transliterated
        - language: The source language (hindi, marathi, english)
        - Various feature flags for customizing transliteration behavior
    
    Returns:
        JSON response with the transliterated output or error message
    """
    print("Received transliteration request")
    print(f"Form data: {request.form}")
    print(f"JSON data: {request.get_json(silent=True)}")
    print(f"Request headers: {request.headers}")
    
    # Try to get input text from different sources (form data, JSON, raw data)
    # This provides flexibility in how clients can send data to the API
    input_text = None
    if request.form:
        input_text = request.form.get('input_text', '')
    elif request.get_json(silent=True):
        input_text = request.get_json(silent=True).get('input_text', '')
    else:
        input_text = request.data.decode('utf-8').split('input_text=')[1].split('&')[0] if 'input_text=' in request.data.decode('utf-8') else ''
    
    print(f"Input text: {input_text}")
    language = request.form.get('language', 'hindi')  # Default to Hindi if not specified
    print(f"Language: {language}")
    
    # Get feature flags from form if available - these control transliteration behavior
    # Each flag enables or disables specific transliteration features
    features = {
        'context_aware': request.form.get('context_aware', 'true').lower() == 'true',  # Use context for better accuracy
        'statistical_schwa': request.form.get('statistical_schwa', 'true').lower() == 'true',  # Intelligent schwa deletion
        'auto_exceptions': request.form.get('auto_exceptions', 'true').lower() == 'true',  # Handle special cases
        'phonetic_refinement': request.form.get('phonetic_refinement', 'true').lower() == 'true',  # Improve phonetic clarity
        'auto_capitalization': request.form.get('auto_capitalization', 'true').lower() == 'true'  # Auto-capitalize proper nouns
    }
    try:
        # Select the appropriate transliteration function based on language
        if language == 'hindi':
            # Use our custom Hindi-to-English transliteration function
            output_text = enhanced_hindi2english(input_text, features)
        elif language == 'marathi':
            # Use our custom Marathi-to-English transliteration function
            output_text = enhanced_marathi2english(input_text, features)
        elif language == 'english':
            # For English input, no transliteration is needed
            output_text = input_text
        else:
            # Placeholder for future language support (Bengali, Tamil, etc.)
            output_text = "Unsupported language selection"
    except ValueError as e:
        # Handle specific validation errors from the transliteration engine
        return jsonify({'error': str(e), 'output': ''})
    except Exception as e:
        # Catch-all for any unexpected errors during processing
        return jsonify({'error': f"An unexpected error occurred: {str(e)}", 'output': ''})
    
    # Save to history if user is logged in
    # This allows users to access their past transliterations
    if current_user.is_authenticated:
        history = TransliterationHistory(
            user_id=current_user.id,
            input_text=input_text,
            output_text=output_text,
            language=language
        )
        db.session.add(history)
        db.session.commit()
    
    # Return the transliterated text as JSON
    return jsonify({'output': output_text})

#---------------------------------------------------------------
# BACKWARD COMPATIBILITY & LEGACY ROUTES
#---------------------------------------------------------------

# Legacy route for backwards compatibility with older frontend versions
@app.route('/indicate', methods=['POST'])
def indicate_text():
    """
    Legacy endpoint that redirects to the main transliteration handler.
    Kept for backward compatibility with older frontend code.
    """
    return transliterate_text()

#---------------------------------------------------------------
# DOCUMENT PROCESSING FUNCTIONALITY
#---------------------------------------------------------------

@app.route('/process_file', methods=['POST'])
def process_file():
    """
    Process uploaded document files for transliteration.
    
    This endpoint handles file uploads (.txt, .docx, .pdf) and extracts text content
    from these documents for transliteration. It can either return a preview of the
    transliterated content or create a new document with the transliteration results.
    
    Request parameters:
        - file: The uploaded file (must be .txt, .docx, or .pdf)
        - language: Source language for transliteration (hindi, marathi)
        - preview_only: If true, only returns a preview without creating a new document
    
    Returns:
        - Preview mode: JSON with transliterated content preview
        - Document mode: The newly created document file for download
    """
    try:
        # Validate that a file was actually uploaded
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        # Extract request parameters
        language = request.form.get('language', 'hindi')  # Default: Hindi
        preview_only = request.form.get('preview_only', 'false').lower() == 'true'  # Check if preview mode
        filename = secure_filename(file.filename.lower())  # Secure filename to prevent path traversal attacks
        
        # Validate supported file types (.txt, .docx, .pdf)
        if not any(filename.endswith(ext) for ext in ['.txt', '.docx', '.pdf']):
            return jsonify({'error': 'Invalid file type. Please upload .txt, .docx, or .pdf files'}), 400

        # Extract text content based on file type
        content = []
        try:
            # Text file handling (.txt) - try UTF-8 first, fall back to Latin-1
            if filename.endswith('.txt'):
                try:
                    # Try UTF-8 encoding first (most common for non-English text)
                    content = file.read().decode('utf-8').splitlines()
                except UnicodeDecodeError:
                    # Fall back to Latin-1 encoding if UTF-8 fails
                    file.seek(0)  # Reset file pointer
                    content = file.read().decode('latin-1').splitlines()
            
            # Word document handling (.docx)
            elif filename.endswith('.docx'):
                doc = Document(BytesIO(file.read()))
                content = [para.text for para in doc.paragraphs if para.text.strip()]  # Extract non-empty paragraphs
            
            # PDF document handling (.pdf)
            elif filename.endswith('.pdf'):
                pdf = PdfReader(BytesIO(file.read()))
                # Extract text from each page
                for page in pdf.pages:
                    text = page.extract_text()
                    if text.strip():  # Skip empty pages
                        content.extend(text.strip().splitlines())  # Split text into lines

        except Exception as e:
            # Handle file parsing errors
            return jsonify({'error': f'Failed to read file: {str(e)}'}), 400

        # Process each line
        results = []
        features = {
            'context_aware': True,
            'statistical_schwa': True,
            'auto_exceptions': True,
            'phonetic_refinement': True,
            'auto_capitalization': True
        }

        for text in content:
            if text.strip():                
                try:
                    processed = enhanced_hindi2english(text.strip(), features=features) if language == 'hindi' else enhanced_marathi2english(text.strip(), features=features)
                    results.append([text.strip(), processed])
                except Exception as e:
                    # More detailed error logging for special characters
                    print(f"Error processing line: {text}")
                    print(f"Error details: {str(e)}")
                    print("Character details:")
                    for i, char in enumerate(text.strip()):
                        print(f"Position {i}: '{char}' (Unicode: U+{ord(char):04X})")
                    # Still attempt basic transliteration even if enhanced fails
                    try:
                        from custom_indicate.transliterate import hindi2english, marathi2english
                        basic_processed = hindi2english(text.strip()) if language == 'hindi' else marathi2english(text.strip())
                        results.append([text.strip(), basic_processed])
                    except Exception as e2:
                        print(f"Basic transliteration also failed: {str(e2)}")
                        results.append([text.strip(), text.strip()])

        # If preview only, return JSON with sample data
        if preview_only:
            original_lines = [row[0] for row in results]
            transliterated_lines = [row[1] for row in results]
            
            # Limit preview to first 500 characters to avoid overwhelming the UI
            original_text = "\n".join(original_lines)[:500]
            transliterated_text = "\n".join(transliterated_lines)[:500]
            
            if len("\n".join(original_lines)) > 500:
                original_text += "..."
            if len("\n".join(transliterated_lines)) > 500:
                transliterated_text += "..."
            
            return jsonify({
                'original_text': original_text,
                'transliterated_text': transliterated_text,
                'total_lines': len(results),
                'file_type': filename.split('.')[-1].upper()
            })

        # For full processing, create downloadable file
        output = BytesIO()
        
        # Add each transliterated text as a new line
        transliterated_lines = [row[1] for row in results]
        output_text = "\n".join(transliterated_lines)
        
        output.write(output_text.encode('utf-8'))
        output.seek(0)

        # Generate output filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        base_name = os.path.splitext(filename)[0]
        output_filename = f"{base_name}_transliterated_{timestamp}.txt"

        # Send response
        return send_file(
            output,
            mimetype='text/plain',
            as_attachment=True,
            download_name=output_filename,
            max_age=0
        )

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/translate', methods=['POST'])
def translate_text():
    input_text = request.form.get('input_text', '')
    source_lang = request.form.get('source_lang', 'hi')
    target_lang = request.form.get('target_lang', 'en')
    
    try:
        translator = Translator()
        translation = translator.translate(input_text, src=source_lang, dest=target_lang)
        return jsonify({'translation': translation.text})
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/history')
@login_required
def history():
    user_history = TransliterationHistory.query.filter_by(user_id=current_user.id).order_by(TransliterationHistory.created_at.desc()).all()
    return render_template('history.html', history=user_history)

@app.route('/settings')
@login_required
def settings():
    return render_template('settings.html')

@app.route('/clear_history', methods=['POST'])
@login_required
def clear_history():
    try:
        # Delete all history records for the current user
        TransliterationHistory.query.filter_by(user_id=current_user.id).delete()
        db.session.commit()
        return jsonify({'success': True, 'message': 'History cleared successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Error clearing history: {str(e)}'})

@app.route('/export_history')
@login_required
def export_history():
    try:
        # Get all history records for the current user
        user_history = TransliterationHistory.query.filter_by(user_id=current_user.id).order_by(TransliterationHistory.created_at.desc()).all()
        
        if not user_history:
            flash('No history found to export.')
            return redirect(url_for('history'))
        
        # Create a CSV-like content
        content = "Date & Time,Input Text,Output Text,Language\n"
        for item in user_history:
            # Escape commas and quotes in CSV
            input_text = item.input_text.replace('"', '""').replace(',', '\\,')
            output_text = item.output_text.replace('"', '""').replace(',', '\\,')
            content += f'"{item.created_at.strftime("%Y-%m-%d %H:%M")}","{input_text}","{output_text}","{item.language}"\n'
        
        # Create a file-like object
        output = BytesIO()
        output.write(content.encode('utf-8'))
        output.seek(0)
        
        # Generate filename with current timestamp
        filename = f"transliteration_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        return send_file(
            output,
            mimetype='text/csv',
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        flash(f'Error exporting history: {str(e)}')
        return redirect(url_for('history'))

#---------------------------------------------------------------
# PREMIUM FEATURES & ANALYTICS
#---------------------------------------------------------------

# API endpoint for advanced analytics (premium feature - greyed out in UI)
@app.route('/api/analytics', methods=['GET'])
@login_required
def analytics():
    """
    Placeholder for premium analytics features.
    Currently returns a message indicating this is a premium feature.
    
    Returns:
        JSON response indicating premium status required
    """
    return jsonify({'status': 'premium_required'})

#---------------------------------------------------------------
# MACHINE LEARNING & FEEDBACK SYSTEM
#---------------------------------------------------------------

@app.route('/feedback', methods=['POST'])
def submit_feedback():
    """
    Process user corrections to improve the transliteration system.
    
    This endpoint implements a continuous learning system. When users correct
    transliterations, the system analyzes the differences between the original
    transliteration and the corrected version, and updates its exception
    dictionary to improve future results.
    
    Request parameters:
        - original_text: The original text in Hindi/Marathi
        - auto_transliteration: The system-generated transliteration
        - corrected_transliteration: The user's corrected version
        - language: The source language (hindi, marathi)
    
    Returns:
        JSON response with success/error status and the number of improvements learned
    """
    original_text = request.form.get('original_text', '')
    auto_transliteration = request.form.get('auto_transliteration', '')
    corrected_transliteration = request.form.get('corrected_transliteration', '')
    language = request.form.get('language', 'hindi')
    
    # Validate required fields
    if not original_text or not auto_transliteration or not corrected_transliteration:
        return jsonify({'status': 'error', 'message': 'Missing required fields'})
    
    # Process the feedback and learn from corrections
    try:
        # The learn_from_corrections function analyzes differences and updates exception dictionaries
        exceptions = learn_from_corrections([original_text], [auto_transliteration], [corrected_transliteration], language)
        
        # Return success with the number of improvements learned
        return jsonify({
            'status': 'success', 
            'message': f'Thank you for your feedback! {len(exceptions)} improvements learned.',
            'improvements': len(exceptions)
        })
    except Exception as e:
        # Handle any errors during the learning process
        return jsonify({'status': 'error', 'message': f'Error processing feedback: {str(e)}'})

@app.route('/delete_history', methods=['POST'])
@login_required
def delete_history():
    try:
        # Delete all history records for the current user
        TransliterationHistory.query.filter_by(user_id=current_user.id).delete()
        db.session.commit()
        flash('Your transliteration history has been successfully deleted.')
        return redirect(url_for('settings', _anchor='danger'))
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting history: {str(e)}', 'error')
        return redirect(url_for('settings', _anchor='danger'))

@app.route('/delete_account', methods=['POST'])
@login_required
def delete_account():
    try:
        # Begin transaction
        user_id = current_user.id
        
        # First delete all history records for the current user
        TransliterationHistory.query.filter_by(user_id=user_id).delete()
        
        # Then delete the user account
        User.query.filter_by(id=user_id).delete()
        
        # Commit transaction
        db.session.commit()
        
        # Log the user out
        logout_user()
        
        flash('Your account has been successfully deleted.')
        return redirect(url_for('index'))
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting account: {str(e)}', 'error')
        return redirect(url_for('settings', _anchor='danger'))

def cleanup_temp_files(temp_dir, max_age_hours=1):
    """Clean up old temporary files"""
    try:
        if not os.path.exists(temp_dir):
            return
            
        current_time = datetime.now()
        for filename in os.listdir(temp_dir):
            filepath = os.path.join(temp_dir, filename)
            try:
                # Skip if file is currently being used
                if not os.path.exists(filepath):
                    continue
                    
                # Remove files older than max_age_hours
                file_modified = datetime.fromtimestamp(os.path.getmtime(filepath))
                if (current_time - file_modified).total_seconds() > max_age_hours * 3600:
                    os.remove(filepath)
            except Exception as e:
                print(f"Error cleaning up file {filename}: {e}")
    except Exception as e:
        print(f"Error during temp file cleanup: {e}")

if __name__ == '__main__':
    app.run(debug=True)

# Add a specific route for favicon.ico
@app.route('/favicon.ico')
def favicon():
    return app.send_static_file('favicon.ico')