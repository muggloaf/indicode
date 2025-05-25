from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import os
import json
import requests
import random
import string
import urllib.parse
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

# User Feedback Model - Individual Word Corrections
class UserFeedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user_email = db.Column(db.String(100), nullable=False)
    user_name = db.Column(db.String(100), nullable=False)
    original_word = db.Column(db.String(500), nullable=False)  # Original Hindi/Marathi word
    original_transliteration = db.Column(db.String(500), nullable=False)  # What our system provided
    corrected_transliteration = db.Column(db.String(500), nullable=False)  # User's correction
    source_language = db.Column(db.String(10), nullable=False)  # 'hindi' or 'marathi'
    target_language = db.Column(db.String(10), default='english', nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship back to user
    user = db.relationship('User', backref=db.backref('feedback', lazy=True))

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

# Email sending utility function
def send_email(to_email, subject, message):
    """Send email using The Group 11 API"""
    try:
        # Build URL step by step for debugging
        base_url = "https://thegroup11.com/api/sendmail"
        api_key = "dGhlZ3JvdXAxMQ=="
        
        # URL encode parameters
        encoded_to = urllib.parse.quote(to_email)
        encoded_subject = urllib.parse.quote(subject)
        encoded_message = urllib.parse.quote(message)
        
        api_url = f"{base_url}?api_key={api_key}&to={encoded_to}&subject={encoded_subject}&message={encoded_message}"
        
        print(f"Sending email to: {to_email}")
        print(f"API URL: {api_url}")
        
        response = requests.get(api_url, timeout=30)
        print(f"Email API Response Status: {response.status_code}")
        print(f"Email API Response Text: {response.text}")
        print(f"Email API Response Headers: {response.headers}")
        
        # Check for success - might need to check response content too
        if response.status_code == 200:
            return True
        else:
            print(f"API returned non-200 status: {response.status_code}")
            return False
            
    except requests.exceptions.Timeout:
        print("Email API timeout error")
        return False
    except requests.exceptions.RequestException as e:
        print(f"Email API request error: {e}")
        return False
    except Exception as e:
        print(f"Email sending error: {e}")
        return False

def generate_otp():
    """Generate a 6-digit OTP"""
    return ''.join(random.choices(string.digits, k=6))

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
        
        print(f"Registration attempt for email: {email}, name: {name}")
        
        # Basic validation
        if not email or not password or not name:
            flash('All fields are required.')
            return redirect(url_for('register'))
        
        # Check if email already exists
        user = User.query.filter_by(email=email).first()
        
        if user:
            flash('Email address already exists')
            return redirect(url_for('register'))
        
        # Generate OTP and store registration data in session
        otp = generate_otp()
        password_hash = generate_password_hash(password, method='pbkdf2:sha256')
        
        print(f"Generated OTP: {otp}")
        
        # Store registration data in session
        session['registration_data'] = {
            'email': email,
            'name': name,
            'password_hash': password_hash,
            'otp': otp,
            'expires_at': (datetime.utcnow() + timedelta(minutes=10)).isoformat()
        }
        
        print("Registration data stored in session")
        
        # Send OTP via email
        subject = "Verify Your Email - IndiCode"
        message = f"Hello {name},\n\nWelcome to IndiCode! Please use the following OTP to verify your email address:\n\nOTP: {otp}\n\nThis OTP will expire in 10 minutes.\n\nBest regards,\nIndiCode Team"
        
        print("Attempting to send email...")
        email_sent = send_email(email, subject, message)
        print(f"Email send result: {email_sent}")
        
        if email_sent:
            flash('OTP has been sent to your email. Please verify to complete registration.')
            return redirect(url_for('verify_otp'))
        else:
            # Clear session data if email failed
            session.pop('registration_data', None)
            flash('Failed to send OTP. Please check your email address and try again.')
            return redirect(url_for('register'))
    
    return render_template('register.html')

@app.route('/verify-otp', methods=['GET', 'POST'])
def verify_otp():
    if 'registration_data' not in session:
        flash('No pending registration found.')
        return redirect(url_for('register'))
    
    if request.method == 'POST':
        entered_otp = request.form.get('otp')
        reg_data = session['registration_data']
        
        # Check if OTP is expired
        expires_at = datetime.fromisoformat(reg_data['expires_at'])
        if datetime.utcnow() > expires_at:
            flash('OTP has expired. Please register again.')
            session.pop('registration_data', None)
            return redirect(url_for('register'))
        
        # Verify OTP
        if entered_otp == reg_data['otp']:
            # Create the user account
            new_user = User(
                email=reg_data['email'],
                password=reg_data['password_hash'],
                name=reg_data['name']
            )
            
            db.session.add(new_user)
            db.session.commit()
            
            # Send welcome email
            welcome_subject = "Welcome to IndiCode!"
            welcome_message = f"Dear {reg_data['name']},\n\nWelcome to IndiCode! Your account has been successfully created.\n\nIndiCode is your go-to platform for seamless transliteration between Indian languages and English. Whether you're working with Hindi, Marathi, or other regional languages, we've got you covered with our advanced AI-powered transliteration engine.\n\nFeatures you can now enjoy:\n- Real-time transliteration\n- Multiple language support\n- Transliteration history\n- Advanced customization options\n- Translation services\n\nStart exploring and make your multilingual content creation effortless!\n\nBest regards,\nThe IndiCode Team\n\nLogin now: {request.url_root}login"
            
            send_email(reg_data['email'], welcome_subject, welcome_message)
            
            session.pop('registration_data', None)
            flash('Account created successfully! A welcome email has been sent. Please login.')
            return redirect(url_for('login'))
        else:
            flash('Invalid OTP. Please try again.')
    
    return render_template('verify_otp.html', email=session['registration_data']['email'])

@app.route('/resend-otp', methods=['POST'])
def resend_otp():
    if 'registration_data' not in session:
        return jsonify({'success': False, 'message': 'No pending registration found.'})
    
    reg_data = session['registration_data']
    
    # Generate new OTP
    new_otp = generate_otp()
    reg_data['otp'] = new_otp
    reg_data['expires_at'] = (datetime.utcnow() + timedelta(minutes=10)).isoformat()
    session['registration_data'] = reg_data
    
    # Send new OTP
    subject = "New OTP - IndiCode Email Verification"
    message = f"Hello {reg_data['name']},\n\nHere's your new OTP for email verification:\n\nOTP: {new_otp}\n\nThis OTP will expire in 10 minutes.\n\nBest regards,\nIndiCode Team"
    
    if send_email(reg_data['email'], subject, message):
        return jsonify({'success': True, 'message': 'New OTP sent successfully!'})
    else:
        return jsonify({'success': False, 'message': 'Failed to send OTP. Please try again.'})

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

@app.route('/request-login-otp', methods=['POST'])
def request_login_otp():
    email = request.form.get('email')
    
    if not email:
        flash('Email address is required.')
        return redirect(url_for('login'))
    
    # Check if user exists
    user = User.query.filter_by(email=email).first()
    
    if not user:
        flash('No account found with this email address.')
        return redirect(url_for('login'))
    
    # Generate OTP and store login data in session
    otp = generate_otp()
    
    print(f"Generated login OTP: {otp} for email: {email}")
    
    # Store login OTP data in session
    session['login_otp_data'] = {
        'email': email,
        'user_id': user.id,
        'otp': otp,
        'expires_at': (datetime.utcnow() + timedelta(minutes=10)).isoformat()
    }
    
    # Send OTP via email
    subject = "Login OTP - IndiCode"
    message = f"Hello {user.name},\n\nYou've requested to login to your IndiCode account. Please use the following OTP to complete your login:\n\nOTP: {otp}\n\nThis OTP will expire in 10 minutes.\n\nIf you didn't request this login, please ignore this email.\n\nBest regards,\nIndiCode Team"
    
    print("Attempting to send login OTP email...")
    email_sent = send_email(email, subject, message)
    print(f"Login OTP email send result: {email_sent}")
    
    if email_sent:
        flash('Login OTP has been sent to your email.')
        return redirect(url_for('verify_login_otp'))
    else:
        # Clear session data if email failed
        session.pop('login_otp_data', None)
        flash('Failed to send login OTP. Please try again.')
        return redirect(url_for('login'))

@app.route('/verify-login-otp', methods=['GET', 'POST'])
def verify_login_otp():
    if 'login_otp_data' not in session:
        flash('No pending login OTP found.')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        entered_otp = request.form.get('otp')
        login_data = session['login_otp_data']
        
        # Check if OTP is expired
        expires_at = datetime.fromisoformat(login_data['expires_at'])
        if datetime.utcnow() > expires_at:
            flash('OTP has expired. Please request a new one.')
            session.pop('login_otp_data', None)
            return redirect(url_for('login'))
        
        # Verify OTP
        if entered_otp == login_data['otp']:
            # Login the user
            user = User.query.get(login_data['user_id'])
            if user:
                login_user(user)
                session.pop('login_otp_data', None)
                flash(f'Welcome back, {user.name}! You have been logged in successfully.')
                return redirect(url_for('dashboard'))
            else:
                flash('User account not found.')
                session.pop('login_otp_data', None)
                return redirect(url_for('login'))
        else:
            flash('Invalid OTP. Please try again.')
    
    return render_template('verify_login_otp.html', email=session['login_otp_data']['email'])

@app.route('/resend-login-otp', methods=['POST'])
def resend_login_otp():
    if 'login_otp_data' not in session:
        return jsonify({'success': False, 'message': 'No pending login OTP found.'})
    
    login_data = session['login_otp_data']
    
    # Generate new OTP
    new_otp = generate_otp()
    login_data['otp'] = new_otp
    login_data['expires_at'] = (datetime.utcnow() + timedelta(minutes=10)).isoformat()
    session['login_otp_data'] = login_data
    
    # Get user details
    user = User.query.get(login_data['user_id'])
    
    # Send new OTP
    subject = "New Login OTP - IndiCode"
    message = f"Hello {user.name},\n\nHere's your new login OTP:\n\nOTP: {new_otp}\n\nThis OTP will expire in 10 minutes.\n\nBest regards,\nIndiCode Team"
    
    if send_email(login_data['email'], subject, message):
        return jsonify({'success': True, 'message': 'New login OTP sent successfully!'})
    else:
        return jsonify({'success': False, 'message': 'Failed to send OTP. Please try again.'})

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
@login_required
def submit_feedback():
    original_text = request.form.get('original_text', '')
    auto_transliteration = request.form.get('auto_transliteration', '')
    corrected_transliteration = request.form.get('corrected_transliteration', '')
    language = request.form.get('language', 'hindi')
    
    if not original_text or not auto_transliteration or not corrected_transliteration:
        return jsonify({'status': 'error', 'message': 'Missing required fields'})
    
    # Split texts into words for individual comparison
    original_words = original_text.split()
    auto_words = auto_transliteration.split()
    corrected_words = corrected_transliteration.split()
    
    # Ensure all word lists have the same length
    if len(original_words) != len(auto_words) or len(auto_words) != len(corrected_words):
        return jsonify({'status': 'error', 'message': 'Word count mismatch between original, auto-transliterated, and corrected text'})
    
    # Save individual word corrections to database
    corrections_count = 0
    try:
        for i, (orig_word, auto_word, corrected_word) in enumerate(zip(original_words, auto_words, corrected_words)):
            # Only save if there's a difference between auto and corrected
            if auto_word != corrected_word:
                feedback = UserFeedback(
                    user_id=current_user.id,
                    user_email=current_user.email,
                    user_name=current_user.name or 'Anonymous',
                    original_word=orig_word,
                    original_transliteration=auto_word,
                    corrected_transliteration=corrected_word,
                    source_language=language,
                    target_language='english'
                )
                db.session.add(feedback)
                corrections_count += 1
        
        db.session.commit()
        
        # Learn from this correction (continue saving to JSON files too)
        exceptions = learn_from_corrections([original_text], [auto_transliteration], [corrected_transliteration], language)
        
        # Return success with the number of improvements learned
        return jsonify({
            'status': 'success', 
            'message': f'Thank you for your feedback! {corrections_count} word corrections and {len(exceptions)} improvements learned.',
            'corrections': corrections_count,
            'improvements': len(exceptions)
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': f'Error processing feedback: {str(e)}'})

# API endpoint to check if user can submit feedback
@app.route('/check_feedback_access', methods=['GET'])
def check_feedback_access():
    if current_user.is_authenticated:
        return jsonify({'can_submit': True})
    else:
        return jsonify({'can_submit': False, 'message': 'Please log in to provide feedback'})

# Main application entry point

if __name__ == '__main__':
    app.run(debug=True)