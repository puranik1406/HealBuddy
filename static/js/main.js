// HealBuddy Main JavaScript Functions

// Initialize tooltips
document.addEventListener('DOMContentLoaded', function() {
    // Initialize Bootstrap tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Add fade-in animation to cards
    const cards = document.querySelectorAll('.card');
    cards.forEach((card, index) => {
        card.style.animationDelay = `${index * 0.1}s`;
        card.classList.add('fade-in');
    });
});

// Utility Functions
function showAlert(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const container = document.querySelector('.container');
    container.insertBefore(alertDiv, container.firstChild);
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.remove();
        }
    }, 5000);
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// API Helper Functions
async function makeRequest(url, options = {}) {
    try {
        const response = await fetch(url, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('Request failed:', error);
        showAlert('An error occurred. Please try again.', 'danger');
        throw error;
    }
}

// Form Validation
function validateForm(formId) {
    const form = document.getElementById(formId);
    if (!form) return false;
    
    const requiredFields = form.querySelectorAll('[required]');
    let isValid = true;
    
    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            field.classList.add('is-invalid');
            isValid = false;
        } else {
            field.classList.remove('is-invalid');
        }
    });
    
    return isValid;
}

// File Upload Helper
function handleFileUpload(input, callback) {
    const file = input.files[0];
    if (!file) return;
    
    // Validate file size (16MB limit)
    const maxSize = 16 * 1024 * 1024;
    if (file.size > maxSize) {
        showAlert('File size must be less than 16MB', 'danger');
        return;
    }
    
    // Validate file type
    const allowedTypes = [
        'application/pdf',
        'image/jpeg',
        'image/jpg',
        'image/png',
        'application/msword',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'text/plain'
    ];
    
    if (!allowedTypes.includes(file.type)) {
        showAlert('Invalid file type. Please upload PDF, image, Word document, or text file.', 'danger');
        return;
    }
    
    if (callback) callback(file);
}

// Audio Recording Functions
class AudioRecorder {
    constructor() {
        this.mediaRecorder = null;
        this.audioChunks = [];
        this.isRecording = false;
    }
    
    async startRecording() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            this.mediaRecorder = new MediaRecorder(stream);
            this.audioChunks = [];
            
            this.mediaRecorder.ondataavailable = (event) => {
                this.audioChunks.push(event.data);
            };
            
            this.mediaRecorder.onstop = () => {
                const audioBlob = new Blob(this.audioChunks, { type: 'audio/wav' });
                this.onRecordingComplete(audioBlob);
            };
            
            this.mediaRecorder.start();
            this.isRecording = true;
            
            return true;
        } catch (error) {
            console.error('Error starting recording:', error);
            showAlert('Could not access microphone. Please check permissions.', 'danger');
            return false;
        }
    }
    
    stopRecording() {
        if (this.mediaRecorder && this.isRecording) {
            this.mediaRecorder.stop();
            this.isRecording = false;
            
            // Stop all tracks
            this.mediaRecorder.stream.getTracks().forEach(track => track.stop());
        }
    }
    
    onRecordingComplete(audioBlob) {
        // This will be overridden by the specific page
        console.log('Recording completed:', audioBlob);
    }
}

// Global audio recorder instance
window.audioRecorder = new AudioRecorder();

// Dashboard Functions
function updateDashboardStats() {
    // This would typically fetch updated stats from the server
    console.log('Updating dashboard stats...');
}

// Health Records Functions
function previewFile(file) {
    const reader = new FileReader();
    reader.onload = function(e) {
        // Create preview modal or display
        console.log('File preview:', e.target.result);
    };
    reader.readAsDataURL(file);
}

// Emergency Functions
function triggerEmergencyAlert() {
    if (confirm('Are you sure this is a medical emergency? This will alert hospitals and emergency services.')) {
        // Implementation would be in the specific page
        console.log('Emergency alert triggered');
    }
}

// Search and Filter Functions
function filterTable(tableId, searchTerm) {
    const table = document.getElementById(tableId);
    if (!table) return;
    
    const rows = table.getElementsByTagName('tr');
    
    for (let i = 1; i < rows.length; i++) {
        const row = rows[i];
        const text = row.textContent.toLowerCase();
        
        if (text.includes(searchTerm.toLowerCase())) {
            row.style.display = '';
        } else {
            row.style.display = 'none';
        }
    }
}

// Notification Functions
function requestNotificationPermission() {
    if ('Notification' in window) {
        Notification.requestPermission().then(permission => {
            if (permission === 'granted') {
                console.log('Notification permission granted');
            }
        });
    }
}

function showNotification(title, body, icon = null) {
    if ('Notification' in window && Notification.permission === 'granted') {
        new Notification(title, {
            body: body,
            icon: icon || '/static/images/healbuddy-icon.png'
        });
    }
}

// Local Storage Helpers
function saveToLocalStorage(key, data) {
    try {
        localStorage.setItem(key, JSON.stringify(data));
    } catch (error) {
        console.error('Error saving to localStorage:', error);
    }
}

function loadFromLocalStorage(key) {
    try {
        const data = localStorage.getItem(key);
        return data ? JSON.parse(data) : null;
    } catch (error) {
        console.error('Error loading from localStorage:', error);
        return null;
    }
}

// Theme Functions (for future dark mode support)
function toggleTheme() {
    const body = document.body;
    const currentTheme = body.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    
    body.setAttribute('data-theme', newTheme);
    saveToLocalStorage('theme', newTheme);
}

function loadTheme() {
    const savedTheme = loadFromLocalStorage('theme') || 'light';
    document.body.setAttribute('data-theme', savedTheme);
}

// Initialize theme on page load
document.addEventListener('DOMContentLoaded', function() {
    loadTheme();
    requestNotificationPermission();
});

// Export functions for use in other scripts
window.HealBuddy = {
    showAlert,
    formatDate,
    formatFileSize,
    makeRequest,
    validateForm,
    handleFileUpload,
    AudioRecorder,
    updateDashboardStats,
    previewFile,
    triggerEmergencyAlert,
    filterTable,
    showNotification,
    saveToLocalStorage,
    loadFromLocalStorage,
    toggleTheme
};

