# Design Document

## Overview

This design document outlines the improvements to the boleto configuration interface to provide a better user experience by dynamically showing/hiding the configuration form based on the current state and user actions. The solution will maintain all existing functionality while providing a cleaner, more intuitive interface.

## Architecture

### Frontend Components

The solution will be implemented using a combination of:
- **Django Template Logic**: Server-side rendering decisions based on existing configurations
- **JavaScript/CSS**: Client-side interactions for form toggling and smooth transitions
- **Bootstrap Classes**: Responsive design and consistent styling
- **Session State Management**: Remembering user preferences for form visibility

### Backend Logic

The existing Django view `configurar_boletos` will be enhanced to:
- Determine initial form state based on existing configurations
- Handle form submission success states
- Provide appropriate context variables for template rendering

## Components and Interfaces

### 1. Enhanced Template Structure

**File**: `templates/controle_financeiro/configurar_boletos.html`

The template will be restructured with:
- **Configuration Summary Section**: Always visible, shows current active configuration
- **Collapsible Form Section**: Can be shown/hidden based on state
- **Action Buttons**: Toggle form visibility and manage configurations
- **Existing Configurations Panel**: Enhanced to be more prominent when form is hidden

### 2. Form State Management

**States**:
- `show-form`: Form is visible (default when no configurations exist)
- `hide-form`: Form is collapsed (default when configurations exist)
- `edit-mode`: Form is visible with pre-populated data for editing

**Triggers**:
- Page load with existing configurations → `hide-form`
- Page load without configurations → `show-form`
- Successful form submission → `hide-form`
- "Add New Configuration" button → `show-form`
- "Edit Configuration" button → `edit-mode`
- Form validation errors → `show-form` with errors

### 3. JavaScript Interactions

**Functions**:
- `toggleConfigForm()`: Show/hide the configuration form
- `showConfigForm()`: Explicitly show the form
- `hideConfigForm()`: Explicitly hide the form
- `resetForm()`: Clear form fields when adding new configuration

### 4. CSS Styling

**Classes**:
- `.config-form-container`: Container for the configuration form
- `.config-form-hidden`: Class to hide the form with smooth transition
- `.config-summary`: Prominent display of current configuration
- `.toggle-form-btn`: Styling for form toggle buttons

## Data Models

No changes to existing data models are required. The solution will work with the existing:
- `ConfiguracaoBoleto` model
- Form handling in the `configurar_boletos` view

## Error Handling

### Form Validation Errors
- **Behavior**: Always show the form when validation errors occur
- **Implementation**: Check for form errors in template and override hide state
- **User Experience**: Clear error messages with form visible for correction

### JavaScript Errors
- **Fallback**: Ensure form remains functional even if JavaScript fails
- **Progressive Enhancement**: Basic functionality works without JavaScript

### Session Management
- **State Persistence**: Use localStorage to remember user's form visibility preference
- **Fallback**: Default to appropriate state based on existing configurations

## Testing Strategy

### Unit Tests
1. **View Tests**: Test form submission and state determination logic
2. **Template Tests**: Verify correct rendering based on different states
3. **JavaScript Tests**: Test form toggle functionality

### Integration Tests
1. **User Flow Tests**: Complete workflow from viewing to configuring boletos
2. **State Transition Tests**: Verify correct behavior when switching between states
3. **Error Handling Tests**: Ensure proper behavior with validation errors

### Manual Testing Scenarios
1. **New Installation**: No configurations exist, form should be visible
2. **Existing Configuration**: Form should be hidden, configurations visible
3. **Form Submission**: Successful submission should hide form
4. **Edit Configuration**: Should show form with pre-populated data
5. **Validation Errors**: Should show form with error messages
6. **Multiple Configurations**: Should handle multiple configurations correctly

## Implementation Details

### Template Logic Flow

```html
<!-- Determine initial state -->
{% if configuracoes and not form_errors %}
    <!-- Hide form by default -->
    <div class="config-form-container" style="display: none;">
{% else %}
    <!-- Show form by default -->
    <div class="config-form-container">
{% endif %}
```

### JavaScript State Management

```javascript
// Initialize form state based on server-side decision
const hasConfigurations = {{ configuracoes|length }} > 0;
const hasErrors = {{ form_errors|yesno:"true,false" }};
const initialState = hasConfigurations && !hasErrors ? 'hidden' : 'visible';
```

### CSS Transitions

```css
.config-form-container {
    transition: all 0.3s ease-in-out;
    overflow: hidden;
}

.config-form-hidden {
    max-height: 0;
    opacity: 0;
    margin: 0;
    padding: 0;
}
```

### Enhanced Configuration Display

When the form is hidden, the existing configurations panel will be enhanced to:
- Show more prominent active configuration details
- Provide quick action buttons
- Display configuration status more clearly
- Include summary statistics if applicable

### Responsive Behavior

The solution will maintain responsive design:
- **Desktop**: Side-by-side layout with form and configurations
- **Mobile**: Stacked layout with collapsible form taking full width
- **Tablet**: Adaptive layout based on screen size

This design ensures a smooth, intuitive user experience while maintaining all existing functionality and providing clear visual feedback for all user actions.