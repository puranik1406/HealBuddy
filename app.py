import os
import json
import base64
from datetime import datetime
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import openai
from dotenv import load_dotenv
import tempfile
import io
from gtts import gTTS
# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///healbuddy.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Initialize extensions
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Configure OpenAI
openai.api_key = os.getenv('OPENAI_API_KEY')

# Create upload directory if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    user_type = db.Column(db.String(20), nullable=False)  # 'patient', 'doctor', 'hospital'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Patient-specific fields
    blood_group = db.Column(db.String(5))
    allergies = db.Column(db.Text)
    medications = db.Column(db.Text)
    
    # Doctor/Hospital-specific fields
    license_number = db.Column(db.String(50))
    specialization = db.Column(db.String(100))
    hospital_name = db.Column(db.String(100))
    contact_number = db.Column(db.String(20))
    
    # Relationships
    health_records = db.relationship('HealthRecord', backref='patient', lazy=True)
    consultations = db.relationship('Consultation', foreign_keys='Consultation.patient_id', backref='patient', lazy=True)
    doctor_consultations = db.relationship('Consultation', foreign_keys='Consultation.doctor_id', backref='doctor', lazy=True)

class HealthRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    file_path = db.Column(db.String(500))
    file_type = db.Column(db.String(50))
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

class Consultation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    symptoms = db.Column(db.Text, nullable=False)
    duration = db.Column(db.String(100))
    pain_level = db.Column(db.Integer)
    ai_response = db.Column(db.Text)
    is_emergency = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    doctor_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    status = db.Column(db.String(20), default='pending')  # pending, reviewed, completed

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# AI Integration Functions
def transcribe_audio(audio_data):
    """Transcribe audio using OpenAI Whisper API"""
    try:
        # Save audio data to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
            temp_file.write(audio_data)
            temp_file_path = temp_file.name
        
        # Transcribe using OpenAI Whisper
        with open(temp_file_path, 'rb') as audio_file:
            transcript = openai.Audio.transcribe("whisper-1", audio_file)
        
        # Clean up temporary file
        os.unlink(temp_file_path)
        
        return transcript.text
    except Exception as e:
        print(f"Error in transcription: {e}")
        return None

def analyze_symptoms(symptoms_text):
    """Analyze symptoms using GPT-4o-mini"""
    try:
        prompt = f"""
        Analyze the following patient symptoms and extract key information in JSON format:
        
        Symptoms: {symptoms_text}
        
        Please provide a JSON response with the following structure:
        {{
            "symptoms": "main symptoms described",
            "duration": "how long symptoms have been present",
            "pain_level": number between 1-10,
            "urgency": "low", "medium", or "high",
            "recommendations": "brief recommendations"
        }}
        
        Pain level scale:
        1-3: Mild discomfort
        4-5: Moderate pain
        6-7: Significant pain
        8-9: Severe pain
        10: Unbearable pain
        """
        
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a medical AI assistant. Analyze symptoms and provide structured responses in JSON format."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        print(f"Error in symptom analysis: {e}")
        return {
            "symptoms": symptoms_text,
            "duration": "unknown",
            "pain_level": 5,
            "urgency": "medium",
            "recommendations": "Please consult with a healthcare professional for proper evaluation."
        }

def generate_tts_response(text):
    """Generate text-to-speech audio using gTTS"""
    try:
        tts = gTTS(text=text, lang='en', slow=False)
        audio_buffer = io.BytesIO()
        tts.write_to_fp(audio_buffer)
        audio_buffer.seek(0)
        return audio_buffer.getvalue()
    except Exception as e:
        print(f"Error in TTS generation: {e}")
        return None

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        user_type = request.form['user_type']
        
        # Check if user already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return render_template('register.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email already exists')
            return render_template('register.html')
        
        # Create new user
        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            user_type=user_type
        )
        
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please log in.')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.user_type == 'patient':
        consultations = Consultation.query.filter_by(patient_id=current_user.id).order_by(Consultation.created_at.desc()).limit(5).all()
        return render_template('patient_dashboard.html', consultations=consultations)
    elif current_user.user_type == 'doctor':
        consultations = Consultation.query.filter_by(doctor_id=current_user.id).order_by(Consultation.created_at.desc()).all()
        return render_template('doctor_dashboard.html', consultations=consultations)
    elif current_user.user_type == 'hospital':
        emergency_cases = Consultation.query.filter_by(is_emergency=True).order_by(Consultation.created_at.desc()).all()
        return render_template('hospital_dashboard.html', emergency_cases=emergency_cases)
    
    return redirect(url_for('index'))

@app.route('/symptom_input')
@login_required
def symptom_input():
    if current_user.user_type != 'patient':
        flash('Access denied')
        return redirect(url_for('dashboard'))
    return render_template('symptom_input.html')

@app.route('/upload_audio', methods=['POST'])
@login_required
def upload_audio():
    if current_user.user_type != 'patient':
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        # Get audio data from request
        audio_data = request.files['audio'].read()
        
        # Transcribe audio
        symptoms_text = transcribe_audio(audio_data)
        if not symptoms_text:
            return jsonify({'error': 'Failed to transcribe audio'}), 500
        
        # Analyze symptoms
        analysis = analyze_symptoms(symptoms_text)
        
        # Save consultation record
        consultation = Consultation(
            patient_id=current_user.id,
            symptoms=symptoms_text,
            duration=analysis.get('duration', 'unknown'),
            pain_level=analysis.get('pain_level', 5),
            ai_response=analysis.get('recommendations', ''),
            is_emergency=analysis.get('pain_level', 5) >= 9 or analysis.get('urgency') == 'high'
        )
        
        db.session.add(consultation)
        db.session.commit()
        
        # Generate TTS response
        tts_audio = generate_tts_response(analysis.get('recommendations', ''))
        
        return jsonify({
            'transcription': symptoms_text,
            'analysis': analysis,
            'consultation_id': consultation.id,
            'tts_audio': base64.b64encode(tts_audio).decode('utf-8') if tts_audio else None
        })
    
    except Exception as e:
        print(f"Error in upload_audio: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/submit_symptoms', methods=['POST'])
@login_required
def submit_symptoms():
    if current_user.user_type != 'patient':
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        symptoms_text = request.json.get('symptoms', '')
        
        # Analyze symptoms
        analysis = analyze_symptoms(symptoms_text)
        
        # Save consultation record
        consultation = Consultation(
            patient_id=current_user.id,
            symptoms=symptoms_text,
            duration=analysis.get('duration', 'unknown'),
            pain_level=analysis.get('pain_level', 5),
            ai_response=analysis.get('recommendations', ''),
            is_emergency=analysis.get('pain_level', 5) >= 9 or analysis.get('urgency') == 'high'
        )
        
        db.session.add(consultation)
        db.session.commit()
        
        return jsonify({
            'analysis': analysis,
            'consultation_id': consultation.id
        })
    
    except Exception as e:
        print(f"Error in submit_symptoms: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/health_records')
@login_required
def health_records():
    if current_user.user_type != 'patient':
        flash('Access denied')
        return redirect(url_for('dashboard'))
    
    records = HealthRecord.query.filter_by(patient_id=current_user.id).order_by(HealthRecord.uploaded_at.desc()).all()
    return render_template('health_records.html', records=records)

@app.route('/upload_record', methods=['POST'])
@login_required
def upload_record():
    if current_user.user_type != 'patient':
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        file = request.files['file']
        title = request.form.get('title', file.filename)
        description = request.form.get('description', '')
        
        if file and file.filename:
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            
            record = HealthRecord(
                patient_id=current_user.id,
                title=title,
                description=description,
                file_path=file_path,
                file_type=file.content_type
            )
            
            db.session.add(record)
            db.session.commit()
            
            return jsonify({'success': True, 'message': 'Record uploaded successfully'})
        
        return jsonify({'error': 'No file provided'}), 400
    
    except Exception as e:
        print(f"Error in upload_record: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/emergency_alert')
@login_required
def emergency_alert():
    if current_user.user_type != 'patient':
        flash('Access denied')
        return redirect(url_for('dashboard'))
    
    return render_template('emergency_alert.html')

@app.route('/trigger_emergency', methods=['POST'])
@login_required
def trigger_emergency():
    if current_user.user_type != 'patient':
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        # Create emergency consultation
        consultation = Consultation(
            patient_id=current_user.id,
            symptoms="EMERGENCY ALERT TRIGGERED",
            duration="immediate",
            pain_level=10,
            ai_response="Emergency services have been notified",
            is_emergency=True
        )
        
        db.session.add(consultation)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Emergency alert sent'})
    
    except Exception as e:
        print(f"Error in trigger_emergency: {e}")
        return jsonify({'error': 'Internal server error'}), 500

# Initialize database
def create_tables():
    db.create_all()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)
