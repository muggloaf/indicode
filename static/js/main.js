/**
 * INDICODE - Main JavaScript
 * =========================
 * 
 * This is the main JavaScript file for the indicode application, handling all client-side 
 * functionality including UI initialization, form handling, API interactions, and user interactions.
 * 
 * Features:
 * - Bootstrap UI component initialization (tooltips, popovers)
 * - Form validation and submission
 * - API communication for transliteration and translation
 * - File handling and document processing
 * - User feedback and correction submission
 * - History and settings management
 */

/**
 * Initialize all functionality when the DOM is fully loaded
 */
document.addEventListener('DOMContentLoaded', function() {
    
    //---------------------------------------------------------------
    // BOOTSTRAP UI COMPONENT INITIALIZATION
    //---------------------------------------------------------------
    
    // Initialize Bootstrap tooltips for better UX
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });    
    
    // Initialize Bootstrap popovers for additional info display
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'))
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl)
    });
    
    //---------------------------------------------------------------
    // PAGE SCROLL HANDLING & TEXTAREA POSITIONING
    //---------------------------------------------------------------
    
    // Add scroll detection to fix positioning issues with textareas
    // This prevents layout issues during scrolling
    let scrollTimeout;
    window.addEventListener('scroll', function() {
        // Add scrolling class to root for potential CSS adjustments
        document.documentElement.classList.add('scrolling');
        
        // Ensure all textareas maintain proper positioning during scroll
        document.querySelectorAll('textarea').forEach(textarea => {
            textarea.classList.add('scrolls-with-page');
            textarea.style.position = 'relative';
        });
        
        // Remove scrolling class after scrolling stops (with debounce)
        clearTimeout(scrollTimeout);
        scrollTimeout = setTimeout(function() {
            document.documentElement.classList.remove('scrolling');
        }, 100); // 100ms debounce
    });
    
    // Initialize all textareas with proper positioning
    document.querySelectorAll('textarea').forEach(textarea => {
        textarea.classList.add('scrolls-with-page');
        textarea.style.position = 'relative';
    });    
    
    // All features are now available for free
    window.showPremiumAlert = function() {
        // This function is now empty as all features are free
    };

    // Animated scroll to anchors
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            if(this.getAttribute('href') !== "#" && !this.getAttribute('data-bs-toggle')) {
                e.preventDefault();
                
                const targetId = this.getAttribute('href');
                const targetElement = document.querySelector(targetId);
                
                if(targetElement) {
                    window.scrollTo({
                        top: targetElement.offsetTop - 70,
                        behavior: 'smooth'
                    });
                }
            }
        });
    });

    // Character counter for text areas
    document.querySelectorAll('textarea').forEach(textarea => {
        textarea.addEventListener('input', function() {
            const counterEl = document.getElementById(this.id + '-counter');
            if(counterEl) {
                counterEl.textContent = this.value.length;
                
                // Add visual indicator for character limit
                if(this.hasAttribute('maxlength')) {
                    const maxLength = parseInt(this.getAttribute('maxlength'));
                    const percentage = (this.value.length / maxLength) * 100;
                    
                    if(percentage > 90) {
                        counterEl.classList.add('text-danger');
                        counterEl.classList.remove('text-warning', 'text-muted');
                    } else if(percentage > 75) {
                        counterEl.classList.add('text-warning');
                        counterEl.classList.remove('text-danger', 'text-muted');
                    } else {
                        counterEl.classList.add('text-muted');
                        counterEl.classList.remove('text-danger', 'text-warning');
                    }
                }
            }
        });
    });

    // Add animation to elements when they come into view
    const animateOnScroll = () => {
        const elements = document.querySelectorAll('.animate-on-scroll');
        
        elements.forEach(element => {
            const elementPosition = element.getBoundingClientRect();
            const windowHeight = window.innerHeight;
            
            if(elementPosition.top < windowHeight - 50) {
                element.classList.add('fade-in');
                element.classList.remove('animate-on-scroll');
            }
        });
    };

    // Call once on load
    animateOnScroll();
    
    // Add scroll event listener
    window.addEventListener('scroll', animateOnScroll);

    // Handle form submissions
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!this.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            
            this.classList.add('was-validated');
        });
    });    
    
    // Check for stored data upon page load (for dashboard history integration)
    if(sessionStorage.getItem('indicate_success')) {
        const alertEl = document.createElement('div');
        alertEl.className = 'alert alert-success alert-dismissible fade show notification-toast';
        alertEl.innerHTML = `
            <strong><i class="fas fa-check-circle me-2"></i>Success!</strong>
            <span>${sessionStorage.getItem('indicate_success')}</span>
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        
        document.body.appendChild(alertEl);
        
        // Auto dismiss after 4 seconds
        setTimeout(() => {
            alertEl.classList.remove('show');
            setTimeout(() => alertEl.remove(), 300);
        }, 4000);
        
        // Remove from session storage
        sessionStorage.removeItem('indicate_success');
    }
});

// Function to detect the language of input text (simplified version)
function detectLanguage(text) {
    // Hindi range: \u0900-\u097F
    const hindiPattern = /[\u0900-\u097F]/;
    
    // Check if text contains Hindi characters
    if (hindiPattern.test(text)) {
        return 'hindi';
    }
    
    return 'english';
}

// Function to show a notification
function showNotification(message, type = 'success') {
    const alertEl = document.createElement('div');
    alertEl.className = `alert alert-${type} alert-dismissible fade show notification-toast`;
    alertEl.innerHTML = `
        <span>${message}</span>
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    // Add to document (always append to body for fixed positioning)
    document.body.appendChild(alertEl);
    
    // Auto dismiss after 4 seconds
    setTimeout(() => {
        alertEl.classList.remove('show');
        setTimeout(() => alertEl.remove(), 300);
    }, 4000);
}

// Analytics tracking (placeholder - would be replaced with actual analytics in a real app)
function trackEvent(category, action, label = null) {
    console.log(`Analytics Event: ${category} - ${action}` + (label ? ` - ${label}` : ''));
    
    // This would be replaced with actual analytics code like Google Analytics
    // Example: gtag('event', action, {'event_category': category, 'event_label': label});
}

// Enhanced Transliteration & translation logic
// Handle guest transliteration
const guestTransliterateBtn = document.getElementById('guest-transliterate-btn');
if (guestTransliterateBtn) {
    guestTransliterateBtn.addEventListener('click', function() {
        const inputText = document.getElementById('guest-input-text').value;
        const inputLanguage = document.getElementById('guest-input-language').value;
        const outputTextArea = document.getElementById('guest-output-text');
        const outputLabel = document.getElementById('guest-output-label');        
        
        // Get feature flags from advanced options
        const contextAware = document.getElementById('context-aware-switch')?.checked ?? true;
        const statisticalSchwa = document.getElementById('statistical-schwa-switch')?.checked ?? true;
        const autoExceptions = document.getElementById('auto-exceptions-switch')?.checked ?? true;
        const autoCapitalization = document.getElementById('auto-capitalization-switch')?.checked ?? true;
        
        // Show loading state
        this.disabled = true;
        this.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Processing...';
        outputTextArea.value = 'Processing...';
        
        // Prepare form data
        const formData = new FormData();
        formData.append('input_text', inputText);
        formData.append('language', inputLanguage);
        formData.append('context_aware', contextAware.toString());
        formData.append('statistical_schwa', statisticalSchwa.toString());
        formData.append('auto_exceptions', autoExceptions.toString());
        formData.append('auto_capitalization', autoCapitalization.toString());
        
        // Make the request
        fetch('/transliterate', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            // Reset button state
            this.disabled = false;
            this.innerHTML = '<i class="fas fa-sync-alt me-2"></i>Transliterate';
            
            if (data.error) {
                outputTextArea.value = `Error: ${data.error}`;
                showNotification(data.error, 'danger');
            } else {
                outputTextArea.value = data.output;
                outputLabel.textContent = 'Transliterated Text';
                
                // Show the feedback container
                const feedbackContainer = document.getElementById('feedback-container');
                feedbackContainer.style.display = 'block';
                feedbackContainer.classList.add('scrolls-with-page');
                // Pre-fill the corrected text with the current output
                document.getElementById('corrected-text').value = data.output;
                
                // Track event
                trackEvent('transliteration', 'guest_transliterate', inputLanguage);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            this.disabled = false;
            this.innerHTML = '<i class="fas fa-sync-alt me-2"></i>Transliterate';
            outputTextArea.value = 'An error occurred. Please try again.';
            showNotification('Failed to connect to the server. Please try again.', 'danger');
        });
    });
}

// Handle feedback submission
const submitFeedbackBtn = document.getElementById('submit-feedback');
if (submitFeedbackBtn) {
    submitFeedbackBtn.addEventListener('click', function() {
        // First check if user can submit feedback
        fetch('/check_feedback_access')
        .then(response => response.json())
        .then(accessData => {
            if (!accessData.can_submit) {
                showNotification('Please log in to provide feedback', 'warning');
                return;
            }
            
            // User is authenticated, proceed with feedback submission
            const originalText = document.getElementById('guest-input-text').value;
            const autoTransliteration = document.getElementById('guest-output-text').value;
            const correctedTransliteration = document.getElementById('corrected-text').value;
            const language = document.getElementById('guest-input-language').value;
            
            // Don't submit if no changes were made
            if (autoTransliteration === correctedTransliteration) {
                showNotification('Please make changes to the transliteration before submitting feedback', 'warning');
                return;
            }
            
            // Show loading state
            this.disabled = true;
            this.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Submitting...';
            
            // Prepare form data
            const formData = new FormData();
            formData.append('original_text', originalText);
            formData.append('auto_transliteration', autoTransliteration);
            formData.append('corrected_transliteration', correctedTransliteration);
            formData.append('language', language);
            
            // Make the request
            fetch('/feedback', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                // Reset button state
                this.disabled = false;
                this.innerHTML = '<i class="fas fa-paper-plane me-1"></i>Submit Correction';
                
                if (data.status === 'error') {
                    showNotification(data.message, 'danger');
                } else {
                    showNotification(data.message, 'success');
                    // Update the output text with the corrected version
                    document.getElementById('guest-output-text').value = correctedTransliteration;
                    // Hide the feedback container
                    document.getElementById('feedback-container').style.display = 'none';
                }
            })
            .catch(error => {
                console.error('Error:', error);
                this.disabled = false;
                this.innerHTML = '<i class="fas fa-paper-plane me-1"></i>Submit Correction';
                showNotification('Failed to submit feedback. Please try again.', 'danger');
            });
        })
        .catch(error => {
            console.error('Error checking access:', error);
            showNotification('Please log in to provide feedback', 'warning');
        });
    });
}

// Initialize the transliteration form handlers
document.addEventListener('DOMContentLoaded', function() {
    // Batch Processing Handler
    const batchForm = document.getElementById('batchForm');
    if (batchForm) {
        batchForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const uploadButton = document.getElementById('upload-button');
            const progressDiv = document.getElementById('upload-progress');
            const errorDiv = document.getElementById('upload-error');
            const successDiv = document.getElementById('upload-success');
            const normalText = uploadButton.querySelector('.normal-text');
            const processingText = uploadButton.querySelector('.processing-text');
            
            // Reset UI
            errorDiv.classList.add('d-none');
            errorDiv.textContent = '';
            successDiv.classList.add('d-none');
            successDiv.textContent = '';
            
            // Show loading state
            uploadButton.disabled = true;
            normalText.classList.add('d-none');
            processingText.classList.remove('d-none');
            progressDiv.classList.remove('d-none');
            
            try {
                const formData = new FormData(this);
                
                const response = await fetch('/batch_process', {
                    method: 'POST',
                    body: formData
                });
                
                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(errorData.error || 'Failed to process file');
                }
                
                // Get the filename from the Content-Disposition header
                const contentDisposition = response.headers.get('Content-Disposition');
                let filename = 'transliterated_document';
                if (contentDisposition) {
                    const filenameMatch = contentDisposition.match(/filename\s*=\s*"?([^";\n]*)"/i);
                    if (filenameMatch && filenameMatch[1]) {
                        filename = filenameMatch[1];
                    }
                }
                
                // Create blob and download
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.style.display = 'none';
                a.href = url;
                a.download = filename;
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                a.remove();
                
                // Show success message
                successDiv.textContent = 'File processed successfully! Downloading...';
                successDiv.classList.remove('d-none');
                
                // Reset form
                this.reset();
                
            } catch (error) {
                console.error('Upload error:', error);
                errorDiv.textContent = error.message || 'An error occurred during file processing';
                errorDiv.classList.remove('d-none');
            } finally {
                // Reset UI
                uploadButton.disabled = false;
                normalText.classList.remove('d-none');
                processingText.classList.add('d-none');
                progressDiv.classList.add('d-none');
            }
        });
        
        // File input validation
        const fileInput = batchForm.querySelector('input[type="file"]');
        if (fileInput) {
            fileInput.addEventListener('change', function() {
                const file = this.files[0];
                const errorDiv = document.getElementById('upload-error');
                
                if (file) {
                    const ext = file.name.split('.').pop().toLowerCase();
                    const allowedTypes = ['txt', 'docx', 'pdf'];
                    
                    if (!allowedTypes.includes(ext)) {
                        errorDiv.textContent = 'Please select a valid file type (.txt, .docx, or .pdf)';
                        errorDiv.classList.remove('d-none');
                        this.value = '';
                    } else {
                        errorDiv.classList.add('d-none');
                        errorDiv.textContent = '';
                    }
                }
            });
        }
    }
});

// File Upload Handling
document.addEventListener('DOMContentLoaded', function() {
    const uploadForm = document.getElementById('upload-form');
    if (uploadForm) {
        uploadForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const uploadButton = document.getElementById('upload-button');
            const progressDiv = document.getElementById('upload-progress');
            const errorDiv = document.getElementById('upload-error');
            const successDiv = document.getElementById('upload-success');
            const normalText = uploadButton.querySelector('.normal-text');
            const processingText = uploadButton.querySelector('.processing-text');
            
            // Reset UI
            errorDiv.classList.add('d-none');
            errorDiv.textContent = '';
            successDiv.classList.add('d-none');
            successDiv.textContent = '';
            
            // Show loading state
            uploadButton.disabled = true;
            normalText.classList.add('d-none');
            processingText.classList.remove('d-none');
            progressDiv.classList.remove('d-none');
            
            try {
                const formData = new FormData(this);
                
                const response = await fetch('/batch_process', {
                    method: 'POST',
                    body: formData,
                    credentials: 'include'
                });
                
                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(errorData.error || 'Failed to process file');
                }
                
                // Get the filename from the response headers
                const contentDisposition = response.headers.get('Content-Disposition');
                let filename = 'translated_document';
                if (contentDisposition) {
                    const filenameMatch = contentDisposition.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/);
                    if (filenameMatch && filenameMatch[1]) {
                        filename = filenameMatch[1].replace(/['"]/g, '');
                    }
                }
                
                // Create blob and download
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.style.display = 'none';
                a.href = url;
                a.download = filename;
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                a.remove();
                
                // Show success message
                successDiv.textContent = 'File processed successfully! Downloading...';
                successDiv.classList.remove('d-none');
                
            } catch (error) {
                console.error('Upload error:', error);
                errorDiv.textContent = error.message || 'An error occurred during file processing';
                errorDiv.classList.remove('d-none');
            } finally {
                // Reset UI
                uploadButton.disabled = false;
                normalText.classList.remove('d-none');
                processingText.classList.add('d-none');
                progressDiv.classList.add('d-none');
            }
        });
        
        // File input validation
        const fileInput = uploadForm.querySelector('input[type="file"]');
        fileInput.addEventListener('change', function() {
            const file = this.files[0];
            const errorDiv = document.getElementById('upload-error');
            
            if (file) {
                const ext = file.name.split('.').pop().toLowerCase();
                const allowedTypes = ['txt', 'docx', 'pdf'];
                
                if (!allowedTypes.includes(ext)) {
                    errorDiv.textContent = 'Please select a valid file type (.txt, .docx, or .pdf)';
                    errorDiv.classList.remove('d-none');
                    this.value = '';
                } else {
                    errorDiv.classList.add('d-none');
                }
            }
        });
    }
});

/**
 * Confirmation function for deleting user's transliteration history
 * Shows a confirmation dialog and submits the form if confirmed
 */
function confirmDeleteHistory() {
    if (confirm('Are you sure you want to delete all your transliteration history? This action cannot be undone.')) {
        // If confirmed, submit the form
        document.getElementById('delete-history-form').submit();
    }
}

/**
 * Confirmation function for deleting user's account
 * Shows a confirmation dialog and submits the form if confirmed
 */
function confirmDeleteAccount() {
    if (confirm('WARNING: You are about to delete your account. This will permanently remove all your data and cannot be undone. Are you sure you want to proceed?')) {
        // If confirmed, submit the form
        document.getElementById('delete-account-form').submit();
    }
}
