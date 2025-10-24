# Voice Input - Quick Setup Guide

## ⚡ Fast Setup (5 Minutes)

### Step 1: Install FFmpeg

**Windows (using Chocolatey):**
```powershell
choco install ffmpeg
```

**Windows (Manual):**
1. Download: https://ffmpeg.org/download.html
2. Extract to `C:\ffmpeg`
3. Add to PATH: `C:\ffmpeg\bin`
4. Restart terminal

**Verify Installation:**
```powershell
ffmpeg -version
```

### Step 2: Install Python Dependencies

All required packages are already in `requirements.txt`. If you need to reinstall:

```powershell
pip install -r requirements.txt
```

Required packages:
- `SpeechRecognition>=3.10.4`
- `gTTS==2.4.0`
- `pydub==0.25.1`

### Step 3: Verify Environment

Check your `.env` file has:
```
GEMINI_API_KEY=your_api_key_here
FLASK_SECRET_KEY=your_secret_key
```

### Step 4: Start the Application

```powershell
cd C:\Users\ishit\HealBuddy
python app.py
```

### Step 5: Test Voice Input

1. Login as a patient
2. Go to **Symptom Input** page
3. Click **"Start Recording"** button
4. Allow microphone permission
5. Speak: *"I have a headache and fever"*
6. Click **"Stop Recording"**
7. Wait for transcription and AI response
8. Click **"Continue Conversation"** or **"Finish & Get Diagnosis"**

## ✅ What Was Implemented

### Frontend
- ✅ Voice recording UI with recording controls
- ✅ Transcription display
- ✅ Conversation interface
- ✅ Audio playback for AI responses
- ✅ Visual feedback (blinking indicators)

### Backend
- ✅ Speech-to-text transcription
- ✅ Text-to-speech generation
- ✅ Conversational AI logic
- ✅ Follow-up question generation
- ✅ Complete diagnosis from conversation
- ✅ Database integration

### Features
- ✅ Natural voice conversation
- ✅ AI asks follow-up questions
- ✅ Voice responses from AI
- ✅ Context-aware conversation
- ✅ Urgency level assessment
- ✅ Treatment recommendations

## 🎯 How to Use

### Basic Flow:
```
1. Click "Start Recording"
2. Speak symptoms
3. Click "Stop Recording"
4. Listen to AI response
5. Continue or finish conversation
6. Get diagnosis with recommendations
```

### Example Conversation:
```
YOU: "I have a severe headache"
AI: "Can you tell me when it started?"
YOU: "This morning"
AI: "Is it affecting your vision?"
YOU: "Yes, things are blurry"
AI: "I have enough information now."
[Click Finish] → Get Diagnosis
```

## 🚨 Troubleshooting

### Microphone Not Working
- Grant permission in browser
- Use HTTPS or localhost
- Check browser settings

### FFmpeg Error
```powershell
# Check if installed
ffmpeg -version

# Reinstall if needed
choco install ffmpeg
```

### Audio Not Playing
- Check browser audio settings
- Verify volume is not muted
- Try different browser

### Transcription Errors
- Speak clearly
- Reduce background noise
- Check microphone volume

## 📱 Browser Support

Works on:
- Chrome 120+
- Firefox 120+
- Edge 120+
- Safari 17+ (macOS)

Requires:
- Microphone access
- MediaRecorder API support
- HTTPS or localhost

## 🔧 Advanced Configuration

### Change TTS Language
In `app.py`, function `generate_tts_audio()`:
```python
tts = gTTS(text=text, lang='en')  # Change 'en' to desired language
```

### Adjust TTS Speed
```python
tts = gTTS(text=text, lang='en', slow=True)  # Slower speech
```

### Audio Quality
Currently uses:
- Input: WebM (from browser)
- Processing: WAV (for transcription)
- Output: MP3 (for playback)

## 📊 Files Modified

1. **templates/symptom_input.html** - Voice UI added
2. **static/js/symptom_input.js** - Recording logic added
3. **static/css/style.css** - Voice styles added
4. **app.py** - Voice processing functions and routes added

## 🎉 Ready to Test!

Your voice input feature is now complete and ready to use. Try it out:

1. Navigate to: `http://localhost:5000/symptom_input`
2. Click the microphone button
3. Start speaking!

For detailed documentation, see `VOICE_INPUT_FEATURE.md`
