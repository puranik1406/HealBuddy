# 🏥 HealBuddy - AI-Powered Healthcare Platform

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-2.3.3-green.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

HealBuddy is a comprehensive full-stack healthcare platform that leverages AI to provide intelligent symptom analysis, voice interaction, appointment booking, and emergency management. Built with Flask and powered by Google's Gemini AI.

Check out the deployed app [HealBuddy]-(https://healbuddy-74m1.onrender.com/)

## ✨ Key Features

### 🎤 Voice Interaction System
- **Speech-to-Text**: Real-time voice input using Google Speech Recognition
- **AI Conversation**: Natural dialogue with follow-up questions
- **Text-to-Speech**: Voice responses using gTTS
- **Hands-free Operation**: Complete voice-driven symptom reporting

### 🤖 AI-Powered Analysis
- **Symptom Analysis**: Intelligent evaluation using Gemini 2.5 Flash
- **Severity Assessment**: Automatic pain level classification (1-10 scale)
- **Condition Prediction**: Possible conditions based on symptoms
- **Treatment Recommendations**: Personalized health advice
- **Emergency Detection**: Automatic alert for critical cases

### 👥 Multi-Role Dashboard System

#### **Patient Features**
- Voice & text symptom input
- Consultation history with AI analysis
- Appointment booking with doctors
- Health records management
- Emergency alert system
- Medicine ordering
- Profile management with gender, blood group, allergies

#### **Doctor Features**
- Patient consultation dashboard
- Active & completed cases tracking
- Appointment management
- Patient medical history access
- Case status updates
- Schedule management

#### **Hospital Features**
- Emergency case monitoring
- Real-time patient alerts
- Critical case tracking
- Patient information access

### 📅 Appointment System
- Doctor search and selection
- Date & time slot booking
- Online/in-person consultation options
- Appointment status tracking
- Automatic consultation linking

### 🚨 Emergency Management
- Automatic emergency detection (pain ≥ 9/10)
- Instant hospital notifications
- Critical case prioritization
- Emergency contact alerts

## 🛠️ Technology Stack

### Backend
- **Framework**: Flask 2.3.3
- **Database**: SQLAlchemy ORM with SQLite (development)
- **Authentication**: Flask-Login
- **AI Integration**: Google Gemini 2.5 Flash
- **Voice Processing**: 
  - Speech Recognition (Google)
  - gTTS (Google Text-to-Speech)
  - pydub (Audio processing)

### Frontend
- **HTML5/CSS3**: Modern responsive design
- **JavaScript**: Vanilla JS for interactivity
- **Bootstrap 5**: UI framework
- **Font Awesome**: Icon library

### APIs & Services
- **Google Gemini AI**: Symptom analysis and recommendations
- **Google Speech Recognition**: Voice transcription
- **Google Text-to-Speech**: Voice responses

## 📋 System Requirements

- Python 3.8 or higher
- pip (Python package manager)
- FFmpeg (for audio processing)
- Modern web browser with microphone support
- Internet connection (for AI services)

## 🚀 Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/puranik1406/HealBuddy.git
cd HealBuddy
```

### 2. Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 4. Install FFmpeg

**Windows (using Chocolatey):**
```powershell
choco install ffmpeg
```

**Windows (Manual):**
1. Download from [ffmpeg.org](https://ffmpeg.org/download.html)
2. Extract to `C:\ffmpeg`
3. Add `C:\ffmpeg\bin` to system PATH

**macOS:**
```bash
brew install ffmpeg
```

**Linux:**
```bash
sudo apt-get install ffmpeg  # Ubuntu/Debian
```

### 5. Configure Environment Variables

Create a `.env` file in the root directory:

```env
# Google Gemini AI API Key
GEMINI_API_KEY=your_gemini_api_key_here

# Flask Configuration
FLASK_SECRET_KEY=your_secret_key_here
FLASK_ENV=development

# Database Configuration
DATABASE_URL=sqlite:///healbuddy.db
```

**Get Gemini API Key:**
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with Google account
3. Create API key
4. Copy to `.env` file

### 6. Initialize Database
```bash
python create_database.py
```

### 7. Run the Application
```bash
python app.py
```

Access the application at: **http://localhost:5000**

## 📁 Project Structure

```
HealBuddy/
├── app.py                          # Main Flask application
├── create_database.py              # Database initialization
├── requirements.txt                # Python dependencies
├── .env                           # Environment variables (not in repo)
├── .gitignore                     # Git ignore rules
├── README.md                      # Documentation
│
├── templates/                     # HTML Templates
│   ├── base.html                  # Base template
│   ├── index.html                 # Landing page
│   ├── login.html                 # Login page
│   ├── register.html              # Registration
│   ├── symptom_input.html         # Voice/text input
│   ├── patient_dashboard.html     # Patient dashboard
│   ├── doctor_dashboard.html      # Doctor dashboard
│   ├── hospital_dashboard.html    # Hospital dashboard
│   ├── book_appointment.html      # Appointment booking
│   ├── health_records.html        # Health records
│   ├── emergency_alert.html       # Emergency alerts
│   └── view_patient.html          # Patient details
│
├── static/                        # Static Assets
│   ├── css/
│   │   └── style.css             # Custom styles
│   └── js/
│       ├── main.js               # Main JavaScript
│       └── symptom_input.js      # Symptom input logic
│
├── uploads/                       # File uploads (created automatically)
└── instance/                      # Instance-specific files
    └── healbuddy.db              # SQLite database
```

## 🎯 Usage Guide

### Patient Workflow

#### 1. **Registration**
- Navigate to home page
- Click "Register as Patient"
- Fill in personal information:
  - Basic info (username, email, password)
  - Personal details (name, gender, date of birth)
  - Health info (height, weight, blood group)
  - Medical history (allergies, conditions, medications)
  - Emergency contact

#### 2. **Symptom Input (Voice)**
- Click "Talk to HealBuddy" from dashboard
- Click "Start Recording" button
- Speak symptoms clearly
- AI asks follow-up questions
- Continue conversation or get diagnosis
- View detailed analysis with:
  - Identified symptoms with severity
  - Urgency level
  - Possible conditions
  - Recommendations
  - Suggested medications
  - Red flags/warnings

#### 3. **Symptom Input (Text)**
- Enter symptoms in text box
- Set pain level (1-10)
- Submit for analysis
- Receive AI recommendations

#### 4. **Book Appointment**
- From consultation results, click "Consult Doctor"
- Select doctor by specialization
- Choose date and time slot
- Select consultation type (online/in-person)
- Confirm booking
- View appointment in dashboard

#### 5. **Health Records**
- Upload medical documents (PDF, images, Word)
- View previous consultations
- Update profile information
- Manage allergies and medications

#### 6. **Emergency Alert**
- Automatic trigger for pain ≥ 9/10
- Manual emergency button available
- Hospitals notified instantly
- Emergency contact alerted

### Doctor Workflow

#### 1. **Dashboard Overview**
- View active cases count
- View completed cases count
- See upcoming appointments
- Access patient consultations

#### 2. **Review Cases**
- Click on patient consultation
- View AI-generated analysis
- Review patient medical history
- Check symptoms and severity

#### 3. **Manage Appointments**
- View scheduled appointments
- Check patient details
- Mark consultations as complete
- Update case status

#### 4. **Patient Information**
- Access full patient profile
- View medical history
- Check health records
- Review previous consultations

### Hospital Workflow

#### 1. **Emergency Monitoring**
- View all emergency alerts
- See critical cases first
- Access patient information
- Monitor pending cases

#### 2. **Case Management**
- Review emergency details
- Update case status
- Track resolved cases

## 🔧 Configuration

### Database Models

#### User
- Basic authentication (username, email, password)
- Personal info (name, gender, DOB, phone, address)
- Patient-specific (height, weight, blood group, allergies)
- Doctor-specific (license, degree, specialization, fees)
- Hospital-specific (name, beds, emergency services)

#### Consultation
- Patient ID
- Symptoms description
- Duration and pain level
- AI analysis response
- Status (pending, reviewed, completed)
- Emergency flag
- Linked doctor ID

#### Appointment
- Patient and doctor IDs
- Consultation ID (linked)
- Date and time slot
- Appointment type
- Status tracking

#### HealthRecord
- Patient ID
- File information
- Upload timestamp

### AI Prompt Engineering

The system uses carefully crafted prompts for Gemini AI:
- Structured JSON output
- Medical terminology
- Severity assessment
- Urgency classification
- Treatment recommendations
- Red flag identification

## 🔒 Security Features

- **Password Hashing**: Werkzeug secure password hashing
- **Session Management**: Flask-Login for secure sessions
- **CSRF Protection**: Flask-WTF forms
- **SQL Injection Protection**: SQLAlchemy ORM
- **File Validation**: Type and size checking
- **Environment Variables**: Sensitive data protection
- **User Role Isolation**: Access control per user type

## 🌐 API Endpoints

### Authentication
```
GET  /                  - Landing page
GET  /login             - Login page
POST /login             - Login authentication
GET  /register          - Registration page
POST /register          - User registration
GET  /logout            - Logout user
```

### Patient Endpoints
```
GET  /dashboard                      - Patient dashboard
GET  /symptom_input                  - Symptom input page
POST /upload_audio                   - Voice input processing
POST /finalize_voice_conversation    - Complete voice session
POST /submit_symptoms                - Text symptom analysis
POST /finalize_analysis              - Final diagnosis
GET  /health_records                 - Health records page
POST /upload_record                  - Upload medical file
GET  /emergency_alert                - Emergency alert page
POST /trigger_emergency              - Trigger emergency
GET  /schedule_consultation          - Appointment booking page
POST /book_appointment               - Book appointment
```

### Doctor Endpoints
```
GET  /dashboard               - Doctor dashboard
GET  /doctor_schedule         - Doctor's schedule
POST /update_case_status      - Update consultation status
POST /update_appointment_status - Update appointment
GET  /view_patient/:id        - Patient details
```

### Hospital Endpoints
```
GET  /dashboard               - Hospital dashboard
POST /update_case_status      - Update emergency case
```

### Utility Endpoints
```
GET  /get_doctors             - List of doctors
GET  /get_pharmacies          - List of pharmacies
GET  /api/hospitals           - List of hospitals
GET  /view_consultation/:id   - Consultation details
```

## 🎨 UI Features

- **Responsive Design**: Mobile-friendly interface
- **Bootstrap 5**: Modern, clean UI
- **Real-time Updates**: Dynamic content loading
- **Loading Indicators**: User feedback for async operations
- **Toast Notifications**: Success/error messages
- **Modal Dialogs**: Interactive popups
- **Voice Indicators**: Recording status visualization
- **Audio Playback**: TTS response player

## 🐛 Troubleshooting

### Microphone Issues
**Problem**: "Error accessing microphone"
**Solutions**:
- Grant browser microphone permissions
- Use HTTPS or localhost
- Check system microphone settings
- Try different browser

### Audio Processing Errors
**Problem**: "Error processing audio"
**Solutions**:
- Verify FFmpeg installation: `ffmpeg -version`
- Check FFmpeg in system PATH
- Ensure uploads folder exists and is writable
- Restart Flask server

### AI API Errors
**Problem**: "Gemini API error"
**Solutions**:
- Verify GEMINI_API_KEY in `.env`
- Check API quota limits
- Test API key at Google AI Studio
- Ensure stable internet connection

### Database Errors
**Problem**: "OperationalError: no such column"
**Solutions**:
- Delete `instance/healbuddy.db`
- Run `python create_database.py`
- Restart application

### Voice Transcription Issues
**Problem**: "Could not understand audio"
**Solutions**:
- Speak clearly and at moderate pace
- Reduce background noise
- Check microphone volume
- Ensure audio quality
- Try recording again

## 🚀 Deployment

### Production Checklist

#### Environment
- [ ] Set `FLASK_ENV=production`
- [ ] Generate strong `FLASK_SECRET_KEY`
- [ ] Set production `DATABASE_URL`
- [ ] Secure API keys

#### Database
- [ ] Migrate to PostgreSQL/MySQL
- [ ] Set up database backups
- [ ] Configure connection pooling

#### Web Server
- [ ] Use Gunicorn or uWSGI
- [ ] Set up reverse proxy (Nginx)
- [ ] Enable HTTPS (required for microphone)
- [ ] Configure static file serving

#### Security
- [ ] Enable HTTPS
- [ ] Set up firewall rules
- [ ] Configure CORS if needed
- [ ] Implement rate limiting
- [ ] Set up logging and monitoring

### Example Deployment (Gunicorn)

```bash
# Install Gunicorn
pip install gunicorn

# Run with 4 workers
gunicorn -w 4 -b 0.0.0.0:8000 app:app

# Run with logging
gunicorn -w 4 -b 0.0.0.0:8000 app:app \
  --access-logfile access.log \
  --error-logfile error.log \
  --log-level info
```

### Cloud Deployment Options

- **Heroku**: Easy deployment with Procfile
- **AWS EC2**: Full control, scalable
- **Google Cloud Run**: Containerized deployment
- **Azure App Service**: Managed platform
- **Digital Ocean**: Simple VPS setup

## 📊 Performance Optimization

- Use database indexing for faster queries
- Implement caching (Redis/Memcached)
- Compress static assets
- Use CDN for static files
- Optimize database queries
- Implement lazy loading
- Use async tasks for heavy operations

## 🧪 Testing

### Manual Testing

1. **User Registration**: Test all user types
2. **Voice Input**: Test microphone access and recording
3. **Symptom Analysis**: Test various symptom inputs
4. **Appointment Booking**: Test full workflow
5. **Emergency Alerts**: Test trigger mechanism
6. **File Uploads**: Test various file types
7. **Dashboard**: Test all role-specific features

### Browser Compatibility

Tested on:
- Chrome 120+
- Firefox 120+
- Edge 120+
- Safari 17+ (macOS)

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Code Style
- Follow PEP 8 for Python code
- Use meaningful variable names
- Add comments for complex logic
- Write docstrings for functions

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Medical Disclaimer

**IMPORTANT**: HealBuddy is designed for informational and educational purposes only. It is NOT a substitute for professional medical advice, diagnosis, or treatment.

- Always seek the advice of qualified healthcare providers
- Never disregard professional medical advice
- Do not delay seeking medical help based on AI recommendations
- In case of emergency, call emergency services immediately
- The AI analysis should be considered as preliminary guidance only

## 📞 Support & Contact

- **Issues**: [GitHub Issues](https://github.com/puranik1406/HealBuddy/issues)
- **Documentation**: This README and inline code comments
- **Email**: Support through GitHub repository

## 🙏 Acknowledgments

- **Google Gemini AI**: For powering intelligent symptom analysis
- **Google Speech Recognition**: For voice transcription
- **Flask Community**: For excellent documentation
- **Bootstrap**: For responsive UI components
- **Open Source Community**: For various libraries and tools

## 📈 Roadmap

### Planned Features
- [ ] Multi-language support
- [ ] Mobile app (React Native)
- [ ] Video consultations
- [ ] Prescription management
- [ ] Medicine reminder system
- [ ] Health analytics dashboard
- [ ] Integration with wearables
- [ ] Telemedicine features
- [ ] Payment gateway integration
- [ ] SMS/Email notifications
- [ ] Doctor availability calendar
- [ ] Patient reviews and ratings

### Future Enhancements
- Machine learning for better diagnosis
- Chatbot for quick queries
- Integration with lab test providers
- Insurance claim management
- Family health management
- Chronic disease monitoring


**Built with ❤️ to make healthcare more accessible and intelligent**

**Version**: 1.0.0  
**Last Updated**: October 2025  
**Repository**: [github.com/puranik1406/HealBuddy](https://github.com/puranik1406/HealBuddy)
