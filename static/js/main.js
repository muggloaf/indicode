/**
 * indicode - Main JavaScript
 * Enhanced version with support for advanced transliteration features
 */

document.addEventListener('DOMContentLoaded', function() {
    
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });

    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'))
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl)
    });
      // Add scroll detection for fixing position issues
    let scrollTimeout;
    window.addEventListener('scroll', function() {
        document.documentElement.classList.add('scrolling');
        
        // Ensure all textareas are properly positioned while scrolling
        document.querySelectorAll('textarea').forEach(textarea => {
            textarea.classList.add('scrolls-with-page');
            textarea.style.position = 'relative';
        });
        
        clearTimeout(scrollTimeout);
        scrollTimeout = setTimeout(function() {
            document.documentElement.classList.remove('scrolling');
        }, 100);
    });
    
    // Initialize all textareas with proper positioning
    document.querySelectorAll('textarea').forEach(textarea => {
        textarea.classList.add('scrolls-with-page');
        textarea.style.position = 'relative';
    });// Global function for Premium features
    window.showPremiumAlert = function() {
        const alertEl = document.createElement('div');
        alertEl.className = 'alert alert-warning alert-dismissible fade show notification-toast';
        alertEl.innerHTML = `
            <strong><i class="fas fa-crown me-2"></i>Premium Feature!</strong>
            <p class="mb-0">This is a premium feature. Please upgrade your account to access it.</p>
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        document.body.appendChild(alertEl);
        
        // Auto dismiss after 4 seconds
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alertEl);
            bsAlert.close();
        }, 4000);
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
    });    // Check for stored data upon page load (for dashboard history integration)
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
        const outputLabel = document.getElementById('guest-output-label');        // Get feature flags from advanced options
        const contextAware = document.getElementById('context-aware-switch')?.checked ?? true;
        const statisticalSchwa = document.getElementById('statistical-schwa-switch')?.checked ?? true;
        const autoExceptions = document.getElementById('auto-exceptions-switch')?.checked ?? true;
        const autoCapitalization = document.getElementById('auto-capitalization-switch')?.checked ?? true;
        
        // Show loading state
        this.disabled = true;
        this.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Processing...';
        outputTextArea.value = 'Processing...';
        
        // Prepare form data
        const formData = new FormData();        formData.append('input_text', inputText);
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
    });
}