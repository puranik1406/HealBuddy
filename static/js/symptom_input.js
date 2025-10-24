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
    const severityRange = document.getElementById('severityRange');
    const severityValue = document.getElementById('severityValue');
    const updateSeverityBtn = document.getElementById('updateSeverityBtn');
    const detailedAnalysis = document.getElementById('detailedAnalysis');
    const symptomsSeverityContainer = document.getElementById('symptomsSeverityContainer');

    // Update severity value display
    severityRange.addEventListener('input', function() {
        severityValue.textContent = this.value;
        severityValue.className = 'ms-2 badge ' + getSeverityBadgeClass(parseInt(this.value));
    });

    let isRecording = false;
    let currentAudioData = null;
    let mediaRecorder = null;
    let audioStream = null;

    // Voice Recording Functions
    recordBtn.addEventListener('click', startRecording);
    stopBtn.addEventListener('click', stopRecording);
    
    // Text Input Functions
    submitTextBtn.addEventListener('click', submitTextSymptoms);
    
    // Helper function for severity badge color
    function getSeverityBadgeClass(level) {
        if (level <= 3) return 'bg-success';
        if (level <= 6) return 'bg-warning';
        return 'bg-danger';
    }
    
    // Emergency Functions
    emergencyBtn.addEventListener('click', triggerEmergency);
    
    // Audio Playback Functions
    playAudioBtn.addEventListener('click', playAudioResponse);
    newConsultationBtn.addEventListener('click', resetForm);

    async function startRecording() {
        try {
            // Request microphone permission
            audioStream = await navigator.mediaDevices.getUserMedia({ 
                audio: {
                    echoCancellation: true,
                    noiseSuppression: true,
                    sampleRate: 16000
                } 
            });
            
            // Update UI
            recordBtn.style.display = 'none';
            stopBtn.style.display = 'inline-block';
            recordingStatus.style.display = 'block';
            
            // Start recording
            mediaRecorder = new MediaRecorder(audioStream, {
                mimeType: 'audio/webm;codecs=opus'
            });
            const audioChunks = [];
            
            mediaRecorder.ondataavailable = (event) => {
                if (event.data.size > 0) {
                    audioChunks.push(event.data);
                }
            };
            
            mediaRecorder.onstop = () => {
                console.log('Recording stopped, processing audio...');
                // Create blob from recorded chunks
                const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
                console.log('Audio blob created, size:', audioBlob.size);
                
                if (audioBlob.size > 0) {
                    processAudioRecording(audioBlob);
                } else {
                    console.error('Audio blob is empty');
                    HealBuddy.showAlert('Recording failed - no audio data captured. Please try again.', 'danger');
                    resetRecordingUI();
                }
                
                // Stop all tracks
                if (audioStream) {
                    audioStream.getTracks().forEach(track => track.stop());
                    audioStream = null;
                }
            };
            
            mediaRecorder.onerror = (event) => {
                console.error('MediaRecorder error:', event.error);
                HealBuddy.showAlert('Recording error: ' + event.error, 'danger');
                resetRecordingUI();
            };
            
            mediaRecorder.start();
            isRecording = true;
            console.log('Recording started');
            
            // Auto-stop after 30 seconds
            setTimeout(() => {
                if (isRecording) {
                    console.log('Auto-stopping recording after 30 seconds');
                    stopRecording();
                }
            }, 30000);
            
        } catch (error) {
            console.error('Error starting recording:', error);
            HealBuddy.showAlert('Could not access microphone. Please check permissions and ensure you are using HTTPS or localhost.', 'danger');
            resetRecordingUI();
        }
    }

    function stopRecording() {
        console.log('stopRecording called, isRecording:', isRecording);
        if (isRecording && mediaRecorder && mediaRecorder.state !== 'inactive') {
            // Stop the media recorder
            mediaRecorder.stop();
            isRecording = false;
            console.log('MediaRecorder stopped');
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
                <p class="mt-2">Transcribing your audio...</p>
            `;
            recordingStatus.style.display = 'block';

            // Create FormData for file upload
            const formData = new FormData();
            // Use a filename that matches the actual container/codec
            formData.append('audio', audioBlob, 'recording.webm');
            
            // Add severity if available
            const severity = document.getElementById('severityRange')?.value || '5';
            formData.append('severity', severity);

            console.log('Uploading audio for transcription, size:', audioBlob.size);

            // Send to server
            const response = await fetch('/upload_audio', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (response.ok) {
                console.log('Audio processed successfully');
                displayResults(data);
                // Success message is shown by displayResults function
            } else {
                // Handle transcription errors
                console.error('Transcription error:', data.error);
                let errorMsg = data.error || 'Failed to process audio';
                if (data.suggestion) {
                    errorMsg += ' ' + data.suggestion;
                }
                HealBuddy.showAlert(errorMsg, 'warning');
                
                // If transcription provided but incomplete, show it
                if (data.transcription) {
                    console.log('Partial transcription:', data.transcription);
                }
            }

        } catch (error) {
            console.error('Error processing audio:', error);
            HealBuddy.showAlert('Error processing audio: ' + error.message + '. Please try text input instead.', 'danger');
        } finally {
            resetRecordingUI();
        }
    }

    async function submitTextSymptoms() {
        const symptoms = symptomsText.value.trim();
        const severity = document.getElementById('severityRange')?.value || '5';
        
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
                body: JSON.stringify({ 
                    symptoms: symptoms,
                    severity: parseInt(severity)
                })
            });

            const data = await response.json();

            if (response.ok) {
                if (!data.analysis) {
                    throw new Error('No analysis data received');
                }
                displayResults(data);
            } else {
                throw new Error(data.error || 'Failed to analyze symptoms');
            }

        } catch (error) {
            console.error('Error submitting symptoms:', error);
            HealBuddy.showAlert('Error analyzing symptoms. Please try again or contact support if the problem persists.', 'danger');
        } finally {
            submitTextBtn.innerHTML = '<i class="fas fa-paper-plane"></i> Submit Symptoms';
            submitTextBtn.disabled = false;
        }
    }

    function displayResults(data) {
        const analysis = data.analysis;
        
        // Show transcription if available (from voice input)
        if (data.transcription) {
            document.getElementById('transcriptionResult').style.display = 'block';
            document.getElementById('transcriptionText').textContent = data.transcription;
        }

        // Parse the AI response if it's a JSON string
        let aiResponse = analysis;
        if (typeof analysis.ai_response === 'string') {
            try {
                aiResponse = JSON.parse(analysis.ai_response);
            } catch (e) {
                console.log('AI response is not in JSON format:', e);
            }
        }

    // Clear existing symptom sliders and follow-up area
    symptomsSeverityContainer.innerHTML = '';
    // Remove any previous follow-up container and diagnosis summary
    const existingFollowUp = document.getElementById('followUpContainer');
    if (existingFollowUp) existingFollowUp.remove();
    const existingDiagnosis = document.getElementById('initialDiagnosisSummary');
    if (existingDiagnosis) existingDiagnosis.remove();

        // Show initial diagnosis summary prominently
        if (aiResponse.diagnosis || aiResponse.possible_conditions) {
            const diagnosisSummary = document.createElement('div');
            diagnosisSummary.id = 'initialDiagnosisSummary';
            diagnosisSummary.className = 'mb-4';
            
            let summaryHTML = '<div class="card border-primary"><div class="card-header bg-primary text-white">';
            summaryHTML += '<h6 class="mb-0"><i class="fas fa-stethoscope"></i> Initial AI Diagnosis Summary</h6>';
            summaryHTML += '</div><div class="card-body">';
            
            // Show preliminary diagnosis
            if (aiResponse.diagnosis) {
                summaryHTML += `<div class="mb-3"><strong>Preliminary Analysis:</strong><p class="mt-2">${aiResponse.diagnosis}</p></div>`;
            }
            
            // Show possible conditions
            if (aiResponse.possible_conditions && aiResponse.possible_conditions.length > 0) {
                summaryHTML += '<div class="mb-3"><strong>Possible Conditions:</strong><ul class="mt-2">';
                aiResponse.possible_conditions.forEach(condition => {
                    summaryHTML += `<li>${condition}</li>`;
                });
                summaryHTML += '</ul></div>';
            }
            
            // Show red flags if any
            if (aiResponse.red_flags && aiResponse.red_flags.length > 0) {
                summaryHTML += '<div class="alert alert-danger mb-0"><strong><i class="fas fa-exclamation-triangle"></i> Warning Signs:</strong><ul class="mt-2 mb-0">';
                aiResponse.red_flags.forEach(flag => {
                    summaryHTML += `<li>${flag}</li>`;
                });
                summaryHTML += '</ul></div>';
            }
            
            summaryHTML += '</div></div>';
            diagnosisSummary.innerHTML = summaryHTML;
            symptomsSeverityContainer.insertAdjacentElement('beforebegin', diagnosisSummary);
        }

        // Create sliders for each identified symptom
        const identified = aiResponse.identified_symptoms || [];
        const defaults = aiResponse.default_severities || [];
        
        if (identified.length > 0) {
            // Add header for symptom severity section
            const severityHeader = document.createElement('div');
            severityHeader.className = 'mb-3';
            severityHeader.innerHTML = '<h6 class="text-primary"><i class="fas fa-sliders-h"></i> Adjust Symptom Severities:</h6><p class="text-muted small">Please adjust the severity for each symptom based on how you feel (1=mild, 10=severe)</p>';
            symptomsSeverityContainer.appendChild(severityHeader);
        }
        
        identified.forEach((symptom, index) => {
            const defaultSeverity = defaults[index] || 5;
            const sliderId = `symptom-severity-${index}`;
            const sliderHTML = `
                <div class="mb-3">
                    <label class="form-label">${symptom}:</label>
                    <div class="d-flex align-items-center">
                        <input type="range" class="form-range flex-grow-1 symptom-slider" 
                            id="${sliderId}" min="1" max="10" value="${defaultSeverity}"
                            data-symptom="${symptom}">
                        <span class="ms-2 badge bg-warning severity-badge">${defaultSeverity}</span>
                    </div>
                </div>
            `;
            symptomsSeverityContainer.insertAdjacentHTML('beforeend', sliderHTML);
        });

        // Show update button if there are symptoms
        updateSeverityBtn.style.display = identified.length > 0 ? 'inline-block' : 'none';
        
        // Add event listeners to new sliders
        document.querySelectorAll('.symptom-slider').forEach(slider => {
            slider.addEventListener('input', function() {
                const badge = this.nextElementSibling;
                badge.textContent = this.value;
                badge.className = 'ms-2 badge ' + getSeverityBadgeClass(parseInt(this.value));
            });
        });

        // Render follow-up questions if provided
        const followUps = aiResponse.follow_up_questions || [];
        if (followUps.length > 0) {
            const followUpContainer = document.createElement('div');
            followUpContainer.id = 'followUpContainer';
            followUpContainer.className = 'mb-4';
            
            let followUpHTML = '<div class="card border-info">';
            followUpHTML += '<div class="card-header bg-info text-white">';
            followUpHTML += '<h6 class="mb-0"><i class="fas fa-question-circle"></i> Follow-up Questions</h6>';
            followUpHTML += '</div><div class="card-body">';
            followUpHTML += '<p class="text-muted small mb-3">Please answer these questions to help refine the diagnosis:</p>';
            
            followUps.forEach((q, i) => {
                followUpHTML += `
                    <div class="mb-3">
                        <label class="form-label fw-bold">${i + 1}. ${q}</label>
                        <input type="text" class="form-control follow-up-input" 
                               data-question="${q}" 
                               placeholder="Your answer..." />
                    </div>
                `;
            });
            
            followUpHTML += '</div></div>';
            followUpContainer.innerHTML = followUpHTML;
            symptomsSeverityContainer.insertAdjacentElement('afterend', followUpContainer);
        }

        // Initial detailed analysis display (will update after finalize)
        updateDetailedAnalysis(aiResponse);

        // Update urgency badge
        const urgencyBadge = document.getElementById('urgencyBadge');
        const urgency = aiResponse.urgency || analysis.urgency || 'medium';
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

        // Show appropriate message based on what's available
        let alertMessage = '✅ Initial diagnosis complete! ';
        if (followUps.length > 0) {
            alertMessage += 'Please answer the follow-up questions and adjust symptom severities, then click "Update Analysis" for final recommendations.';
        } else if (identified.length > 0) {
            alertMessage += 'Please adjust the symptom severities if needed, then click "Update Analysis" for final recommendations.';
        } else {
            alertMessage += 'Review the diagnosis summary below.';
        }
        HealBuddy.showAlert(alertMessage, 'info');
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

    function updateDetailedAnalysis(analysis) {
        // Show the detailed analysis section
        detailedAnalysis.style.display = 'block';

        // Save suggested medications to localStorage for order_medicine page
        if (analysis.suggested_medications && analysis.suggested_medications.length > 0) {
            localStorage.setItem('suggestedMedications', JSON.stringify(analysis.suggested_medications));
        }

        // Update duration
        document.getElementById('durationResult').textContent = analysis.duration || 'Unknown';

        // Calculate overall severity from symptom sliders
        const sliders = document.querySelectorAll('.symptom-slider');
        const severityValues = Array.from(sliders).map(slider => parseInt(slider.value));
        const overallSeverity = severityValues.length > 0 
            ? Math.ceil(severityValues.reduce((a, b) => a + b) / severityValues.length)
            : parseInt(severityRange.value);

        // Update overall severity display
        const painLevelBar = document.getElementById('painLevelBar');
        const painLevelText = document.getElementById('painLevelText');
        painLevelBar.style.width = (overallSeverity * 10) + '%';
        painLevelBar.className = `progress-bar bg-${getSeverityBadgeClass(overallSeverity)}`;
        painLevelText.textContent = `${overallSeverity}/10 - ${getSeverityDescription(overallSeverity)}`;

        // Update assessment
        document.getElementById('assessmentResult').textContent = analysis.diagnosis || 'Assessment not available';

        // Update possible conditions
        const conditionsList = document.getElementById('conditionsList');
        conditionsList.innerHTML = '';
        const conditions = analysis.possible_conditions || [];
        conditions.forEach(condition => {
            conditionsList.insertAdjacentHTML('beforeend', `
                <li class="list-group-item">${condition}</li>
            `);
        });

        // Update recommendation options based on severity
        const recommendationOptions = document.getElementById('recommendationOptions');
        recommendationOptions.innerHTML = '';

        if (overallSeverity >= 6) {
            // High severity (6-10) - Only Doctor consultation
            recommendationOptions.innerHTML = `
                <div class="alert alert-danger">
                    <h6><i class="fas fa-exclamation-circle"></i> Medical Consultation Recommended</h6>
                    <p>Based on the severity of your symptoms (${overallSeverity}/10), immediate medical consultation is advised.</p>
                    <button class="btn btn-danger mt-2" onclick="scheduleDoctor()">
                        <i class="fas fa-user-md"></i> Book Doctor Consultation
                    </button>
                </div>
            `;
        } else if (overallSeverity >= 1) {
            // Mild to moderate case (1-5) - Both medicine order and consultation options
            recommendationOptions.innerHTML = `
                <div class="alert alert-info">
                    <h6><i class="fas fa-info-circle"></i> Treatment Options</h6>
                    <p>Based on your symptoms (severity: ${overallSeverity}/10), you can:</p>
                    <div class="d-grid gap-2">
                        <button class="btn btn-success" onclick="orderMedicine()">
                            <i class="fas fa-shopping-cart"></i> Order Medicines
                        </button>
                        <button class="btn btn-primary" onclick="scheduleDoctor()">
                            <i class="fas fa-user-md"></i> Book Consultation
                        </button>
                    </div>
                </div>
            `;
        }

        // Update additional recommendations
        document.getElementById('recommendationsResult').textContent = analysis.recommendations || 'No specific recommendations available.';
    }

    function getSeverityDescription(level) {
        if (level <= 3) return 'Mild';
        if (level <= 5) return 'Moderate';
        if (level <= 7) return 'Significant';
        return 'Severe';
    }

    function getSeverityBadgeClass(level) {
        if (level <= 3) return 'bg-success';
        if (level <= 6) return 'bg-warning';
        return 'bg-danger';
    }

    // Add event listener for the update severity button
    updateSeverityBtn.addEventListener('click', async function() {
        // Collect per-symptom severities
        const symptoms = Array.from(document.querySelectorAll('.symptom-slider')).map(slider => ({
            symptom: slider.dataset.symptom,
            severity: parseInt(slider.value)
        }));

        // Collect follow-up answers
        const followUpInputs = Array.from(document.querySelectorAll('.follow-up-input'));
        const follow_up_answers = followUpInputs.map(input => ({
            question: input.dataset.question,
            answer: input.value.trim()
        }));

        try {
            const response = await fetch('/finalize_analysis', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ symptoms, follow_up_answers })
            });

            const data = await response.json();
            if (response.ok) {
                // Display final analysis
                const final = data.analysis;
                updateDetailedAnalysis(final);
                document.getElementById('recommendationsResult').textContent = final.recommendations || '';
                // Store consultation id if returned
                if (data.consultation_id) {
                    // you could store this for later; currently not used in frontend
                }
                HealBuddy.showAlert('Final analysis ready. Review recommendations below.', 'success');
            } else {
                throw new Error(data.error || 'Failed to finalize analysis');
            }
        } catch (error) {
            console.error('Error finalizing analysis:', error);
            HealBuddy.showAlert('Error finalizing analysis: ' + error.message, 'danger');
        }
    });

    // Placeholder functions for actions
    function scheduleDoctor() {
        window.location.href = '/schedule_consultation';
    }

    function orderMedicine() {
        window.location.href = '/order_medicine';
    }

    function resetForm() {
        // Clear form
        symptomsText.value = '';
        
        // Hide results
        resultsSection.style.display = 'none';
        document.getElementById('transcriptionResult').style.display = 'none';
        playAudioBtn.style.display = 'none';
        detailedAnalysis.style.display = 'none';
        updateSeverityBtn.style.display = 'none';
        
        // Clear symptoms
        symptomsSeverityContainer.innerHTML = '';
        
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

