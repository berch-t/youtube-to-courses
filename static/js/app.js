/**
 * YouTube Course Builder - Frontend JavaScript
 * Handles UI interactions, form validation, and progress monitoring
 */

// Configuration
const CONFIG = {
    POLL_INTERVAL: 2000, // 2 seconds
    MAX_FILE_SIZE: 50 * 1024 * 1024, // 50MB
    SUPPORTED_FORMATS: ['.md'],
    YOUTUBE_REGEX: /^(https?:\/\/)?(www\.)?(youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/|youtube\.com\/v\/)[a-zA-Z0-9_-]{11}/
};

// Global state
let currentTaskId = null;
let progressInterval = null;
let startTime = null;

// DOM elements
const elements = {
    youtubeForm: document.getElementById('youtube-form'),
    localForm: document.getElementById('local-form'),
    youtubeUrl: document.getElementById('youtube-url'),
    transcriptFile: document.getElementById('transcript-file'),
    outputFilename: document.getElementById('output-filename'),
    progressModal: document.getElementById('progressModal'),
    successModal: document.getElementById('successModal'),
    progressBar: document.getElementById('progress-bar'),
    progressMessage: document.getElementById('progress-message'),
    currentStep: document.getElementById('current-step'),
    timeElapsed: document.getElementById('time-elapsed'),
    downloadLink: document.getElementById('download-link')
};

// Initialize application
document.addEventListener('DOMContentLoaded', function() {
    initializeEventListeners();
    setupFormValidation();
    setupFileUploadHandling();
});

/**
 * Initialize all event listeners
 */
function initializeEventListeners() {
    // Form submissions
    document.getElementById('youtube-processing-form')?.addEventListener('submit', handleYouTubeSubmission);
    document.getElementById('local-processing-form')?.addEventListener('submit', handleLocalSubmission);
    
    // File input change
    elements.transcriptFile?.addEventListener('change', handleFileSelection);
    
    // URL input validation
    elements.youtubeUrl?.addEventListener('input', debounce(validateYouTubeUrl, 500));
    
    // Modal events
    elements.progressModal?.addEventListener('hidden.bs.modal', handleProgressModalHidden);
    elements.successModal?.addEventListener('hidden.bs.modal', resetForms);
}

/**
 * Setup form validation
 */
function setupFormValidation() {
    // Real-time YouTube URL validation
    if (elements.youtubeUrl) {
        elements.youtubeUrl.addEventListener('blur', function() {
            validateYouTubeUrl();
        });
    }
    
    // File size validation
    if (elements.transcriptFile) {
        elements.transcriptFile.addEventListener('change', function(e) {
            validateFileSize(e.target.files[0]);
        });
    }
}

/**
 * Setup file upload handling
 */
function setupFileUploadHandling() {
    if (!elements.transcriptFile) return;
    
    // Drag and drop functionality
    const dropZone = elements.transcriptFile.closest('.mb-4');
    
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, preventDefaults, false);
    });
    
    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, highlight, false);
    });
    
    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, unhighlight, false);
    });
    
    dropZone.addEventListener('drop', handleDrop, false);
    
    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }
    
    function highlight(e) {
        dropZone.classList.add('border-primary', 'bg-light');
    }
    
    function unhighlight(e) {
        dropZone.classList.remove('border-primary', 'bg-light');
    }
    
    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        
        if (files.length > 0) {
            elements.transcriptFile.files = files;
            handleFileSelection({ target: elements.transcriptFile });
        }
    }
}

/**
 * Validate YouTube URL
 */
function validateYouTubeUrl() {
    const url = elements.youtubeUrl?.value.trim();
    if (!url) return;
    
    const isValid = CONFIG.YOUTUBE_REGEX.test(url);
    
    if (isValid) {
        elements.youtubeUrl.classList.remove('is-invalid');
        elements.youtubeUrl.classList.add('is-valid');
        showValidationFeedback(elements.youtubeUrl, 'URL YouTube valide', 'valid');
    } else {
        elements.youtubeUrl.classList.remove('is-valid');
        elements.youtubeUrl.classList.add('is-invalid');
        showValidationFeedback(elements.youtubeUrl, 'URL YouTube invalide', 'invalid');
    }
    
    return isValid;
}

/**
 * Validate file size
 */
function validateFileSize(file) {
    if (!file) return false;
    
    const isValidSize = file.size <= CONFIG.MAX_FILE_SIZE;
    const isValidFormat = CONFIG.SUPPORTED_FORMATS.some(format => 
        file.name.toLowerCase().endsWith(format)
    );
    
    if (!isValidSize) {
        showAlert('Le fichier est trop volumineux. Taille maximale: 50MB', 'danger');
        elements.transcriptFile.value = '';
        return false;
    }
    
    if (!isValidFormat) {
        showAlert('Format de fichier non supporté. Utilisez un fichier .md', 'danger');
        elements.transcriptFile.value = '';
        return false;
    }
    
    return true;
}

/**
 * Handle file selection
 */
function handleFileSelection(e) {
    const file = e.target.files[0];
    if (!file) return;
    
    if (validateFileSize(file)) {
        // Auto-generate output filename
        const baseName = file.name.replace(/\.[^/.]+$/, '');
        const timestamp = new Date().toISOString().slice(0, 19).replace(/[T:]/g, '-');
        elements.outputFilename.value = `cours-${baseName}-${timestamp}.md`;
        
        // Show file info
        showFileInfo(file);
    }
}

/**
 * Show file information
 */
function showFileInfo(file) {
    const fileSize = (file.size / 1024 / 1024).toFixed(2);
    const info = `Fichier sélectionné: ${file.name} (${fileSize} MB)`;
    
    // Find or create info element
    let infoElement = document.getElementById('file-info');
    if (!infoElement) {
        infoElement = document.createElement('div');
        infoElement.id = 'file-info';
        infoElement.className = 'alert alert-info mt-2';
        elements.transcriptFile.parentNode.appendChild(infoElement);
    }
    
    infoElement.innerHTML = `<i class="bi bi-file-earmark-check me-2"></i>${info}`;
}

/**
 * Handle YouTube form submission
 */
async function handleYouTubeSubmission(e) {
    e.preventDefault();
    
    const url = elements.youtubeUrl.value.trim();
    const chunkMinutes = parseInt(document.getElementById('chunk-minutes').value);
    
    // Validate form
    if (!url || !validateYouTubeUrl()) {
        showAlert('Veuillez entrer une URL YouTube valide', 'danger');
        return;
    }
    
    // Show loading state
    const submitButton = e.target.querySelector('button[type="submit"]');
    setButtonLoading(submitButton, true);
    
    try {
        const response = await fetch('/process-youtube', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                url: url,
                chunk_minutes: chunkMinutes
            })
        });
        
        const result = await response.json();
        
        if (response.ok) {
            currentTaskId = result.task_id;
            showProgressModal();
            startProgressMonitoring();
        } else {
            throw new Error(result.error || 'Erreur lors du traitement');
        }
    } catch (error) {
        console.error('Error:', error);
        showAlert(`Erreur: ${error.message}`, 'danger');
    } finally {
        setButtonLoading(submitButton, false);
    }
}

/**
 * Handle local file form submission
 */
async function handleLocalSubmission(e) {
    e.preventDefault();
    
    const file = elements.transcriptFile.files[0];
    const outputName = elements.outputFilename.value.trim();
    
    // Validate form
    if (!file) {
        showAlert('Veuillez sélectionner un fichier de transcription', 'danger');
        return;
    }
    
    if (!outputName) {
        showAlert('Veuillez spécifier un nom de fichier de sortie', 'danger');
        return;
    }
    
    // Show loading state
    const submitButton = e.target.querySelector('button[type="submit"]');
    setButtonLoading(submitButton, true);
    
    const formData = new FormData();
    formData.append('transcript_file', file);
    formData.append('output_filename', outputName);
    
    try {
        const response = await fetch('/process-local', {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (response.ok) {
            currentTaskId = result.task_id;
            showProgressModal();
            startProgressMonitoring();
        } else {
            throw new Error(result.error || 'Erreur lors du traitement');
        }
    } catch (error) {
        console.error('Error:', error);
        showAlert(`Erreur: ${error.message}`, 'danger');
    } finally {
        setButtonLoading(submitButton, false);
    }
}

/**
 * Show progress modal
 */
function showProgressModal() {
    const modal = new bootstrap.Modal(elements.progressModal, {
        backdrop: 'static',
        keyboard: false
    });
    modal.show();
    
    // Reset progress
    updateProgressUI({
        progress: 0,
        message: 'Initialisation...',
        status: 'processing'
    });
    
    startTime = new Date();
}

/**
 * Start progress monitoring
 */
function startProgressMonitoring() {
    if (progressInterval) {
        clearInterval(progressInterval);
    }
    
    progressInterval = setInterval(async () => {
        try {
            const response = await fetch(`/status/${currentTaskId}`);
            const task = await response.json();
            
            updateProgressUI(task);
            
            if (task.status === 'completed') {
                clearInterval(progressInterval);
                progressInterval = null;
                setTimeout(() => showSuccess(task.result), 500);
            } else if (task.status === 'failed') {
                clearInterval(progressInterval);
                progressInterval = null;
                setTimeout(() => showError(task.error || 'Une erreur est survenue'), 500);
            }
        } catch (error) {
            console.error('Error checking task status:', error);
            // Continue polling on error
        }
    }, CONFIG.POLL_INTERVAL);
}

/**
 * Update progress UI
 */
function updateProgressUI(task) {
    if (!elements.progressBar || !elements.progressMessage) return;
    
    const progress = Math.max(0, Math.min(100, task.progress || 0));
    
    // Update progress bar
    elements.progressBar.style.width = progress + '%';
    elements.progressBar.textContent = progress + '%';
    elements.progressBar.setAttribute('aria-valuenow', progress);
    
    // Update message
    elements.progressMessage.textContent = task.message || 'Traitement en cours...';
    
    // Update current step
    if (elements.currentStep) {
        elements.currentStep.textContent = getStepName(progress);
    }
    
    // Update elapsed time
    if (elements.timeElapsed && startTime) {
        const elapsed = Math.floor((new Date() - startTime) / 1000);
        const minutes = Math.floor(elapsed / 60);
        const seconds = elapsed % 60;
        elements.timeElapsed.textContent = 
            `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
    }
}

/**
 * Get step name based on progress
 */
function getStepName(progress) {
    if (progress < 20) return 'Initialisation';
    if (progress < 40) return 'Téléchargement';
    if (progress < 70) return 'Transcription';
    if (progress < 90) return 'Génération du cours';
    if (progress < 100) return 'Finalisation';
    return 'Terminé';
}

/**
 * Show success modal
 */
function showSuccess(result) {
    hideProgressModal();
    
    if (result && result.download_url) {
        elements.downloadLink.href = result.download_url;
        
        const successModal = new bootstrap.Modal(elements.successModal);
        successModal.show();
        
        // Trigger confetti effect
        if (typeof confetti !== 'undefined') {
            confetti({
                particleCount: 100,
                spread: 70,
                origin: { y: 0.6 }
            });
        }
    } else {
        showAlert('Cours généré avec succès, mais le lien de téléchargement est indisponible', 'warning');
    }
}

/**
 * Show error
 */
function showError(error) {
    hideProgressModal();
    showAlert(`Erreur lors du traitement: ${error}`, 'danger');
}

/**
 * Hide progress modal
 */
function hideProgressModal() {
    if (progressInterval) {
        clearInterval(progressInterval);
        progressInterval = null;
    }
    
    const modalInstance = bootstrap.Modal.getInstance(elements.progressModal);
    if (modalInstance) {
        modalInstance.hide();
    }
}

/**
 * Handle progress modal hidden event
 */
function handleProgressModalHidden() {
    if (progressInterval) {
        clearInterval(progressInterval);
        progressInterval = null;
    }
}

/**
 * Show/Hide forms
 */
function showYouTubeForm() {
    hideAllForms();
    elements.youtubeForm?.classList.remove('d-none');
    elements.youtubeUrl?.focus();
}

function showLocalForm() {
    hideAllForms();
    elements.localForm?.classList.remove('d-none');
    elements.transcriptFile?.focus();
}

function hideAllForms() {
    elements.youtubeForm?.classList.add('d-none');
    elements.localForm?.classList.add('d-none');
}

/**
 * Reset forms
 */
function resetForms() {
    // Reset YouTube form
    const youtubeForm = document.getElementById('youtube-processing-form');
    if (youtubeForm) {
        youtubeForm.reset();
        elements.youtubeUrl?.classList.remove('is-valid', 'is-invalid');
    }
    
    // Reset local form
    const localForm = document.getElementById('local-processing-form');
    if (localForm) {
        localForm.reset();
    }
    
    // Remove file info
    const fileInfo = document.getElementById('file-info');
    if (fileInfo) {
        fileInfo.remove();
    }
    
    // Clear validation feedback
    document.querySelectorAll('.valid-feedback, .invalid-feedback').forEach(el => el.remove());
    
    // Reset global state
    currentTaskId = null;
    startTime = null;
}

/**
 * Show validation feedback
 */
function showValidationFeedback(element, message, type) {
    // Remove existing feedback
    const existingFeedback = element.parentNode.querySelector(`.${type}-feedback`);
    if (existingFeedback) {
        existingFeedback.remove();
    }
    
    // Add new feedback
    const feedback = document.createElement('div');
    feedback.className = `${type}-feedback`;
    feedback.textContent = message;
    
    element.parentNode.appendChild(feedback);
}

/**
 * Show alert message
 */
function showAlert(message, type = 'info') {
    // Create alert element
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        <i class="bi bi-${getAlertIcon(type)} me-2"></i>
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    // Insert at top of main content
    const main = document.querySelector('main.container');
    if (main) {
        main.insertBefore(alertDiv, main.firstChild);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.classList.remove('show');
                setTimeout(() => alertDiv.remove(), 150);
            }
        }, 5000);
    }
}

/**
 * Get alert icon based on type
 */
function getAlertIcon(type) {
    const icons = {
        success: 'check-circle',
        danger: 'exclamation-triangle',
        warning: 'exclamation-triangle',
        info: 'info-circle'
    };
    return icons[type] || 'info-circle';
}

/**
 * Set button loading state
 */
function setButtonLoading(button, loading) {
    if (loading) {
        button.disabled = true;
        button.innerHTML = `
            <span class="spinner-border spinner-border-sm me-2" role="status"></span>
            Traitement...
        `;
    } else {
        button.disabled = false;
        // Restore original text based on button context
        const isYouTube = button.closest('#youtube-processing-form');
        button.innerHTML = isYouTube 
            ? '<i class="bi bi-magic me-2"></i>Générer le Cours SOTA'
            : '<i class="bi bi-lightning-charge me-2"></i>Convertir en Cours SOTA';
    }
}

/**
 * Debounce utility function
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Utility function to format file size
 */
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// Make functions globally available for onclick handlers
window.showYouTubeForm = showYouTubeForm;
window.showLocalForm = showLocalForm;
window.hideAllForms = hideAllForms;