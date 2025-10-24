import os
import json
import base64
import traceback
from datetime import datetime
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import google.generativeai as genai
from dotenv import load_dotenv
import speech_recognition as sr
from gtts import gTTS
from pydub import AudioSegment
import io
# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///healbuddy.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Add from_json filter to Jinja
@app.template_filter('from_json')
def from_json_filter(value):
    try:
        return json.loads(value) if isinstance(value, str) else value
    except:
        return {}

# Initialize extensions
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Configure Gemini AI
try:
    genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
    model = genai.GenerativeModel('models/gemini-2.5-flash')
except Exception as e:
    print(f"Error initializing Gemini AI: {e}")
    model = None

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
    
    # Common fields
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    gender = db.Column(db.String(20))
    date_of_birth = db.Column(db.Date)
    phone_number = db.Column(db.String(20))
    address = db.Column(db.Text)
    
    # Patient-specific fields
    height = db.Column(db.Float)  # in cm
    weight = db.Column(db.Float)  # in kg
    blood_group = db.Column(db.String(5))
    allergies = db.Column(db.Text)
    medical_conditions = db.Column(db.Text)
    current_medications = db.Column(db.Text)
    emergency_contact_name = db.Column(db.String(100))
    emergency_contact_phone = db.Column(db.String(20))
    preferred_hospital = db.Column(db.String(200))  # Legacy field
    preferred_hospitals = db.Column(db.Text)  # JSON array of multiple hospitals
    
    # Doctor-specific fields
    license_number = db.Column(db.String(50))
    degree = db.Column(db.String(100))
    specialization = db.Column(db.String(100))
    years_of_experience = db.Column(db.Integer)
    hospital_affiliation = db.Column(db.String(200))
    consultation_fee = db.Column(db.Float)
    
    # Hospital-specific fields
    hospital_name = db.Column(db.String(200))
    hospital_type = db.Column(db.String(50))  # 'public', 'private', 'clinic'
    registration_number = db.Column(db.String(100))
    license_number_hospital = db.Column(db.String(100))
    emergency_services = db.Column(db.Boolean, default=False)
    specialties_available = db.Column(db.Text)
    total_beds = db.Column(db.Integer)
    icu_beds = db.Column(db.Integer)
    emergency_contact = db.Column(db.String(20))
    
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

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    consultation_id = db.Column(db.Integer, db.ForeignKey('consultation.id'))
    appointment_type = db.Column(db.String(20), default='online')  # online, offline
    appointment_date = db.Column(db.DateTime)
    appointment_slot = db.Column(db.String(50))  # e.g., "09:00-10:00"
    status = db.Column(db.String(20), default='scheduled')  # scheduled, completed, cancelled
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    patient = db.relationship('User', foreign_keys=[patient_id], backref='patient_appointments')
    doctor = db.relationship('User', foreign_keys=[doctor_id], backref='doctor_appointments')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# AI Integration Functions
def analyze_symptoms(symptoms_text, severity=None):
    """Analyze symptoms using Gemini AI"""
    try:
        severity_text = f"Patient-reported severity level: {severity}/10" if severity else "Severity level not provided"
        
        # Print debug information
        print(f"Analyzing symptoms: {symptoms_text}")
        print(f"Severity: {severity_text}")
        
        prompt = f"""
        You are a medical analysis AI. Analyze these patient symptoms and provide a detailed medical assessment.

        Symptoms: {symptoms_text}
        {severity_text}

        First, parse and extract individual symptoms. For each symptom, provide a suggested default severity (1-10) based on the text.

        If more information is required to make a confident assessment (for example: onset, associated symptoms, aggravating/alleviating factors, fever, breathing difficulty, etc.), include a list of follow_up_questions the system should ask the patient. Each follow-up question should be a short, focused question.

        Respond with this exact JSON structure (fields not applicable can be empty arrays/strings):
        {{
            "identified_symptoms": ["symptom1", "symptom2", ...],
            "default_severities": [5, 5, ...],
            "follow_up_questions": ["question 1", "question 2"],
            "duration": "how long symptoms have been present (if mentioned)",
            "urgency": "low/medium/high",
            "possible_conditions": [
                "condition 1 with brief description",
                "condition 2 with brief description"
            ],
            "recommendations": "initial recommendations for home care and when to seek medical attention",
            "diagnosis": "brief preliminary analysis",
            "suggested_medications": [
                {{
                    "name": "medication name",
                    "purpose": "what it treats",
                    "notes": "usage notes/warnings"
                }}
            ],
            "red_flags": ["any concerning symptoms that need immediate attention"]
        }}

        Rules:
        1. Provide concise follow-up questions only when needed.
        2. Do NOT provide definitive diagnoses — only preliminary suggestions.
        3. Keep medication suggestions limited to common over-the-counter options and include cautions.
        4. If any red flags appear, set urgency to "high" and include them in red_flags.
        5. Keep the JSON valid and parsable — do not wrap the JSON in markdown fences or code blocks.
        6. Return ONLY the JSON structure, no additional text before or after.
        """
        
        # Use Gemini AI to generate response
        response = model.generate_content(prompt)
        
        # Extract and validate the response
        response_text = response.text
        print(f"Raw API Response: {response_text}")  # Debug log
        
        try:
            # Clean up the response text to ensure it's valid JSON
            response_text = response_text.strip()
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.startswith('```'):
                response_text = response_text[3:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
            response_text = response_text.strip()
            
            analysis = json.loads(response_text)
            # Ensure all required fields are present and normalize structure
            return {
                "identified_symptoms": analysis.get("identified_symptoms", [symptoms_text]),
                "default_severities": analysis.get("default_severities", [severity if severity is not None else 5]),
                "follow_up_questions": analysis.get("follow_up_questions", []),
                "duration": analysis.get("duration", "unknown"),
                "pain_level": severity if severity is not None else analysis.get("pain_level", 5),
                "urgency": analysis.get("urgency", "medium"),
                "possible_conditions": analysis.get("possible_conditions", ["Analysis in progress"]),
                "recommendations": analysis.get("recommendations", "Please consult with a healthcare professional for proper evaluation."),
                "diagnosis": analysis.get("diagnosis", "Initial analysis in progress"),
                "suggested_medications": analysis.get("suggested_medications", []),
                "red_flags": analysis.get("red_flags", [])
            }
            
        except json.JSONDecodeError as e:
            print(f"JSON Parse Error: {e}")
            print(f"Problematic response: {response_text}")
            # Return a basic analysis if JSON parsing fails
            return {
                "identified_symptoms": [symptoms_text],
                "default_severities": [severity if severity is not None else 5],
                "follow_up_questions": [],
                "duration": "unknown",
                "pain_level": severity if severity is not None else 5,
                "urgency": "medium",
                "recommendations": "Please consult with a healthcare professional for proper evaluation.",
                "possible_conditions": ["Unable to determine at this time"],
                "diagnosis": "Analysis temporarily unavailable",
                "suggested_medications": [],
                "red_flags": []
            }
        
    except Exception as e:
        print(f"Error in symptom analysis: {e}")
        import traceback
        traceback.print_exc()
        return {
            "identified_symptoms": [symptoms_text],
            "default_severities": [severity if severity is not None else 5],
            "follow_up_questions": [],
            "duration": "unknown",
            "pain_level": severity if severity is not None else 5,
            "urgency": "medium",
            "recommendations": "Please consult with a healthcare professional for proper evaluation.",
            "possible_conditions": ["Unable to analyze at this time"],
            "diagnosis": "Analysis error occurred",
            "suggested_medications": [],
            "red_flags": []
        }

# Voice Processing Functions
def transcribe_audio(audio_file_path):
    """Transcribe audio file to text using Google Speech Recognition"""
    try:
        recognizer = sr.Recognizer()
        
        # Convert webm to wav if needed
        if audio_file_path.endswith('.webm'):
            audio = AudioSegment.from_file(audio_file_path, format="webm")
            wav_path = audio_file_path.replace('.webm', '.wav')
            audio.export(wav_path, format="wav")
            audio_file_path = wav_path
        
        # Transcribe
        with sr.AudioFile(audio_file_path) as source:
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data)
            return text
    except sr.UnknownValueError:
        return "Could not understand audio"
    except sr.RequestError as e:
        print(f"Speech recognition error: {e}")
        return "Error processing audio"
    except Exception as e:
        print(f"Transcription error: {e}")
        traceback.print_exc()
        return "Error transcribing audio"

def generate_tts_audio(text):
    """Generate text-to-speech audio and return base64 encoded MP3"""
    try:
        # Create TTS
        tts = gTTS(text=text, lang='en', slow=False)
        
        # Save to bytes buffer
        audio_buffer = io.BytesIO()
        tts.write_to_fp(audio_buffer)
        audio_buffer.seek(0)
        
        # Encode to base64
        audio_base64 = base64.b64encode(audio_buffer.read()).decode('utf-8')
        return audio_base64
    except Exception as e:
        print(f"TTS error: {e}")
        traceback.print_exc()
        return None

def generate_conversational_response(conversation_history):
    """Generate AI response for ongoing conversation with follow-up questions"""
    try:
        # Build conversation context
        conversation_context = "\n".join([
            f"{msg['role'].upper()}: {msg['content']}" for msg in conversation_history
        ])
        
        prompt = f"""
You are a medical AI assistant having a conversation with a patient to gather symptom information.

Conversation so far:
{conversation_context}

Based on the conversation, provide a response that:
1. Acknowledges what the patient said
2. Asks a relevant follow-up question to gather more information (about duration, severity, associated symptoms, triggers, etc.)
3. Is empathetic and professional
4. Keeps responses concise (2-3 sentences max)

If you have gathered sufficient information about:
- Main symptoms and their severity
- Duration/onset
- Associated symptoms
- Any relevant medical history

Then indicate you're ready for diagnosis by including "READY_FOR_DIAGNOSIS: true" at the end.

Provide your response in this format:
{{
    "text": "Your conversational response here",
    "ready_for_diagnosis": false
}}
"""
        
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        
        # Clean up JSON
        if response_text.startswith('```json'):
            response_text = response_text[7:]
        if response_text.startswith('```'):
            response_text = response_text[3:]
        if response_text.endswith('```'):
            response_text = response_text[:-3]
        response_text = response_text.strip()
        
        result = json.loads(response_text)
        return result
    except Exception as e:
        print(f"Error generating conversational response: {e}")
        traceback.print_exc()
        return {
            "text": "I understand. Can you tell me more about when these symptoms started?",
            "ready_for_diagnosis": False
        }

def analyze_conversation_for_diagnosis(conversation_history):
    """Analyze complete conversation to extract symptoms and generate diagnosis"""
    try:
        # Extract all patient messages
        patient_messages = [msg['content'] for msg in conversation_history if msg['role'] == 'user']
        combined_symptoms = " ".join(patient_messages)
        
        # Use existing analyze_symptoms function
        return analyze_symptoms(combined_symptoms, severity=None)
    except Exception as e:
        print(f"Error analyzing conversation: {e}")
        traceback.print_exc()
        return None


@app.route('/finalize_analysis', methods=['POST'])
@login_required
def finalize_analysis():
    """Finalize analysis after user answers follow-up questions and sets per-symptom severities.

    Expected JSON body:
    {
        "symptoms": [{"symptom": "headache", "severity": 6}, ...],
        "follow_up_answers": [{"question": "Do you have a fever?", "answer": "Yes, 101F"}, ...],
        "consultation_id": optional
    }
    """
    if current_user.user_type != 'patient':
        return jsonify({'error': 'Access denied'}), 403

    try:
        data = request.json
        symptoms = data.get('symptoms', [])
        follow_up_answers = data.get('follow_up_answers', [])

        # Build a combined context string for re-analysis
        symptoms_text = '. '.join([f"{s['symptom']} (Severity: {s.get('severity', 5)}/10)" for s in symptoms])
        answers_text = '. '.join([f"Q: {a.get('question')} A: {a.get('answer')}" for a in follow_up_answers])
        combined_text = symptoms_text + ('. ' + answers_text if answers_text else '')

        overall_severity = 5
        if symptoms:
            overall_severity = max(1, sum(int(s.get('severity', 5)) for s in symptoms) // len(symptoms))

        analysis = analyze_symptoms(combined_text, overall_severity)

        # Persist consultation (create or update)
        consultation_id = data.get('consultation_id')
        if consultation_id:
            consultation = Consultation.query.get(consultation_id)
            if consultation and consultation.patient_id == current_user.id:
                consultation.symptoms = symptoms_text
                consultation.pain_level = overall_severity
                consultation.ai_response = json.dumps(analysis)
                db.session.commit()
        else:
            consultation = Consultation(
                patient_id=current_user.id,
                symptoms=symptoms_text,
                duration=analysis.get('duration', 'unknown'),
                pain_level=overall_severity,
                ai_response=json.dumps(analysis),
                is_emergency=(analysis.get('urgency') == 'high') or bool(analysis.get('red_flags'))
            )
            db.session.add(consultation)
            db.session.commit()
            consultation_id = consultation.id

        return jsonify({'analysis': analysis, 'consultation_id': consultation_id})

    except Exception as e:
        print(f"Error in finalize_analysis: {e}")
        return jsonify({'error': 'Internal server error'}), 500

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Get basic information
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        user_type = request.form['user_type']
        first_name = request.form.get('first_name', '')
        last_name = request.form.get('last_name', '')
        phone_number = request.form.get('phone_number', '')
        address = request.form.get('address', '')
        
        # Check if user already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return render_template('register.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email already exists')
            return render_template('register.html')
        
        # Create new user with basic info
        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            user_type=user_type,
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number,
            address=address
        )
        
        # Add user-type specific information
        if user_type == 'patient':
            # Patient-specific fields
            user.gender = request.form.get('gender', '')
            user.date_of_birth = datetime.strptime(request.form.get('date_of_birth', '1990-01-01'), '%Y-%m-%d').date() if request.form.get('date_of_birth') else None
            user.height = float(request.form.get('height', 0)) if request.form.get('height') else None
            user.weight = float(request.form.get('weight', 0)) if request.form.get('weight') else None
            user.blood_group = request.form.get('blood_group', '')
            user.allergies = request.form.get('allergies', '')
            user.medical_conditions = request.form.get('medical_conditions', '')
            user.current_medications = request.form.get('current_medications', '')
            user.emergency_contact_name = request.form.get('emergency_contact_name', '')
            user.emergency_contact_phone = request.form.get('emergency_contact_phone', '')
            preferred_hospital = request.form.get('preferred_hospital', '')
            
            # Validate preferred hospital if provided
            if preferred_hospital:
                # Check if the hospital is registered on the portal
                hospital_exists = User.query.filter_by(user_type='hospital', hospital_name=preferred_hospital).first()
                if not hospital_exists:
                    flash(f'Hospital "{preferred_hospital}" is not registered on this portal. Please choose a registered hospital or leave blank.')
                    return render_template('register.html')
            
            user.preferred_hospital = preferred_hospital
            
        elif user_type == 'doctor':
            # Doctor-specific fields
            user.license_number = request.form.get('license_number', '')
            user.degree = request.form.get('degree', '')
            user.specialization = request.form.get('specialization', '')
            user.years_of_experience = int(request.form.get('years_of_experience', 0)) if request.form.get('years_of_experience') else None
            user.hospital_affiliation = request.form.get('hospital_affiliation', '')
            user.consultation_fee = float(request.form.get('consultation_fee', 0)) if request.form.get('consultation_fee') else None
            
        elif user_type == 'hospital':
            # Hospital-specific fields
            user.hospital_name = request.form.get('hospital_name', '')
            user.hospital_type = request.form.get('hospital_type', '')
            user.registration_number = request.form.get('registration_number', '')
            user.license_number_hospital = request.form.get('license_number_hospital', '')
            user.emergency_services = 'emergency_services' in request.form
            user.specialties_available = request.form.get('specialties_available', '')
            user.total_beds = int(request.form.get('total_beds', 0)) if request.form.get('total_beds') else None
            user.icu_beds = int(request.form.get('icu_beds', 0)) if request.form.get('icu_beds') else None
            user.emergency_contact = request.form.get('emergency_contact', '')
        
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
        consultations = Consultation.query.filter_by(patient_id=current_user.id).order_by(Consultation.created_at.desc()).limit(10).all()
        appointments = Appointment.query.filter_by(patient_id=current_user.id).order_by(Appointment.appointment_date.desc()).limit(5).all()
        
        # Create a mapping of consultation_id to appointment for easy lookup (only non-completed)
        consultation_appointments = {}
        for appointment in Appointment.query.filter_by(patient_id=current_user.id).all():
            if appointment.consultation_id and appointment.status != 'completed':
                consultation_appointments[appointment.consultation_id] = appointment
        
        return render_template('patient_dashboard.html', 
                             consultations=consultations, 
                             appointments=appointments,
                             consultation_appointments=consultation_appointments,
                             get_severity=get_severity_classification)
    elif current_user.user_type == 'doctor':
        # Get all appointments for this doctor
        all_appointments = Appointment.query.filter_by(doctor_id=current_user.id).order_by(Appointment.appointment_date).all()
        
        # Get all unique consultations linked to this doctor's appointments
        consultation_ids = set()
        for appt in all_appointments:
            if appt.consultation_id:
                consultation_ids.add(appt.consultation_id)
        
        # Fetch all consultations for this doctor (both through appointments and direct assignment)
        consultations_from_appointments = Consultation.query.filter(Consultation.id.in_(consultation_ids)).all() if consultation_ids else []
        consultations_direct = Consultation.query.filter_by(doctor_id=current_user.id).all()
        
        # Combine and deduplicate consultations
        all_consultations_dict = {}
        for c in consultations_from_appointments + consultations_direct:
            all_consultations_dict[c.id] = c
        consultations = list(all_consultations_dict.values())
        consultations.sort(key=lambda x: x.created_at, reverse=True)
        
        # Filter out completed appointments and appointments with completed consultations
        appointments = []
        for appt in all_appointments:
            # Skip if appointment itself is completed
            if appt.status == 'completed':
                continue
            
            # If appointment has no consultation, include it
            if not appt.consultation_id:
                appointments.append(appt)
            else:
                # Check if consultation is completed
                consultation = Consultation.query.get(appt.consultation_id)
                if consultation and consultation.status != 'completed':
                    appointments.append(appt)
        
        # Calculate case counts
        # Active cases: consultations assigned to this doctor that are not completed (pending or reviewed)
        active_cases = len([c for c in consultations if c.status != 'completed'])
        
        # Completed cases: consultations this doctor has completed
        completed_cases = len([c for c in consultations if c.status == 'completed'])
        
        # Debug logging
        print(f"Doctor {current_user.id} Dashboard:")
        print(f"  Total consultations fetched: {len(consultations)}")
        print(f"  Active cases: {active_cases}")
        print(f"  Completed cases: {completed_cases}")
        for c in consultations:
            print(f"    Consultation {c.id}: status={c.status}, doctor_id={c.doctor_id}")
        
        return render_template('doctor_dashboard.html', 
                             consultations=consultations, 
                             appointments=appointments, 
                             active_cases=active_cases,
                             completed_cases=completed_cases,
                             get_severity=get_severity_classification)
    elif current_user.user_type == 'hospital':
        # Only show cases where patient explicitly triggered emergency alert (is_emergency=True)
        all_cases = Consultation.query.filter_by(is_emergency=True).order_by(Consultation.created_at.desc()).all()
        
        # Filter emergency cases based on status within the emergency-only cases
        emergency_cases = [c for c in all_cases if c.status == 'pending']  # Active emergencies
        pending_cases = [c for c in all_cases if c.status == 'pending']  # Same as emergency for now
        resolved_cases = [c for c in all_cases if c.status in ['completed', 'reviewed']]
        
        return render_template('hospital_dashboard.html', 
                             all_cases=all_cases,
                             emergency_cases=emergency_cases, 
                             pending_cases=pending_cases,
                             resolved_cases=resolved_cases,
                             get_severity=get_severity_classification)
    
    return redirect(url_for('index'))

@app.route('/view_consultation/<int:consultation_id>')
@login_required
def view_consultation(consultation_id):
    """View AI consultation details"""
    if current_user.user_type != 'patient':
        return jsonify({'error': 'Access denied'}), 403
    
    consultation = Consultation.query.get_or_404(consultation_id)
    
    # Ensure user can only view their own consultations
    if consultation.patient_id != current_user.id:
        return jsonify({'error': 'Access denied'}), 403
    
    # Parse AI response
    try:
        ai_response = json.loads(consultation.ai_response) if consultation.ai_response else {}
    except:
        ai_response = {}
    
    # Check if appointment exists for this consultation
    appointment = Appointment.query.filter_by(consultation_id=consultation_id).first()
    
    return jsonify({
        'id': consultation.id,
        'symptoms': consultation.symptoms,
        'duration': consultation.duration,
        'pain_level': consultation.pain_level,
        'severity': get_severity_classification(consultation.pain_level),
        'created_at': consultation.created_at.strftime('%Y-%m-%d %H:%M'),
        'is_emergency': consultation.is_emergency,
        'status': consultation.status,
        'ai_response': ai_response,
        'has_appointment': appointment is not None,
        'appointment': {
            'id': appointment.id,
            'date': appointment.appointment_date.strftime('%Y-%m-%d %H:%M') if appointment.appointment_date else None,
            'slot': appointment.appointment_slot,
            'type': appointment.appointment_type,
            'status': appointment.status,
            'doctor_name': f"Dr. {appointment.doctor.first_name} {appointment.doctor.last_name}" if appointment.doctor.first_name else appointment.doctor.username
        } if appointment else None
    })

@app.route('/symptom_input')
@login_required
def symptom_input():
    if current_user.user_type != 'patient':
        flash('Access denied')
        return redirect(url_for('dashboard'))
    return render_template('symptom_input.html')

@app.route('/submit_symptoms', methods=['POST'])
@login_required
def submit_symptoms():
    if current_user.user_type != 'patient':
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        symptoms_text = request.json.get('symptoms', '')
        severity = request.json.get('severity', 5)  # Default to 5 if not provided
        
        # Analyze symptoms with severity
        analysis = analyze_symptoms(symptoms_text, severity)
        
        # Ensure we have a valid analysis object
        if not isinstance(analysis, dict):
            raise ValueError("Invalid analysis result")
        
        # Save consultation record with expanded analysis
        is_emergency = severity >= 9 or analysis.get('urgency') == 'high' or bool(analysis.get('red_flags', []))
        
        consultation = Consultation(
            patient_id=current_user.id,
            symptoms=symptoms_text,
            duration=analysis.get('duration', 'unknown'),
            pain_level=severity,  # Use the provided severity
            ai_response=json.dumps(analysis),  # Store the full analysis
            is_emergency=is_emergency
        )
        
        db.session.add(consultation)
        db.session.commit()
        
        # Auto-trigger emergency alert if severity >= 9
        if severity >= 9:
            # Get patient's preferred hospitals
            preferred_hospitals = []
            if current_user.preferred_hospitals:
                try:
                    preferred_hospitals = json.loads(current_user.preferred_hospitals)
                except:
                    pass
            if current_user.preferred_hospital:
                preferred_hospitals.append(current_user.preferred_hospital)
            
            print(f"🚨 EMERGENCY ALERT AUTO-TRIGGERED 🚨")
            print(f"Patient: {current_user.username} (ID: {current_user.id})")
            print(f"Pain Level: {severity}/10")
            print(f"Symptoms: {symptoms_text}")
            print(f"Notifying Preferred Hospitals: {preferred_hospitals}")
            print(f"Notifying All Hospitals in System")
        
        return jsonify({
            'analysis': analysis,
            'consultation_id': consultation.id,
            'emergency_triggered': severity >= 9
        })
    
    except Exception as e:
        print(f"Error in submit_symptoms: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

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

@app.route('/update_analysis', methods=['POST'])
@login_required
def update_analysis():
    if current_user.user_type != 'patient':
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        symptoms_data = request.json.get('symptoms', [])
        
        # Format symptoms for analysis
        symptoms_text = '. '.join([
            f"{s['symptom']} (Severity: {s['severity']}/10)"
            for s in symptoms_data
        ])
        
        # Calculate overall severity
        overall_severity = sum(s['severity'] for s in symptoms_data) // len(symptoms_data) if symptoms_data else 5
        
        # Get updated analysis
        analysis = analyze_symptoms(symptoms_text, overall_severity)
        
        # Update consultation if it exists
        consultation_id = request.json.get('consultation_id')
        if consultation_id:
            consultation = Consultation.query.get(consultation_id)
            if consultation and consultation.patient_id == current_user.id:
                consultation.pain_level = overall_severity
                consultation.ai_response = json.dumps(analysis)
                db.session.commit()
        
        return jsonify({'analysis': analysis})
    
    except Exception as e:
        print(f"Error in update_analysis: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/trigger_emergency', methods=['POST'])
@login_required
def trigger_emergency():
    if current_user.user_type != 'patient':
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        # Get emergency details from request (could be JSON or form data or empty)
        data = request.get_json(silent=True) or {}
        symptoms = data.get('symptoms', 'EMERGENCY ALERT TRIGGERED BY PATIENT')
        
        # Create AI response in JSON format
        ai_emergency_response = {
            'diagnosis': 'Emergency alert triggered by patient',
            'recommendations': 'Emergency services have been notified. Stay calm and wait for medical assistance.',
            'urgency': 'high',
            'possible_conditions': ['Emergency situation requiring immediate medical attention'],
            'red_flags': ['Patient has triggered emergency alert button']
        }
        
        # Create emergency consultation
        consultation = Consultation(
            patient_id=current_user.id,
            symptoms=symptoms,
            duration="immediate",
            pain_level=10,
            ai_response=json.dumps(ai_emergency_response),
            is_emergency=True,
            status='pending'
        )
        
        db.session.add(consultation)
        db.session.commit()
        
        # Get patient's preferred hospitals
        preferred_hospitals = []
        if current_user.preferred_hospitals:
            try:
                preferred_hospitals = json.loads(current_user.preferred_hospitals)
            except:
                pass
        if current_user.preferred_hospital:
            preferred_hospitals.append(current_user.preferred_hospital)
        
        # In production, this would send actual notifications to hospitals
        # For now, we just log which hospitals should be notified
        print(f"🚨 EMERGENCY ALERT TRIGGERED 🚨")
        print(f"Patient: {current_user.username} (ID: {current_user.id})")
        print(f"Contact: {current_user.phone_number or 'Not provided'}")
        print(f"Address: {current_user.address or 'Not provided'}")
        print(f"Emergency Contact: {current_user.emergency_contact_name} - {current_user.emergency_contact_phone}" if current_user.emergency_contact_name else "No emergency contact")
        print(f"Preferred Hospitals to notify: {preferred_hospitals}")
        print(f"All hospitals in system will also be notified")
        
        return jsonify({
            'success': True, 
            'message': 'Emergency alert sent to all nearby and preferred hospitals',
            'hospitals_notified': len(preferred_hospitals) if preferred_hospitals else 'all',
            'consultation_id': consultation.id
        })
    
    except Exception as e:
        print(f"Error in trigger_emergency: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e), 'success': False}), 500

@app.route('/update_case_status', methods=['POST'])
@login_required
def update_case_status():
    if current_user.user_type not in ['doctor', 'hospital']:
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        case_id = request.json.get('case_id')
        new_status = request.json.get('status')
        
        if not case_id or not new_status:
            return jsonify({'error': 'Missing required parameters'}), 400
        
        consultation = Consultation.query.get(case_id)
        if not consultation:
            return jsonify({'error': 'Case not found'}), 404
        
        old_status = consultation.status
        consultation.status = new_status
        if current_user.user_type == 'doctor':
            consultation.doctor_id = current_user.id
        
        # Also update associated appointments if marking as completed
        updated_appointments = []
        if new_status == 'completed':
            appointments = Appointment.query.filter_by(consultation_id=case_id).all()
            for appt in appointments:
                appt.status = 'completed'
                updated_appointments.append(appt.id)
        
        db.session.commit()
        
        # Debug logging
        print(f"✅ Case status updated:")
        print(f"  Consultation ID: {case_id}")
        print(f"  Old status: {old_status}")
        print(f"  New status: {new_status}")
        print(f"  Doctor ID: {consultation.doctor_id}")
        print(f"  Updated appointments: {updated_appointments}")
        
        return jsonify({'success': True, 'message': f'Case status updated to {new_status}'})
    
    except Exception as e:
        print(f"Error in update_case_status: {e}")
        traceback.print_exc()
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/update_appointment_status', methods=['POST'])
@login_required
def update_appointment_status():
    if current_user.user_type != 'doctor':
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        appointment_id = request.json.get('appointment_id')
        new_status = request.json.get('status')
        
        if not appointment_id or not new_status:
            return jsonify({'error': 'Missing required parameters'}), 400
        
        appointment = Appointment.query.get(appointment_id)
        if not appointment:
            return jsonify({'error': 'Appointment not found'}), 404
        
        # Verify doctor owns this appointment
        if appointment.doctor_id != current_user.id:
            return jsonify({'error': 'Access denied'}), 403
        
        appointment.status = new_status
        db.session.commit()
        
        return jsonify({'success': True, 'message': f'Appointment status updated to {new_status}'})
    
    except Exception as e:
        print(f"Error in update_appointment_status: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/hospitals')
def get_hospitals():
    """Get list of registered hospitals for patient registration"""
    hospitals = User.query.filter_by(user_type='hospital').all()
    hospital_list = [{'id': h.id, 'name': h.hospital_name} for h in hospitals if h.hospital_name]
    return jsonify(hospital_list)

# Helper function for severity classification
def get_severity_classification(pain_level):
    """Return proper severity classification"""
    if pain_level >= 9:
        return "Emergency"
    elif pain_level >= 7:
        return "High Risk"
    elif pain_level >= 4:
        return "Moderate Risk"
    else:
        return "Mild Risk"

# Pharmacy data (hardcoded for MVP)
PHARMACIES = [
    {"name": "Apollo Pharmacy", "address": "123 Main Street, Downtown", "phone": "+91 98765 43210", "distance": "0.5 km"},
    {"name": "MedPlus", "address": "456 Park Avenue, City Center", "phone": "+91 98765 43211", "distance": "1.2 km"},
    {"name": "HealthCare Pharmacy", "address": "789 Hospital Road, Medical District", "phone": "+91 98765 43212", "distance": "2.0 km"}
]

@app.route('/get_doctors', methods=['GET'])
@login_required
def get_doctors():
    """Get list of available doctors"""
    doctors = User.query.filter_by(user_type='doctor').all()
    return jsonify([{
        'id': d.id,
        'name': f"Dr. {d.first_name} {d.last_name}" if d.first_name and d.last_name else d.username,
        'specialization': d.specialization or 'General Physician',
        'experience': d.years_of_experience or 0,
        'hospital': d.hospital_affiliation or 'Independent Practice',
        'fee': d.consultation_fee or 500
    } for d in doctors])

@app.route('/get_pharmacies', methods=['GET'])
@login_required
def get_pharmacies():
    """Get list of nearby pharmacies"""
    return jsonify(PHARMACIES)

@app.route('/book_appointment', methods=['POST'])
@login_required
def book_appointment():
    """Book an appointment with a doctor"""
    if current_user.user_type != 'patient':
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        data = request.json
        consultation_id = data.get('consultation_id')
        
        appointment = Appointment(
            patient_id=current_user.id,
            doctor_id=data['doctor_id'],
            consultation_id=consultation_id,
            appointment_type=data.get('appointment_type', 'online'),
            appointment_date=datetime.strptime(data['appointment_date'], '%Y-%m-%d'),
            appointment_slot=data['appointment_slot']
        )
        
        db.session.add(appointment)
        
        # Update consultation status to 'reviewed' if consultation_id is provided
        if consultation_id:
            consultation = Consultation.query.get(consultation_id)
            if consultation and consultation.patient_id == current_user.id:
                consultation.status = 'reviewed'
                consultation.doctor_id = data['doctor_id']
        
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Appointment booked successfully', 'appointment_id': appointment.id})
    except Exception as e:
        print(f"Error booking appointment: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/view_patient/<int:patient_id>')
@login_required
def view_patient(patient_id):
    """View detailed patient information (for doctors/hospitals)"""
    if current_user.user_type not in ['doctor', 'hospital']:
        flash('Access denied')
        return redirect(url_for('dashboard'))
    
    patient = User.query.get_or_404(patient_id)
    if patient.user_type != 'patient':
        flash('Invalid patient ID')
        return redirect(url_for('dashboard'))
    
    consultations = Consultation.query.filter_by(patient_id=patient_id).order_by(Consultation.created_at.desc()).all()
    health_records = HealthRecord.query.filter_by(patient_id=patient_id).order_by(HealthRecord.uploaded_at.desc()).all()
    
    age = None
    if patient.date_of_birth:
        today = datetime.today()
        age = today.year - patient.date_of_birth.year - ((today.month, today.day) < (patient.date_of_birth.month, patient.date_of_birth.day))
    
    return render_template('view_patient.html', patient=patient, consultations=consultations, health_records=health_records, age=age)

@app.route('/doctor_schedule')
@login_required
def doctor_schedule():
    """View doctor's schedule"""
    if current_user.user_type != 'doctor':
        flash('Access denied')
        return redirect(url_for('dashboard'))
    
    appointments = Appointment.query.filter_by(doctor_id=current_user.id).order_by(Appointment.appointment_date).all()
    return render_template('doctor_schedule.html', appointments=appointments)

@app.route('/view_health_record/<int:record_id>')
@login_required
def view_health_record(record_id):
    """View or download a health record"""
    if current_user.user_type not in ['patient', 'doctor', 'hospital']:
        flash('Access denied')
        return redirect(url_for('dashboard'))
    
    record = HealthRecord.query.get_or_404(record_id)
    
    # Check permissions
    if current_user.user_type == 'patient' and record.patient_id != current_user.id:
        flash('Access denied')
        return redirect(url_for('dashboard'))
    
    # For doctors/hospitals, they can view any patient's records they're treating
    if current_user.user_type in ['doctor', 'hospital']:
        # In production, add proper authorization check
        pass
    
    # If file exists, serve it
    if record.file_path and os.path.exists(record.file_path):
        return send_file(record.file_path, as_attachment=False)
    else:
        flash('File not found')
        return redirect(url_for('health_records'))

@app.route('/download_health_record/<int:record_id>')
@login_required
def download_health_record(record_id):
    """Download a health record"""
    if current_user.user_type not in ['patient', 'doctor', 'hospital']:
        flash('Access denied')
        return redirect(url_for('dashboard'))
    
    record = HealthRecord.query.get_or_404(record_id)
    
    # Check permissions
    if current_user.user_type == 'patient' and record.patient_id != current_user.id:
        flash('Access denied')
        return redirect(url_for('dashboard'))
    
    if record.file_path and os.path.exists(record.file_path):
        return send_file(record.file_path, as_attachment=True, download_name=f"{record.title}.{record.file_type}")
    else:
        flash('File not found')
        return redirect(url_for('health_records'))

@app.route('/suggest_doctors', methods=['POST'])
@login_required
def suggest_doctors():
    """Use AI to suggest doctors based on symptoms"""
    if current_user.user_type != 'patient':
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        data = request.json
        symptoms = data.get('symptoms', '')
        consultation_id = data.get('consultation_id')
        
        # Get the consultation to extract symptoms and AI analysis
        if consultation_id:
            consultation = Consultation.query.get(consultation_id)
            if consultation:
                symptoms = consultation.symptoms
                try:
                    ai_analysis = json.loads(consultation.ai_response)
                    possible_conditions = ai_analysis.get('possible_conditions', [])
                except:
                    possible_conditions = []
        
        # Use Gemini AI to suggest specialization
        if model:
            prompt = f"""Based on these symptoms: {symptoms}
            
Suggest the most appropriate medical specialization needed (choose from: General Physician, Cardiologist, Neurologist, Orthopedic, Dermatologist, ENT Specialist, Pediatrician, Gynecologist, Psychiatrist, Gastroenterologist).

Respond with ONLY the specialization name, nothing else."""
            
            response = model.generate_content(prompt)
            suggested_specialization = response.text.strip()
        else:
            suggested_specialization = "General Physician"
        
        # Get doctors, prioritize those with matching specialization
        all_doctors = User.query.filter_by(user_type='doctor').all()
        
        matching_doctors = []
        other_doctors = []
        
        for d in all_doctors:
            doctor_data = {
                'id': d.id,
                'name': f"Dr. {d.first_name} {d.last_name}" if d.first_name and d.last_name else d.username,
                'specialization': d.specialization or 'General Physician',
                'experience': d.years_of_experience or 0,
                'hospital': d.hospital_affiliation or 'Independent Practice',
                'fee': d.consultation_fee or 500,
                'recommended': False
            }
            
            if d.specialization and suggested_specialization.lower() in d.specialization.lower():
                doctor_data['recommended'] = True
                matching_doctors.append(doctor_data)
            else:
                other_doctors.append(doctor_data)
        
        # Sort by recommended first, then by experience
        matching_doctors.sort(key=lambda x: x['experience'], reverse=True)
        other_doctors.sort(key=lambda x: x['experience'], reverse=True)
        
        return jsonify({
            'suggested_specialization': suggested_specialization,
            'doctors': matching_doctors + other_doctors
        })
        
    except Exception as e:
        print(f"Error in suggest_doctors: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/schedule_consultation')
@login_required
def schedule_consultation():
    """Show appointment booking page"""
    if current_user.user_type != 'patient':
        flash('Access denied')
        return redirect(url_for('dashboard'))
    
    # Get consultation_id from query parameter if provided
    consultation_id = request.args.get('consultation_id', type=int)
    return render_template('book_appointment.html', consultation_id=consultation_id)

@app.route('/order_medicine')
@login_required
def order_medicine():
    """Show medicine ordering page"""
    if current_user.user_type != 'patient':
        flash('Access denied')
        return redirect(url_for('dashboard'))
    return render_template('order_medicine.html')

# Voice Input Routes
@app.route('/upload_audio', methods=['POST'])
@login_required
def upload_audio():
    """Handle voice recording upload, transcribe, and generate AI response"""
    if current_user.user_type != 'patient':
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        if 'audio' not in request.files:
            return jsonify({'error': 'No audio file provided'}), 400
        
        audio_file = request.files['audio']
        
        # Save audio file temporarily
        audio_filename = secure_filename(f'voice_{current_user.id}_{datetime.utcnow().timestamp()}.webm')
        audio_path = os.path.join(app.config['UPLOAD_FOLDER'], audio_filename)
        audio_file.save(audio_path)
        
        # Transcribe audio
        transcription = transcribe_audio(audio_path)
        
        # Get conversation history if provided
        conversation_history_json = request.form.get('conversation_history')
        conversation_history = []
        if conversation_history_json:
            conversation_history = json.loads(conversation_history_json)
        
        # Add user message to history
        conversation_history.append({
            'role': 'user',
            'content': transcription
        })
        
        # Generate AI conversational response
        ai_response = generate_conversational_response(conversation_history)
        
        # Generate TTS audio for AI response
        audio_base64 = generate_tts_audio(ai_response['text'])
        
        # Add AI response to history
        conversation_history.append({
            'role': 'ai',
            'content': ai_response['text']
        })
        
        # Clean up audio file
        try:
            os.remove(audio_path)
            wav_path = audio_path.replace('.webm', '.wav')
            if os.path.exists(wav_path):
                os.remove(wav_path)
        except:
            pass
        
        return jsonify({
            'transcription': transcription,
            'ai_response': {
                'text': ai_response['text'],
                'audio': audio_base64,
                'ready_for_diagnosis': ai_response.get('ready_for_diagnosis', False)
            },
            'conversation_history': conversation_history
        })
    
    except Exception as e:
        print(f"Error in upload_audio: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/finalize_voice_conversation', methods=['POST'])
@login_required
def finalize_voice_conversation():
    """Finalize voice conversation and generate diagnosis"""
    if current_user.user_type != 'patient':
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        data = request.json
        conversation_history = data.get('conversation_history', [])
        
        if not conversation_history:
            return jsonify({'error': 'No conversation history provided'}), 400
        
        # Analyze conversation for diagnosis
        analysis = analyze_conversation_for_diagnosis(conversation_history)
        
        if not analysis:
            return jsonify({'error': 'Failed to analyze conversation'}), 500
        
        # Extract symptoms text from conversation
        patient_messages = [msg['content'] for msg in conversation_history if msg['role'] == 'user']
        symptoms_text = " ".join(patient_messages)
        
        # Calculate overall severity from identified symptoms
        overall_severity = 5
        if analysis.get('default_severities'):
            severities = analysis['default_severities']
            overall_severity = sum(severities) // len(severities) if severities else 5
        
        # Save consultation to database
        consultation = Consultation(
            patient_id=current_user.id,
            symptoms=symptoms_text,
            duration=analysis.get('duration', 'unknown'),
            pain_level=overall_severity,
            ai_response=json.dumps(analysis),
            is_emergency=(analysis.get('urgency', 'medium').lower() == 'high')
        )
        db.session.add(consultation)
        db.session.commit()
        
        return jsonify({
            'analysis': analysis,
            'consultation_id': consultation.id
        })
    
    except Exception as e:
        print(f"Error in finalize_voice_conversation: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/update_patient_profile', methods=['POST'])
@login_required
def update_patient_profile():
    if current_user.user_type != 'patient':
        flash('Access denied')
        return redirect(url_for('dashboard'))
    
    try:
        # Update patient profile information
        current_user.blood_group = request.form.get('blood_group', '')
        current_user.allergies = request.form.get('allergies', '')
        current_user.current_medications = request.form.get('medications', '')
        
        # Update preferred hospitals if provided
        preferred_hospitals_input = request.form.get('preferred_hospitals', '')
        if preferred_hospitals_input:
            # Split by comma and clean up
            hospitals_list = [h.strip() for h in preferred_hospitals_input.split(',') if h.strip()]
            current_user.preferred_hospitals = json.dumps(hospitals_list)
        
        db.session.commit()
        flash('Profile updated successfully!')
        
    except Exception as e:
        print(f"Error updating profile: {e}")
        import traceback
        traceback.print_exc()
        flash('Error updating profile')
    
    return redirect(url_for('health_records'))

# Initialize database
def create_tables():
    db.create_all()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)
