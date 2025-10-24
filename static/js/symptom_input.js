// Symptom Input Page JavaScript

document.addEventListener('DOMContentLoaded', function() {
    const submitTextBtn = document.getElementById('submitTextBtn');
    const symptomsText = document.getElementById('symptomsText');
    const resultsSection = document.getElementById('resultsSection');
    const emergencyBtn = document.getElementById('emergencyBtn');
    const newConsultationBtn = document.getElementById('newConsultationBtn');
    const severityRange = document.getElementById('severityRange');
    const severityValue = document.getElementById('severityValue');
    const updateSeverityBtn = document.getElementById('updateSeverityBtn');
    const detailedAnalysis = document.getElementById('detailedAnalysis');
    const symptomsSeverityContainer = document.getElementById('symptomsSeverityContainer');

    // Voice Input Elements
    const startRecordBtn = document.getElementById('startRecordBtn');
    const stopRecordBtn = document.getElementById('stopRecordBtn');
    const recordingStatus = document.getElementById('recordingStatus');
    const transcriptionSection = document.getElementById('transcriptionSection');
    const transcriptionText = document.getElementById('transcriptionText');
    const conversationSection = document.getElementById('conversationSection');
    const conversationMessages = document.getElementById('conversationMessages');
    const continueConversationBtn = document.getElementById('continueConversationBtn');
    const finishConversationBtn = document.getElementById('finishConversationBtn');
    const aiAudioPlayer = document.getElementById('aiAudioPlayer');

    // Voice Recording Variables
    let mediaRecorder = null;
    let audioChunks = [];
    let conversationHistory = [];
    let isRecording = false;

    // Update severity value display
    severityRange.addEventListener('input', function() {
        severityValue.textContent = this.value;
        severityValue.className = 'ms-2 badge ' + getSeverityBadgeClass(parseInt(this.value));
    });
    
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
    
    // New Consultation
    newConsultationBtn.addEventListener('click', resetForm);

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
        detailedAnalysis.style.display = 'none';
        updateSeverityBtn.style.display = 'none';
        
        // Clear symptoms
        symptomsSeverityContainer.innerHTML = '';
        
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

    // ======================
    // VOICE INPUT FUNCTIONS
    // ======================

    // Voice Recording Event Listeners
    startRecordBtn.addEventListener('click', startRecording);
    stopRecordBtn.addEventListener('click', stopRecording);
    continueConversationBtn.addEventListener('click', continueConversation);
    finishConversationBtn.addEventListener('click', finishConversation);

    async function startRecording() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaRecorder = new MediaRecorder(stream);
            audioChunks = [];

            mediaRecorder.ondataavailable = (event) => {
                audioChunks.push(event.data);
            };

            mediaRecorder.onstop = async () => {
                const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
                await processAudio(audioBlob);
                
                // Stop all tracks to release microphone
                stream.getTracks().forEach(track => track.stop());
            };

            mediaRecorder.start();
            isRecording = true;

            // Update UI
            startRecordBtn.style.display = 'none';
            stopRecordBtn.style.display = 'inline-block';
            recordingStatus.style.display = 'block';

        } catch (error) {
            console.error('Error accessing microphone:', error);
            HealBuddy.showAlert('Error accessing microphone. Please grant permission.', 'danger');
        }
    }

    function stopRecording() {
        if (mediaRecorder && isRecording) {
            mediaRecorder.stop();
            isRecording = false;

            // Update UI
            startRecordBtn.style.display = 'inline-block';
            stopRecordBtn.style.display = 'none';
            recordingStatus.style.display = 'none';
        }
    }

    async function processAudio(audioBlob) {
        const formData = new FormData();
        formData.append('audio', audioBlob, 'recording.webm');
        
        // Add conversation history for context
        if (conversationHistory.length > 0) {
            formData.append('conversation_history', JSON.stringify(conversationHistory));
        }

        try {
            // Show loading
            HealBuddy.showAlert('Processing your voice input...', 'info');

            const response = await fetch('/upload_audio', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (response.ok) {
                // Display transcription
                transcriptionText.textContent = data.transcription;
                transcriptionSection.style.display = 'block';

                // Add user message to conversation
                addMessageToConversation('user', data.transcription);
                conversationHistory.push({
                    role: 'user',
                    content: data.transcription
                });

                // Add AI response to conversation
                addMessageToConversation('ai', data.ai_response.text);
                conversationHistory.push({
                    role: 'ai',
                    content: data.ai_response.text
                });

                // Show conversation section
                conversationSection.style.display = 'block';

                // Play AI audio response
                if (data.ai_response.audio) {
                    playAudioResponse(data.ai_response.audio);
                }

                // Check if conversation should continue or finish
                if (data.ai_response.ready_for_diagnosis) {
                    // Show finish button prominently
                    finishConversationBtn.classList.add('btn-lg');
                    HealBuddy.showAlert('AI has gathered enough information. Click "Finish & Get Diagnosis" to see results.', 'success');
                } else {
                    HealBuddy.showAlert('Continue the conversation or finish to get diagnosis.', 'info');
                }

            } else {
                throw new Error(data.error || 'Failed to process audio');
            }

        } catch (error) {
            console.error('Error processing audio:', error);
            HealBuddy.showAlert('Error processing audio: ' + error.message, 'danger');
        }
    }

    function addMessageToConversation(role, content) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `conversation-message ${role}`;
        
        const icon = role === 'user' ? '<i class="fas fa-user"></i>' : '<i class="fas fa-robot"></i>';
        const roleName = role === 'user' ? 'You' : 'AI Doctor';
        
        messageDiv.innerHTML = `
            <div class="message-header">
                ${icon} ${roleName}
            </div>
            <div class="message-content">${content}</div>
        `;
        
        conversationMessages.appendChild(messageDiv);
        conversationMessages.scrollTop = conversationMessages.scrollHeight;
    }

    function playAudioResponse(audioBase64) {
        const audioBlob = base64ToBlob(audioBase64, 'audio/mp3');
        const audioUrl = URL.createObjectURL(audioBlob);
        
        aiAudioPlayer.src = audioUrl;
        aiAudioPlayer.play();
        
        // Add visual feedback
        conversationMessages.classList.add('audio-playing');
        
        aiAudioPlayer.onended = () => {
            conversationMessages.classList.remove('audio-playing');
            URL.revokeObjectURL(audioUrl);
        };
    }

    function base64ToBlob(base64, contentType) {
        const byteCharacters = atob(base64);
        const byteArrays = [];
        
        for (let offset = 0; offset < byteCharacters.length; offset += 512) {
            const slice = byteCharacters.slice(offset, offset + 512);
            const byteNumbers = new Array(slice.length);
            
            for (let i = 0; i < slice.length; i++) {
                byteNumbers[i] = slice.charCodeAt(i);
            }
            
            const byteArray = new Uint8Array(byteNumbers);
            byteArrays.push(byteArray);
        }
        
        return new Blob(byteArrays, { type: contentType });
    }

    async function continueConversation() {
        // Just start recording again
        await startRecording();
    }

    async function finishConversation() {
        try {
            // Show loading
            finishConversationBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Analyzing...';
            finishConversationBtn.disabled = true;

            const response = await fetch('/finalize_voice_conversation', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    conversation_history: conversationHistory
                })
            });

            const data = await response.json();

            if (response.ok) {
                // Display results using existing function
                displayResults(data);
                
                // Hide voice input section, show results
                conversationSection.style.display = 'none';
                transcriptionSection.style.display = 'none';
                
                HealBuddy.showAlert('Diagnosis complete! Review your results below.', 'success');
            } else {
                throw new Error(data.error || 'Failed to finalize conversation');
            }

        } catch (error) {
            console.error('Error finalizing conversation:', error);
            HealBuddy.showAlert('Error finalizing conversation: ' + error.message, 'danger');
        } finally {
            finishConversationBtn.innerHTML = '<i class="fas fa-check"></i> Finish & Get Diagnosis';
            finishConversationBtn.disabled = false;
        }
    }
});

