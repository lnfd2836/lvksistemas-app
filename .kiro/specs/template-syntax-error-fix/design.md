# Design Document

## Overview

This design addresses the Django template syntax error caused by using Python comparison operators (`==`) instead of proper Django template syntax. The error occurs in the store detail template (`templates/lojas/detalhar.html`) where conditional logic is used to pre-select the current status in a dropdown.

## Architecture

The fix involves updating the template syntax to use Django's proper conditional template tags. Django templates use different syntax for comparisons than Python code.

### Current Problem
- Template uses `{% if loja.status=="ativa" %}` which is invalid Django template syntax
- Django template parser cannot handle the `==` operator in this context
- This causes a TemplateSyntaxError that prevents the page from loading

### Solution Approach
- Replace `==` comparisons with Django's `ifequal` tag or proper `if` tag syntax
- Use Django template filters for string comparison
- Maintain the same functionality while using correct syntax

## Components and Interfaces

### Template Layer
- **File**: `templates/lojas/detalhar.html`
- **Lines affected**: 561-563
- **Current syntax**: `{% if loja.status=="ativa" %}`
- **Correct syntax options**:
  1. `{% if loja.status == "ativa" %}` (with spaces around ==)
  2. `{% ifequal loja.status "ativa" %}`
  3. Using custom template filter if needed

### Django Template Engine
- The Django template engine expects specific syntax for conditionals
- String comparisons in templates require proper spacing or specific tags
- The `ifequal` tag is designed specifically for equality comparisons

## Data Models

### Store Model
- **Field**: `status` (CharField with choices)
- **Values**: "ativa", "inativa", "suspensa"
- **Usage**: Compared in template to determine selected option

## Error Handling

### Template Syntax Validation
- Ensure all template syntax follows Django conventions
- Test template rendering with different status values
- Verify no other templates have similar syntax issues

### Fallback Behavior
- If status is None or empty, no option should be pre-selected
- Template should handle edge cases gracefully
- Form should still be functional even if comparison fails

## Testing Strategy

### Template Rendering Tests
- Test template renders without syntax errors
- Verify correct option is selected for each status value
- Test with edge cases (None, empty string, invalid status)

### Integration Tests
- Test the complete status change workflow
- Verify form submission works correctly
- Test modal functionality remains intact

### Manual Testing
- Load store detail page for stores with different statuses
- Verify modal opens and displays correct selected option
- Test status change functionality end-to-end

## Implementation Details

### Syntax Fix Options

**Option 1: Proper if tag syntax**
```django
{% if loja.status == "ativa" %}selected{% endif %}
```

**Option 2: ifequal tag**
```django
{% ifequal loja.status "ativa" %}selected{% endif %}
```

**Option 3: Using template filter**
```django
{% if loja.status|default:"" == "ativa" %}selected{% endif %}
```

### Recommended Approach
Use Option 1 (proper if tag syntax) as it's the most modern and readable approach in current Django versions. The `ifequal` tag is deprecated in newer Django versions.

## Security Considerations

- No security implications as this is a template syntax fix
- Existing CSRF protection remains in place
- No changes to data validation or processing logic

## Performance Impact

- Minimal performance impact
- Template rendering will be slightly more efficient without syntax errors
- No additional database queries or processing overhead