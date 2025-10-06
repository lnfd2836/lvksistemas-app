# Design Document

## Overview

The application is experiencing a Django TemplateSyntaxError when rendering the lojas listing page (`/lojas/`). The error occurs in the `templates/lojas/listar.html` template at line 127, where the template syntax `{% if status_filter=='ativa' %}selected{% endif %}` is malformed according to Django's template parser.

The issue is that Django template language doesn't support the `==` operator for string comparisons in the same way as Python. Instead, Django templates require proper spacing and use different comparison syntax.

## Root Cause Analysis

1. **Template Syntax Error**: The line `{% if status_filter=='ativa' %}selected{% endif %}` uses incorrect syntax
2. **Django Template Language**: Django templates require proper spacing around operators and use different comparison methods
3. **Multiple Occurrences**: The same pattern appears on lines 127, 129, and 130 for different status values
4. **Production Impact**: This error prevents users from accessing the lojas listing page, which is critical functionality

## Architecture

The fix involves correcting the Django template syntax in the `templates/lojas/listar.html` file. The solution will:

1. **Template Syntax Correction**: Replace `==` comparisons with proper Django template syntax
2. **Consistent Pattern**: Apply the same fix to all similar comparisons in the template
3. **Validation**: Ensure the template renders correctly with various filter values
4. **Testing**: Verify the fix works in both development and production environments

## Components and Interfaces

### Affected Components

1. **Template File**: `templates/lojas/listar.html`
   - Lines 127, 129, 130 contain the malformed syntax
   - Status filter dropdown options need correction

2. **View Function**: `lojas.views.listar_lojas`
   - Passes `status_filter` context variable to template
   - No changes needed to view logic

3. **URL Pattern**: `lojas/urls.py`
   - No changes needed to URL configuration

### Template Syntax Solutions

Django templates support several approaches for string comparison:

#### Option 1: Using the `|default` filter with string comparison
```django
<option value="ativa" {% if status_filter == "ativa" %}selected{% endif %}>Ativa</option>
```

#### Option 2: Using proper spacing (recommended)
```django
<option value="ativa" {% if status_filter == "ativa" %}selected{% endif %}>Ativa</option>
```

#### Option 3: Using the `|yesno` filter
```django
<option value="ativa" {{ status_filter|yesno:"selected," }}>Ativa</option>
```

The recommended approach is Option 2, which uses proper spacing around the `==` operator.

## Data Models

No changes to data models are required. The issue is purely a template syntax problem.

## Error Handling

### Current Error
- **Error Type**: `django.template.exceptions.TemplateSyntaxError`
- **Error Message**: `Could not parse the remainder: '=='ativa'' from 'status_filter=='ativa''`
- **Location**: `templates/lojas/listar.html:127`

### Prevention Measures
1. **Template Validation**: Implement template syntax validation in development
2. **Testing**: Add template rendering tests to catch syntax errors
3. **Code Review**: Establish template syntax guidelines for the team

## Testing Strategy

### Unit Tests
1. **Template Rendering Test**: Verify the template renders without errors
2. **Filter Functionality Test**: Test status filtering with different values
3. **Context Variable Test**: Ensure `status_filter` is properly passed to template

### Integration Tests
1. **View Response Test**: Test the complete `/lojas/` endpoint
2. **Filter Parameter Test**: Test URL parameters for status filtering
3. **User Permission Test**: Verify superuser access requirements

### Manual Testing
1. **Development Environment**: Test template rendering locally
2. **Production Deployment**: Verify fix works on Heroku
3. **Browser Testing**: Test dropdown functionality across browsers

### Test Cases

```python
def test_listar_lojas_template_renders_without_error(self):
    """Test that the lojas listing template renders without syntax errors"""
    
def test_status_filter_selection_active(self):
    """Test that 'ativa' status filter shows as selected"""
    
def test_status_filter_selection_inactive(self):
    """Test that 'inativa' status filter shows as selected"""
    
def test_status_filter_selection_suspended(self):
    """Test that 'suspensa' status filter shows as selected"""
    
def test_no_status_filter_no_selection(self):
    """Test that no option is selected when no filter is applied"""
```

## Implementation Plan

### Phase 1: Template Syntax Fix
1. Correct the malformed template syntax in `templates/lojas/listar.html`
2. Apply consistent formatting to all status filter options
3. Verify template syntax is valid

### Phase 2: Testing
1. Create template rendering tests
2. Test filter functionality
3. Verify fix in development environment

### Phase 3: Deployment
1. Deploy fix to production
2. Monitor for any remaining template errors
3. Verify functionality works correctly

## Security Considerations

No security implications for this fix. The change is purely cosmetic template syntax correction.

## Performance Considerations

No performance impact. The fix corrects syntax without changing functionality or adding computational overhead.

## Backward Compatibility

The fix maintains full backward compatibility. The corrected template syntax produces the same HTML output as intended by the original code.