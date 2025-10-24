# Voice Input Setup Guide

## Overview
HealBuddy supports voice input for symptom reporting. Patients can speak their symptoms, which will be transcribed to text and analyzed by AI.

## Requirements

### Python Dependencies
All Python dependencies are in `requirements.txt`. The key ones for voice input are:
- `SpeechRecognition>=3.10.4` - Google Speech Recognition API
- `pydub==0.25.1` - Audio format conversion
- `gTTS==2.4.0` - Text-to-speech for AI responses

### System Dependencies

#### FFmpeg (Required)
Pydub requires FFmpeg to convert WebM audio (from browser) to WAV format (for speech recognition).

**Windows:**
1. Download FFmpeg from: https://www.gyan.dev/ffmpeg/builds/
2. Extract the zip file
3. Add the `bin` folder to your System PATH
4. Verify installation: `ffmpeg -version`

**macOS:**
```bash
brew install ffmpeg
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install ffmpeg
```

## How It Works

1. **Recording**: Patient clicks "Start Recording" button
   - Browser requests microphone permission
   - MediaRecorder API captures audio in WebM format
   - Recording auto-stops after 30 seconds or when user clicks "Stop"

2. **Transcription**: Audio is sent to server
   - WebM file is converted to WAV format using pydub/ffmpeg
   - Google Speech Recognition API transcribes the audio
   - Transcription is returned to frontend

3. **Analysis**: Transcribed text is analyzed
   - Text is sent to Gemini AI for symptom analysis
   - AI provides diagnosis, recommendations, and severity assessment
   - Results are displayed to patient with interactive sliders

## Troubleshooting

### "Could not understand the audio"
- Speak more clearly and slowly
- Ensure microphone is working and not muted
- Reduce background noise
- Try text input instead

### "Failed to transcribe audio"
- Check FFmpeg is installed: `ffmpeg -version`
- Verify microphone permissions in browser
- Ensure you're using HTTPS or localhost (required for microphone access)

### "Could not access microphone"
- Grant microphone permission when browser prompts
- Check system microphone settings
- Use HTTPS or localhost (HTTP doesn't support getUserMedia)

### Empty audio blob
- Browser may not support MediaRecorder API (update browser)
- Microphone may be in use by another application

## Browser Compatibility

Voice input requires:
- **getUserMedia API**: Chrome 53+, Firefox 36+, Safari 11+, Edge 79+
- **MediaRecorder API**: Chrome 47+, Firefox 25+, Safari 14.1+, Edge 79+
- **HTTPS or localhost** (required for microphone access)

## Testing

1. Navigate to `/symptom_input` page
2. Click "Start Recording"
3. Grant microphone permission
4. Speak your symptoms clearly: "I have a headache and fever"
5. Click "Stop Recording"
6. Wait for transcription and analysis
7. Review AI recommendations

## Fallback

If voice input doesn't work, patients can always use the text input option on the same page.
