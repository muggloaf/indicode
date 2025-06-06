from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
import json
# Using enhanced custom implementation for transliteration
from custom_indicate import enhanced_hindi2english, enhanced_marathi2english
from custom_indicate.exception_detection import learn_from_corrections
from googletrans import Translator

# Initialize Flask application
app = Flask(__name__)
# Enable CORS with more explicit configuration
CORS(app, resources={r"/*": {"origins": "*", "supports_credentials": True}})
app.secret_key = 'your_super_secret_key_change_in_production'

# Ensure database directory exists
db_path = os.path.join(os.path.dirname(__file__), 'database')
if not os.path.exists(db_path):
    os.makedirs(db_path)

# Configure database URI with absolute path
db_file = os.path.join(db_path, 'transliterate.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_file}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# User Model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    name = db.Column(db.String(100))
    history = db.relationship('TransliterationHistory', backref='user', lazy=True)

# Transliteration History Model
class TransliterationHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    input_text = db.Column(db.Text, nullable=False)
    output_text = db.Column(db.Text, nullable=False)
    language = db.Column(db.String(10), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Create database tables
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

@app.route('/transliterate', methods=['POST'])
def transliterate_text():
    print("Received transliteration request")
    print(f"Form data: {request.form}")
    print(f"JSON data: {request.get_json(silent=True)}")
    print(f"Request headers: {request.headers}")
    
    # Try to get input text from different sources
    input_text = None
    if request.form:
        input_text = request.form.get('input_text', '')
    elif request.get_json(silent=True):
        input_text = request.get_json(silent=True).get('input_text', '')
    else:
        input_text = request.data.decode('utf-8').split('input_text=')[1].split('&')[0] if 'input_text=' in request.data.decode('utf-8') else ''
    
    print(f"Input text: {input_text}")
    language = request.form.get('language', 'hindi')
    print(f"Language: {language}")
    
    # Get feature flags from form if available
    features = {
        'context_aware': request.form.get('context_aware', 'true').lower() == 'true',
        'statistical_schwa': request.form.get('statistical_schwa', 'true').lower() == 'true',
        'auto_exceptions': request.form.get('auto_exceptions', 'true').lower() == 'true',
        'phonetic_refinement': request.form.get('phonetic_refinement', 'true').lower() == 'true',
        'auto_capitalization': request.form.get('auto_capitalization', 'true').lower() == 'true'
    }
    
    try:
        if language == 'hindi':
            output_text = enhanced_hindi2english(input_text, features)
        elif language == 'marathi':
            output_text = enhanced_marathi2english(input_text, features)
        elif language == 'english':
            # For English, we just return the text as is - no transliteration needed
            output_text = input_text
        else:
            # Placeholder for future language support
            output_text = "Unsupported language selection"
    except ValueError as e:
        # Handle the transliteration error
        return jsonify({'error': str(e), 'output': ''})
    except Exception as e:
        # Handle any other unexpected errors
        return jsonify({'error': f"An unexpected error occurred: {str(e)}", 'output': ''})
    
    # Save to history if user is logged in
    if current_user.is_authenticated:
        history = TransliterationHistory(
            user_id=current_user.id,
            input_text=input_text,
            output_text=output_text,
            language=language
        )
        db.session.add(history)
        db.session.commit()
    
    return jsonify({'output': output_text})

# Legacy route for backwards compatibility
@app.route('/indicate', methods=['POST'])
def indicate_text():
    return transliterate_text()

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

# API endpoint for batch processing (premium feature - greyed out)
@app.route('/api/batch', methods=['POST'])
@login_required
def batch_process():
    return jsonify({'status': 'premium_required'})

# API endpoint for advanced analytics (premium feature - greyed out)
@app.route('/api/analytics', methods=['GET'])
@login_required
def analytics():
    return jsonify({'status': 'premium_required'})

# API endpoint for submitting corrections and feedback
@app.route('/feedback', methods=['POST'])
def submit_feedback():
    original_text = request.form.get('original_text', '')
    auto_transliteration = request.form.get('auto_transliteration', '')
    corrected_transliteration = request.form.get('corrected_transliteration', '')
    language = request.form.get('language', 'hindi')
    
    if not original_text or not auto_transliteration or not corrected_transliteration:
        return jsonify({'status': 'error', 'message': 'Missing required fields'})
    
    # Learn from this correction
    try:
        exceptions = learn_from_corrections([original_text], [auto_transliteration], [corrected_transliteration], language)
        
        # Return success with the number of improvements learned
        return jsonify({
            'status': 'success', 
            'message': f'Thank you for your feedback! {len(exceptions)} improvements learned.',
            'improvements': len(exceptions)
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Error processing feedback: {str(e)}'})

# Main application entry point

if __name__ == '__main__':
    app.run(debug=True)