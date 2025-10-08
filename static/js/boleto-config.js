/**
 * Boleto Configuration Form State Management
 * Handles showing/hiding the configuration form and managing user interactions
 */

class BoletoConfigManager {
    constructor() {
        this.formContainer = document.getElementById('config-form-container');
        this.toggleButton = document.getElementById('toggle-form-btn');
        this.addNewButton = document.getElementById('add-new-config-btn');
        this.cancelButton = document.getElementById('cancel-form-btn');
        this.configForm = document.getElementById('boleto-config-form');
        this.configSummary = document.getElementById('config-summary');
        
        this.init();
    }
    
    init() {
        // Bind event listeners
        this.bindEvents();
        
        // Initialize form state based on server-side data
        this.initializeFormState();
        
        // Load user preferences from localStorage
        this.loadUserPreferences();
    }
    
    bindEvents() {
        // Toggle form button
        if (this.toggleButton) {
            this.toggleButton.addEventListener('click', (e) => {
                e.preventDefault();
                this.toggleConfigForm();
            });
        }
        
        // Add new configuration button
        if (this.addNewButton) {
            this.addNewButton.addEventListener('click', (e) => {
                e.preventDefault();
                this.showConfigForm(true); // true = reset form
            });
        }
        
        // Cancel button
        if (this.cancelButton) {
            this.cancelButton.addEventListener('click', (e) => {
                e.preventDefault();
                this.hideConfigForm();
            });
        }
        
        // Form submission handling
        if (this.configForm) {
            this.configForm.addEventListener('submit', (e) => {
                this.onFormSubmit(e);
            });
        }
        
        // Edit configuration buttons - use event delegation for dynamic content
        document.addEventListener('click', (e) => {
            if (e.target.closest('.edit-config-btn')) {
                e.preventDefault();
                const btn = e.target.closest('.edit-config-btn');
                const configId = btn.dataset.configId;
                this.editConfiguration(configId);
            }
        });
    }
    
    initializeFormState() {
        // Only initialize if form container exists
        if (!this.formContainer) {
            return;
        }
        
        // Get initial state from server-side template variables
        const hasConfigurations = window.boletoConfigData?.hasConfigurations || false;
        const showForm = window.boletoConfigData?.showForm || false;
        const formErrors = window.boletoConfigData?.formErrors || false;
        const editing = window.boletoConfigData?.editing || false;
        
        // Determine initial visibility
        if (showForm || formErrors || !hasConfigurations || editing) {
            this.showConfigForm(false);
        } else {
            this.hideConfigForm();
        }
    }
    
    toggleConfigForm() {
        if (this.isFormVisible()) {
            this.hideConfigForm();
        } else {
            this.showConfigForm(false);
        }
    }
    
    showConfigForm(resetForm = false) {
        if (!this.formContainer) return;
        
        // Reset form if requested
        if (resetForm && this.configForm) {
            this.resetForm();
        }
        
        // Show form with smooth animation
        this.formContainer.style.display = 'block';
        this.formContainer.classList.remove('config-form-hidden');
        this.formContainer.classList.add('config-form-visible');
        
        // Update button states
        this.updateButtonStates(true);
        
        // Focus on first input
        const firstInput = this.configForm?.querySelector('input[type="text"]');
        if (firstInput) {
            setTimeout(() => firstInput.focus(), 300);
        }
        
        // Save preference
        this.saveUserPreference('form-visible');
        
        // Scroll to form
        this.scrollToForm();
    }
    
    hideConfigForm() {
        if (!this.formContainer) return;
        
        // Hide form with smooth animation
        this.formContainer.classList.remove('config-form-visible');
        this.formContainer.classList.add('config-form-hidden');
        
        // Update button states
        this.updateButtonStates(false);
        
        // Save preference
        this.saveUserPreference('form-hidden');
        
        // Hide after animation completes
        setTimeout(() => {
            if (this.formContainer.classList.contains('config-form-hidden')) {
                this.formContainer.style.display = 'none';
            }
        }, 300);
    }
    
    isFormVisible() {
        if (!this.formContainer) return false;
        return this.formContainer.classList.contains('config-form-visible') || 
               (this.formContainer.style.display !== 'none' && 
                !this.formContainer.classList.contains('config-form-hidden'));
    }
    
    resetForm() {
        if (!this.configForm) return;
        
        // Reset all form fields
        this.configForm.reset();
        
        // Clear any error states
        this.configForm.querySelectorAll('.is-invalid').forEach(field => {
            field.classList.remove('is-invalid');
        });
        
        // Clear error messages
        this.configForm.querySelectorAll('.invalid-feedback').forEach(msg => {
            msg.style.display = 'none';
        });
        
        // Remove config_id if present (for new configurations)
        const configIdField = this.configForm.querySelector('input[name="config_id"]');
        if (configIdField) {
            configIdField.remove();
        }
        
        // Update form title
        const formTitle = document.querySelector('#config-form-title');
        if (formTitle) {
            formTitle.textContent = 'Nova Configuração de Boleto';
        }
    }
    
    updateButtonStates(formVisible) {
        // Update toggle button text
        if (this.toggleButton) {
            const icon = this.toggleButton.querySelector('i');
            const text = this.toggleButton.querySelector('.btn-text');
            
            if (formVisible) {
                if (icon) icon.className = 'fas fa-eye-slash';
                if (text) text.textContent = 'Ocultar Formulário';
                this.toggleButton.classList.remove('btn-primary');
                this.toggleButton.classList.add('btn-secondary');
            } else {
                if (icon) icon.className = 'fas fa-plus';
                if (text) text.textContent = 'Nova Configuração';
                this.toggleButton.classList.remove('btn-secondary');
                this.toggleButton.classList.add('btn-primary');
            }
        }
        
        // Show/hide add new button
        if (this.addNewButton) {
            this.addNewButton.style.display = formVisible ? 'none' : 'inline-block';
        }
    }
    
    editConfiguration(configId) {
        // Redirect to edit page with show_form parameter
        const editUrl = `/financeiro/boletos/configurar/${configId}/`;
        window.location.href = editUrl;
    }
    
    onFormSubmit(event) {
        // Save that form was submitted for state management
        this.saveUserPreference('form-submitted');
        
        // Let the form submit normally
        return true;
    }
    
    scrollToForm() {
        if (this.formContainer) {
            this.formContainer.scrollIntoView({ 
                behavior: 'smooth', 
                block: 'start' 
            });
        }
    }
    
    saveUserPreference(state) {
        try {
            localStorage.setItem('boleto-config-form-state', state);
        } catch (e) {
            // localStorage not available, ignore
            console.warn('Could not save form state preference:', e);
        }
    }
    
    loadUserPreferences() {
        try {
            const savedState = localStorage.getItem('boleto-config-form-state');
            
            // Only apply saved preference if no server-side override
            if (savedState && !window.boletoConfigData?.showForm && !window.boletoConfigData?.formErrors) {
                if (savedState === 'form-visible') {
                    this.showConfigForm(false);
                } else if (savedState === 'form-hidden') {
                    this.hideConfigForm();
                }
            }
        } catch (e) {
            // localStorage not available, ignore
            console.warn('Could not load form state preference:', e);
        }
    }
    
    // Public methods for external use
    static getInstance() {
        if (!window.boletoConfigManager) {
            window.boletoConfigManager = new BoletoConfigManager();
        }
        return window.boletoConfigManager;
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    // Initialize the manager
    BoletoConfigManager.getInstance();
});

// Export for external use
window.BoletoConfigManager = BoletoConfigManager;