# HealBuddy - AI-Powered Health Assistant

HealBuddy is a comprehensive full-stack web application that provides AI-powered health assistance through voice interaction, symptom analysis, and medical record management. Built with Flask and integrated with Google's Gemini AI.

## 🚀 Features

### Core Functionalities
- **Voice Interaction**: Speak symptoms directly to HealBuddy using Google Speech Recognition
- **AI Symptom Analysis**: Intelligent analysis using Gemini 1.5 Flash for structured medical insights
- **Text-to-Speech**: Natural voice responses using gTTS
- **Health Records Management**: Secure storage and organization of medical documents
- **Emergency Alert System**: Automatic emergency detection and hospital notification
- **Multi-User Support**: Separate dashboards for patients, doctors, and hospitals

### User Roles
- **Patients**: Voice/text symptom input, health record management, emergency alerts
- **Doctors**: Access to AI-generated case summaries and patient consultations
- **Hospitals**: Emergency case monitoring and patient information management

## 🛠 Tech Stack

### Backend
- **Flask**: Python web framework
- **SQLAlchemy**: Database ORM
- **Flask-Login**: User authentication
- **SQLite**: Database (MVP)

### Frontend
- **HTML5/CSS3/JavaScript**: Core frontend technologies
- **Bootstrap 5**: Responsive UI framework
- **Font Awesome**: Icons

### AI Integration
- **Google Speech Recognition**: Speech-to-text transcription
- **Gemini 1.5 Flash**: Symptom analysis and recommendations
- **gTTS**: Text-to-speech responses

## 📁 Project Structure

```
HealBuddy/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── env_template.txt       # Environment variables template
├── README.md             # This file
├── templates/            # HTML templates
│   ├── base.html         # Base template
│   ├── index.html        # Home page
│   ├── login.html        # Login page
│   ├── register.html     # Registration page
│   ├── symptom_input.html # Voice/text input page
│   ├── patient_dashboard.html # Patient dashboard
│   ├── doctor_dashboard.html  # Doctor dashboard
│   ├── hospital_dashboard.html # Hospital dashboard
│   ├── health_records.html    # Health records management
│   └── emergency_alert.html   # Emergency alert page
├── static/               # Static files
│   ├── css/
│   │   └── style.css     # Custom styles
│   └── js/
│       ├── main.js       # Main JavaScript functions
│       └── symptom_input.js # Symptom input page logic
└── uploads/              # File upload directory (created automatically)
```

## 🚀 Installation & Setup

### Prerequisites
- Python 3.8 or higher
- Google Gemini API key
- Git (optional)

### Step 1: Clone the Repository
```bash
git clone <repository-url>
cd HealBuddy
```

### Step 2: Create Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Environment Configuration
1. Copy the environment template:
   ```bash
   cp env_template.txt .env
   ```

2. Edit `.env` file and add your API keys:
   ```env
   # Gemini AI API Configuration
   GEMINI_API_KEY=your_gemini_api_key_here
   
   # Flask Configuration
   FLASK_SECRET_KEY=your_secret_key_here
   FLASK_ENV=development
   
   # Database Configuration
   DATABASE_URL=sqlite:///healbuddy.db
   ```

### Step 5: Run the Application
```bash
python app.py
```

The application will be available at `http://localhost:5000`

## 🔧 Configuration

### Gemini API Setup
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create or sign in to your Google account
3. Generate an API key
4. Add the key to your `.env` file

### Database Configuration
- Default: SQLite database (`healbuddy.db`)
- For production: Update `DATABASE_URL` in `.env` to use PostgreSQL or MySQL

### File Upload Configuration
- Maximum file size: 16MB
- Supported formats: PDF, Images (JPG, PNG), Word documents, Text files
- Upload directory: `uploads/` (created automatically)

## 🎯 Usage Guide

### For Patients
1. **Register** as a patient
2. **Login** to access your dashboard
3. **Talk to HealBuddy**:
   - Click "Talk to HealBuddy" button
   - Use voice input (microphone) or text input
   - Receive AI analysis and recommendations
4. **Manage Health Records**:
   - Upload medical documents
   - Update personal health information
5. **Emergency Alerts**:
   - Use emergency button for critical situations
   - Automatic hospital notification

### For Doctors
1. **Register** as a doctor
2. **Login** to access doctor dashboard
3. **Review Cases**:
   - View AI-generated case summaries
   - Access patient consultation history
   - Update case status

### For Hospitals
1. **Register** as a hospital
2. **Login** to access hospital dashboard
3. **Monitor Emergencies**:
   - View emergency alerts
   - Access patient information
   - Update case status

## 🔒 Security Features

- **Password Hashing**: Secure password storage using Werkzeug
- **Session Management**: Flask-Login for secure user sessions
- **File Validation**: Uploaded files are validated for type and size
- **Environment Variables**: Sensitive data stored in environment variables
- **SQL Injection Protection**: SQLAlchemy ORM prevents SQL injection

## 🧠 AI Integration Details

### Symptom Analysis Flow
1. **Voice Input**: Audio captured via microphone
2. **Transcription**: Google Speech Recognition converts speech to text
3. **Analysis**: Gemini 1.5 Flash analyzes symptoms and provides structured output
4. **Response**: Text-to-speech conversion for audio feedback

### Pain Level Classification
- **1-3**: Mild discomfort → Rest and over-the-counter medication
- **4-5**: Moderate pain → Consider doctor consultation
- **6-8**: Significant pain → Schedule doctor appointment
- **9-10**: Severe pain → Emergency alert triggered

### Emergency Detection
- Pain level ≥ 9
- Urgency level = "high"
- Manual emergency button trigger

## 🐛 Troubleshooting

### Common Issues

1. **Microphone Access Denied**
   - Ensure browser permissions are granted
   - Use HTTPS in production (required for microphone access)

2. **Gemini API Errors**
   - Verify API key is correct
   - Check API quota limits
   - Ensure internet connection

3. **File Upload Issues**
   - Check file size (max 16MB)
   - Verify file format is supported
   - Ensure uploads directory exists

4. **Database Errors**
   - Delete `healbuddy.db` to reset database
   - Check file permissions

### Debug Mode
Run with debug mode for detailed error messages:
```bash
export FLASK_ENV=development
python app.py
```

## 🚀 Deployment

### Production Considerations
1. **Environment Variables**: Set production values in `.env`
2. **Database**: Use PostgreSQL or MySQL for production
3. **Web Server**: Deploy with Gunicorn or similar WSGI server
4. **HTTPS**: Required for microphone access in production
5. **File Storage**: Consider cloud storage for uploaded files

### Example Production Setup
```bash
# Install Gunicorn
pip install gunicorn

# Run with Gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

## 📝 API Endpoints

### Authentication
- `GET /` - Home page
- `GET /login` - Login page
- `POST /login` - User login
- `GET /register` - Registration page
- `POST /register` - User registration
- `GET /logout` - User logout

### Patient Features
- `GET /dashboard` - Patient dashboard
- `GET /symptom_input` - Symptom input page
- `POST /upload_audio` - Voice input processing
- `POST /submit_symptoms` - Text input processing
- `GET /health_records` - Health records page
- `POST /upload_record` - Upload health record
- `GET /emergency_alert` - Emergency alert page
- `POST /trigger_emergency` - Trigger emergency alert

### Doctor/Hospital Features
- `GET /dashboard` - Role-specific dashboard
- Various consultation management endpoints

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## ⚠️ Disclaimer

HealBuddy is designed for informational purposes only and should not replace professional medical advice. Always consult with qualified healthcare professionals for medical concerns.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Check the troubleshooting section
- Review the documentation

---

**Built with ❤️ for better healthcare accessibility**
