// Symptom Input Page JavaScript

document.addEventListener('DOMContentLoaded', function() {
    const recordBtn = document.getElementById('recordBtn');
    const stopBtn = document.getElementById('stopBtn');
    const recordingStatus = document.getElementById('recordingStatus');
    const submitTextBtn = document.getElementById('submitTextBtn');
    const symptomsText = document.getElementById('symptomsText');
    const resultsSection = document.getElementById('resultsSection');
    const emergencyBtn = document.getElementById('emergencyBtn');
    const playAudioBtn = document.getElementById('playAudioBtn');
    const newConsultationBtn = document.getElementById('newConsultationBtn');
    const audioPlayer = document.getElementById('audioPlayer');

    let isRecording = false;
    let currentAudioData = null;

    // Voice Recording Functions
    recordBtn.addEventListener('click', startRecording);
    stopBtn.addEventListener('click', stopRecording);
    
    // Text Input Functions
    submitTextBtn.addEventListener('click', submitTextSymptoms);
    
    // Emergency Functions
    emergencyBtn.addEventListener('click', triggerEmergency);
    
    // Audio Playback Functions
    playAudioBtn.addEventListener('click', playAudioResponse);
    newConsultationBtn.addEventListener('click', resetForm);

    async function startRecording() {
        try {
            // Request microphone permission
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            
            // Update UI
            recordBtn.style.display = 'none';
            stopBtn.style.display = 'inline-block';
            recordingStatus.style.display = 'block';
            
            // Start recording
            const mediaRecorder = new MediaRecorder(stream);
            const audioChunks = [];
            
            mediaRecorder.ondataavailable = (event) => {
                audioChunks.push(event.data);
            };
            
            mediaRecorder.onstop = () => {
                const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                processAudioRecording(audioBlob);
                
                // Stop all tracks
                stream.getTracks().forEach(track => track.stop());
            };
            
            mediaRecorder.start();
            isRecording = true;
            
            // Auto-stop after 30 seconds
            setTimeout(() => {
                if (isRecording) {
                    stopRecording();
                }
            }, 30000);
            
        } catch (error) {
            console.error('Error starting recording:', error);
            HealBuddy.showAlert('Could not access microphone. Please check permissions.', 'danger');
            resetRecordingUI();
        }
    }

    function stopRecording() {
        if (isRecording) {
            // The mediaRecorder will be stopped in the onstop event
            isRecording = false;
            resetRecordingUI();
        }
    }

    function resetRecordingUI() {
        recordBtn.style.display = 'inline-block';
        stopBtn.style.display = 'none';
        recordingStatus.style.display = 'none';
    }

    async function processAudioRecording(audioBlob) {
        try {
            // Show processing status
            recordingStatus.innerHTML = `
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Processing...</span>
                </div>
                <p class="mt-2">Processing your audio...</p>
            `;

            // Create FormData for file upload
            const formData = new FormData();
            formData.append('audio', audioBlob, 'recording.wav');

            // Send to server
            const response = await fetch('/upload_audio', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (response.ok) {
                displayResults(data);
            } else {
                throw new Error(data.error || 'Failed to process audio');
            }

        } catch (error) {
            console.error('Error processing audio:', error);
            HealBuddy.showAlert('Error processing audio: ' + error.message, 'danger');
        } finally {
            resetRecordingUI();
        }
    }

    async function submitTextSymptoms() {
        const symptoms = symptomsText.value.trim();
        
        if (!symptoms) {
            HealBuddy.showAlert('Please describe your symptoms', 'warning');
            return;
        }

        try {
            // Show loading state
            submitTextBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Analyzing...';
            submitTextBtn.disabled = true;

            const response = await fetch('/submit_symptoms', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ symptoms: symptoms })
            });

            const data = await response.json();

            if (response.ok) {
                displayResults(data);
            } else {
                throw new Error(data.error || 'Failed to analyze symptoms');
            }

        } catch (error) {
            console.error('Error submitting symptoms:', error);
            HealBuddy.showAlert('Error analyzing symptoms: ' + error.message, 'danger');
        } finally {
            submitTextBtn.innerHTML = '<i class="fas fa-paper-plane"></i> Submit Symptoms';
            submitTextBtn.disabled = false;
        }
    }

    function displayResults(data) {
        const analysis = data.analysis;
        
        // Show transcription if available
        if (data.transcription) {
            document.getElementById('transcriptionResult').style.display = 'block';
            document.getElementById('transcriptionText').textContent = data.transcription;
        }

        // Update analysis results
        document.getElementById('symptomsResult').textContent = analysis.symptoms || 'Not specified';
        document.getElementById('durationResult').textContent = analysis.duration || 'Unknown';
        
        // Update pain level
        const painLevel = analysis.pain_level || 5;
        const painLevelBar = document.getElementById('painLevelBar');
        const painLevelText = document.getElementById('painLevelText');
        
        painLevelBar.style.width = (painLevel * 10) + '%';
        painLevelBar.className = `progress-bar bg-${getPainLevelColor(painLevel)}`;
        painLevelText.textContent = `${painLevel}/10 - ${getPainLevelDescription(painLevel)}`;
        
        // Update urgency
        const urgencyBadge = document.getElementById('urgencyBadge');
        const urgency = analysis.urgency || 'medium';
        urgencyBadge.className = `badge bg-${getUrgencyColor(urgency)}`;
        urgencyBadge.textContent = urgency.toUpperCase();
        
        // Update recommendations
        document.getElementById('recommendationsResult').textContent = analysis.recommendations || 'No specific recommendations available.';

        // Show audio response if available
        if (data.tts_audio) {
            currentAudioData = data.tts_audio;
            playAudioBtn.style.display = 'inline-block';
        }

        // Show results section
        resultsSection.style.display = 'block';
        resultsSection.scrollIntoView({ behavior: 'smooth' });

        // Show appropriate alert based on pain level
        if (painLevel >= 9) {
            HealBuddy.showAlert('High pain level detected. Consider seeking immediate medical attention.', 'danger');
        } else if (painLevel >= 6) {
            HealBuddy.showAlert('Moderate to high pain level. Consider scheduling a doctor appointment.', 'warning');
        } else {
            HealBuddy.showAlert('Analysis complete. Please review the recommendations below.', 'success');
        }
    }

    function getPainLevelColor(level) {
        if (level <= 3) return 'success';
        if (level <= 6) return 'warning';
        return 'danger';
    }

    function getPainLevelDescription(level) {
        if (level <= 3) return 'Mild';
        if (level <= 5) return 'Moderate';
        if (level <= 7) return 'Significant';
        if (level <= 9) return 'Severe';
        return 'Unbearable';
    }

    function getUrgencyColor(urgency) {
        switch (urgency.toLowerCase()) {
            case 'low': return 'success';
            case 'medium': return 'warning';
            case 'high': return 'danger';
            default: return 'secondary';
        }
    }

    function playAudioResponse() {
        if (currentAudioData) {
            try {
                // Convert base64 to blob
                const audioBlob = base64ToBlob(currentAudioData, 'audio/mpeg');
                const audioUrl = URL.createObjectURL(audioBlob);
                
                audioPlayer.src = audioUrl;
                audioPlayer.play();
                
                // Update button state
                playAudioBtn.innerHTML = '<i class="fas fa-volume-up"></i> Playing...';
                playAudioBtn.disabled = true;
                
                audioPlayer.onended = () => {
                    playAudioBtn.innerHTML = '<i class="fas fa-volume-up"></i> Play Audio Response';
                    playAudioBtn.disabled = false;
                    URL.revokeObjectURL(audioUrl);
                };
                
            } catch (error) {
                console.error('Error playing audio:', error);
                HealBuddy.showAlert('Error playing audio response', 'danger');
            }
        }
    }

    function base64ToBlob(base64, mimeType) {
        const byteCharacters = atob(base64);
        const byteNumbers = new Array(byteCharacters.length);
        
        for (let i = 0; i < byteCharacters.length; i++) {
            byteNumbers[i] = byteCharacters.charCodeAt(i);
        }
        
        const byteArray = new Uint8Array(byteNumbers);
        return new Blob([byteArray], { type: mimeType });
    }

    function resetForm() {
        // Clear form
        symptomsText.value = '';
        
        // Hide results
        resultsSection.style.display = 'none';
        document.getElementById('transcriptionResult').style.display = 'none';
        playAudioBtn.style.display = 'none';
        
        // Reset audio
        currentAudioData = null;
        audioPlayer.src = '';
        
        // Scroll to top
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    async function triggerEmergency() {
        if (confirm('Are you sure this is a medical emergency? This will alert hospitals and emergency services immediately.')) {
            try {
                const response = await fetch('/trigger_emergency', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    }
                });

                const data = await response.json();

                if (response.ok) {
                    HealBuddy.showAlert('Emergency alert sent! Help is on the way.', 'success');
                    // Redirect to dashboard after a short delay
                    setTimeout(() => {
                        window.location.href = '/dashboard';
                    }, 2000);
                } else {
                    throw new Error(data.error || 'Failed to send emergency alert');
                }

            } catch (error) {
                console.error('Error triggering emergency:', error);
                HealBuddy.showAlert('Error sending emergency alert. Please call emergency services directly.', 'danger');
            }
        }
    }

    // Auto-save text input to localStorage
    symptomsText.addEventListener('input', function() {
        localStorage.setItem('symptomsDraft', this.value);
    });

    // Load saved draft on page load
    const savedDraft = localStorage.getItem('symptomsDraft');
    if (savedDraft) {
        symptomsText.value = savedDraft;
    }

    // Clear draft when form is submitted
    submitTextBtn.addEventListener('click', function() {
        localStorage.removeItem('symptomsDraft');
    });
});

