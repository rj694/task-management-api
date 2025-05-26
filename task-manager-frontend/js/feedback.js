// js/feedback.js
const feedback = {
    // Show success message
    showSuccess(message, duration = 3000) {
        const existingToast = document.querySelector('.toast');
        if (existingToast) existingToast.remove();
        
        const toast = document.createElement('div');
        toast.className = 'toast toast-success';
        toast.innerHTML = `
            <i class="fas fa-check-circle"></i>
            <span>${message}</span>
        `;
        document.body.appendChild(toast);
        
        setTimeout(() => toast.classList.add('show'), 10);
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        }, duration);
    },
    
    // Show error message with user-friendly text
    showError(error, context = '') {
        const existingToast = document.querySelector('.toast');
        if (existingToast) existingToast.remove();
        
        // Map technical errors to user-friendly messages
        let userMessage = this.getUserFriendlyError(error, context);
        
        const toast = document.createElement('div');
        toast.className = 'toast toast-error';
        toast.innerHTML = `
            <i class="fas fa-exclamation-circle"></i>
            <span>${userMessage}</span>
        `;
        document.body.appendChild(toast);
        
        setTimeout(() => toast.classList.add('show'), 10);
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        }, 5000);
    },
    
    // Convert technical errors to user-friendly messages
    getUserFriendlyError(error, context) {
        const errorMessage = error.message || error;
        
        // Network errors
        if (errorMessage.includes('NetworkError') || errorMessage.includes('Failed to fetch')) {
            return 'Unable to connect to the server. Please check your internet connection and try again.';
        }
        
        // Authentication errors
        if (errorMessage.includes('Token has expired')) {
            return 'Your session has expired. Please log in again.';
        }
        if (errorMessage.includes('Authorization required')) {
            return 'Please log in to access this feature.';
        }
        if (errorMessage.includes('Invalid credentials')) {
            return 'Incorrect email or password. Please try again.';
        }
        
        // Permission errors
        if (errorMessage.includes('Admin privileges required')) {
            return 'You need administrator privileges to perform this action.';
        }
        if (errorMessage.includes('permission')) {
            return 'You don\'t have permission to perform this action.';
        }
        
        // Validation errors
        if (errorMessage.includes('already exists')) {
            if (context === 'tag') return 'A tag with this name already exists. Please choose a different name.';
            if (context === 'user') return 'This email or username is already registered.';
            return 'This item already exists. Please choose a different name.';
        }
        
        // Rate limiting
        if (errorMessage.includes('Rate limit exceeded')) {
            return 'You\'re making too many requests. Please wait a moment and try again.';
        }
        
        // Not found errors
        if (errorMessage.includes('not found')) {
            if (context === 'task') return 'This task no longer exists. It may have been deleted.';
            if (context === 'tag') return 'This tag no longer exists.';
            if (context === 'comment') return 'This comment no longer exists.';
            return 'The requested item could not be found.';
        }
        
        // Generic fallback
        return `Something went wrong${context ? ` while ${context}` : ''}. Please try again.`;
    },
    
    // Show loading state
    showLoading(element, text = 'Loading...') {
        const original = element.innerHTML;
        element.innerHTML = `<i class="fas fa-spinner fa-spin"></i> ${text}`;
        element.disabled = true;
        return () => {
            element.innerHTML = original;
            element.disabled = false;
        };
    },
    
    // Show inline validation error
    showFieldError(fieldId, message) {
        const field = document.getElementById(fieldId);
        if (!field) return;
        
        // Remove any existing error
        const existingError = field.parentElement.querySelector('.field-error');
        if (existingError) existingError.remove();
        
        // Add error message
        const errorDiv = document.createElement('div');
        errorDiv.className = 'field-error';
        errorDiv.textContent = message;
        field.parentElement.appendChild(errorDiv);
        field.classList.add('error');
    },
    
    // Clear field error
    clearFieldError(fieldId) {
        const field = document.getElementById(fieldId);
        if (!field) return;
        
        const existingError = field.parentElement.querySelector('.field-error');
        if (existingError) existingError.remove();
        field.classList.remove('error');
    },
    
    // Show confirmation dialog
    confirm(message, onConfirm, onCancel = () => {}) {
        const modal = document.createElement('div');
        modal.className = 'confirmation-modal';
        modal.innerHTML = `
            <div class="confirmation-content">
                <h3>Confirm Action</h3>
                <p>${message}</p>
                <div class="confirmation-buttons">
                    <button class="btn btn-outline" id="cancel-btn">Cancel</button>
                    <button class="btn btn-danger" id="confirm-btn">Confirm</button>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        setTimeout(() => modal.classList.add('show'), 10);
        
        const cleanup = () => {
            modal.classList.remove('show');
            setTimeout(() => modal.remove(), 300);
        };
        
        document.getElementById('cancel-btn').onclick = () => {
            cleanup();
            onCancel();
        };
        
        document.getElementById('confirm-btn').onclick = () => {
            cleanup();
            onConfirm();
        };
    }
};