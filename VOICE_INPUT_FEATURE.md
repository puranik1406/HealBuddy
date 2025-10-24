# Voice Input Feature - Complete Implementation Guide

## Overview

The HealBuddy application now includes a comprehensive **Voice Input** feature that allows patients to:
- Speak about their symptoms instead of typing
- Have a conversational interaction with AI
- Receive voice responses from the AI
- Get follow-up questions asked by voice
- Receive diagnosis based on the complete voice conversation

## Features

### ✅ Voice Recording
- Click-to-record interface with visual feedback
- Real-time recording status indicator
- Automatic microphone permission handling

### ✅ Speech-to-Text Transcription
- Converts patient voice to text using Google Speech Recognition
- Displays transcription for verification
- Supports WebM audio format from browser

### ✅ Conversational AI
- AI asks intelligent follow-up questions
- Gathers comprehensive symptom information
- Empathetic and professional responses
- Context-aware conversation flow

### ✅ Text-to-Speech Responses
- AI speaks responses back to the patient
- Uses Google TTS (gTTS) for natural voice
- Automatic audio playback
- Visual feedback during playback

### ✅ Complete Diagnosis
- Analyzes entire conversation history
- Extracts symptoms, severity, duration
- Provides urgency assessment
- Generates treatment recommendations
- Saves consultation to database

## System Requirements

### Python Dependencies
All required packages are already in `requirements.txt`:
```
Flask==2.3.3
google-generativeai==0.3.2
gTTS==2.4.0
SpeechRecognition>=3.10.4
pydub==0.25.1
```

### System Requirements
**FFmpeg** is required for audio format conversion (WebM to WAV):

#### Windows Installation:
1. Download FFmpeg from: https://ffmpeg.org/download.html
2. Extract to `C:\ffmpeg`
3. Add `C:\ffmpeg\bin` to System PATH
4. Verify installation: `ffmpeg -version`

#### Alternative (Chocolatey):
```powershell
choco install ffmpeg
```

#### Linux/Mac:
```bash
# Ubuntu/Debian
sudo apt-get install ffmpeg

# macOS
brew install ffmpeg
```

### Browser Requirements
- Modern browser with MediaRecorder API support
- Microphone access permission
- HTTPS or localhost (required for microphone access)

## File Changes

### Frontend Changes

#### 1. `templates/symptom_input.html`
- Added voice input section with recording controls
- Added transcription display area
- Added conversation interface
- Added audio player for AI responses

#### 2. `static/js/symptom_input.js`
- Added voice recording functions
- Added audio processing logic
- Added conversation management
- Added TTS playback functionality

#### 3. `static/css/style.css`
- Added voice input styles
- Added conversation message styles
- Added blinking recording indicator
- Added audio playing animations

### Backend Changes

#### 1. `app.py` - New Imports
```python
import speech_recognition as sr
from gtts import gTTS
from pydub import AudioSegment
import io
import base64
```

#### 2. `app.py` - New Functions
- `transcribe_audio(audio_file_path)` - Speech-to-text conversion
- `generate_tts_audio(text)` - Text-to-speech generation
- `generate_conversational_response(conversation_history)` - AI conversation
- `analyze_conversation_for_diagnosis(conversation_history)` - Final analysis

#### 3. `app.py` - New Routes
- `POST /upload_audio` - Process voice recordings
- `POST /finalize_voice_conversation` - Generate final diagnosis

## Usage Flow

### Step 1: Start Recording
```
Patient clicks "Start Recording" button
→ Browser requests microphone permission
→ Recording indicator appears (blinking red dot)
→ Patient speaks symptoms
```

### Step 2: Stop Recording
```
Patient clicks "Stop Recording"
→ Audio uploaded to server
→ Transcription displayed
→ AI processes and responds
```

### Step 3: AI Conversation
```
AI Response displayed in conversation panel
→ AI asks follow-up question
→ Audio response plays automatically
→ Patient clicks "Continue Conversation" to respond
```

### Step 4: Continue or Finish
```
Option 1: Continue Conversation
→ Record another message
→ AI asks more questions

Option 2: Finish & Get Diagnosis
→ AI analyzes complete conversation
→ Displays results section with:
  - Identified symptoms
  - Urgency level
  - Possible conditions
  - Recommendations
  - Treatment options
```

## Example Conversation

**Patient (speaks):**
> "I have a severe headache and feel nauseous"

**AI Response (text + voice):**
> "I understand you're experiencing a severe headache and nausea. Can you tell me when these symptoms started and if anything makes them better or worse?"

**Patient (speaks):**
> "It started this morning, and bright lights make it worse"

**AI Response (text + voice):**
> "Thank you for that information. Have you experienced any visual disturbances like blurry vision or seeing spots?"

**Patient (speaks):**
> "Yes, I see some flashing lights"

**AI Response (text + voice):**
> "I have enough information now. Let me analyze your symptoms."

**[Patient clicks "Finish & Get Diagnosis"]**

**Diagnosis Display:**
- **Urgency:** High
- **Identified Symptoms:** Severe headache (8/10), Nausea (6/10), Light sensitivity (7/10), Visual disturbances (7/10)
- **Possible Conditions:** Migraine headache, Cluster headache
- **Recommendation:** Book doctor consultation immediately
- **Action Button:** [Book Doctor Consultation]

## API Endpoints

### POST /upload_audio
**Purpose:** Process voice recording and generate AI response

**Request:**
- Content-Type: multipart/form-data
- Body:
  - `audio`: Audio file (WebM format)
  - `conversation_history`: JSON string (optional)

**Response:**
```json
{
  "transcription": "patient's spoken text",
  "ai_response": {
    "text": "AI conversational response",
    "audio": "base64_encoded_mp3",
    "ready_for_diagnosis": false
  },
  "conversation_history": [...]
}
```

### POST /finalize_voice_conversation
**Purpose:** Generate final diagnosis from conversation

**Request:**
- Content-Type: application/json
- Body:
```json
{
  "conversation_history": [
    {"role": "user", "content": "..."},
    {"role": "ai", "content": "..."}
  ]
}
```

**Response:**
```json
{
  "analysis": {
    "identified_symptoms": [...],
    "urgency": "high",
    "possible_conditions": [...],
    "diagnosis": "...",
    "recommendations": "..."
  },
  "consultation_id": 123
}
```

## Technical Details

### Audio Processing Pipeline
```
1. Browser captures audio (WebM)
   ↓
2. Upload to Flask server
   ↓
3. pydub converts WebM → WAV
   ↓
4. SpeechRecognition transcribes WAV → Text
   ↓
5. Text sent to Gemini AI
   ↓
6. AI generates response text
   ↓
7. gTTS converts text → MP3
   ↓
8. MP3 encoded to base64
   ↓
9. Sent to browser
   ↓
10. Browser decodes and plays audio
```

### Conversation State Management
- Conversation history stored in frontend JavaScript
- Each message includes role (user/ai) and content
- History passed with each audio upload for context
- Final diagnosis uses complete history

### Security Considerations
- Login required for all voice endpoints
- Audio files cleaned up after processing
- Temporary files use secure filenames
- Patient ID included in filename for isolation

## Troubleshooting

### Issue: "Error accessing microphone"
**Solution:**
- Grant microphone permission in browser
- Use HTTPS or localhost
- Check browser microphone settings

### Issue: "Error processing audio"
**Solution:**
- Ensure FFmpeg is installed and in PATH
- Check audio file is valid WebM format
- Verify uploads folder has write permissions

### Issue: "Could not understand audio"
**Solution:**
- Speak clearly and at moderate pace
- Reduce background noise
- Check microphone volume levels
- Try recording again

### Issue: "TTS audio not playing"
**Solution:**
- Check browser audio/volume settings
- Verify base64 audio is being received
- Check browser console for errors
- Test with different browser

## Benefits

### For Patients
- ✅ Easier than typing (especially for elderly or disabled)
- ✅ Natural conversation flow
- ✅ Immediate audio feedback
- ✅ Hands-free operation
- ✅ More detailed symptom description

### For Healthcare
- ✅ Richer symptom information
- ✅ Better patient engagement
- ✅ Improved accessibility
- ✅ Natural conversation captures nuances
- ✅ Complete conversation history saved

### For AI Accuracy
- ✅ Interactive clarification
- ✅ Follow-up questions improve accuracy
- ✅ Context-aware responses
- ✅ Comprehensive symptom gathering
- ✅ Better urgency assessment

## Future Enhancements

Potential improvements for future versions:
- [ ] Multi-language support
- [ ] Offline mode with local TTS/STT
- [ ] Voice emotion detection
- [ ] Background noise filtering
- [ ] Conversation summaries
- [ ] Voice biometrics for authentication
- [ ] Real-time transcription display
- [ ] Conversation export/sharing

## Configuration

### Environment Variables
No additional environment variables needed. Uses existing:
- `GEMINI_API_KEY` - For AI responses
- `FLASK_SECRET_KEY` - For session management
- `DATABASE_URL` - For storing consultations

### Audio Settings
Can be customized in code:
- TTS language: `gTTS(text=text, lang='en')`
- TTS speed: `gTTS(text=text, slow=False)`
- Audio format: Currently WebM → WAV → MP3

## Testing

### Manual Testing Checklist
- [ ] Click "Start Recording" - microphone permission granted
- [ ] Speak symptoms - recording indicator shows
- [ ] Click "Stop Recording" - transcription appears
- [ ] Verify AI response displays in conversation
- [ ] Check audio response plays automatically
- [ ] Click "Continue Conversation" - can record again
- [ ] Multiple conversation turns work correctly
- [ ] Click "Finish & Get Diagnosis" - results display
- [ ] Results section shows complete analysis
- [ ] Consultation saved to database

### Browser Compatibility
Tested on:
- ✅ Chrome 120+
- ✅ Firefox 120+
- ✅ Edge 120+
- ✅ Safari 17+ (macOS)

## Support

For issues or questions:
1. Check this documentation
2. Review browser console for errors
3. Check Flask server logs
4. Verify FFmpeg installation
5. Test microphone in other applications

## Summary

The voice input feature provides a natural, conversational way for patients to describe symptoms and interact with the AI doctor. It combines:
- Speech recognition
- Conversational AI
- Text-to-speech
- Intelligent follow-up questions
- Comprehensive diagnosis

This creates an accessible, engaging, and effective medical consultation experience.
