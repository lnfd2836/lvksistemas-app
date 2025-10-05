# Design Document

## Overview

The URL routing errors are caused by missing URL patterns that templates are trying to reference. After analyzing the codebase, I identified two main issues:

1. **Missing URL patterns**: Templates reference URL names that don't exist in the URL configuration
2. **Namespace inconsistencies**: Some templates use URL names without proper namespace prefixes

The solution involves adding the missing URL patterns and ensuring consistent naming conventions across the application.

## Architecture

The Django URL routing system follows a hierarchical structure:
- **Root URLs** (`lojad/urls.py`) - Main project URL configuration
- **App URLs** - Individual app URL configurations (dashboard, lojas, etc.)
- **Namespaced URLs** - URLs with app namespaces for better organization

## Components and Interfaces

### 1. URL Pattern Analysis

**Current Issues Identified:**

1. **`dashboard_loja_id` reference** in `templates/lojas/listar.html`:
   - Template uses: `{% url 'dashboard:loja_especifica' loja.id %}`
   - This URL pattern exists and is correctly named
   - The error suggests the template might be using a different reference

2. **Missing URL patterns** in `templates/dashboard/usuarios_super_admin.html`:
   - `editar_usuario_super_admin` - Template references this but URL pattern is named `admin_usuarios_editar`
   - `alterar_senha_usuario_super_admin` - Template references this but URL pattern is named `admin_usuarios_alterar_senha`
   - `excluir_usuario_super_admin` - Template references this but URL pattern is named `admin_usuarios_excluir`

3. **Namespace issues with `criar_loja` references**:
   - `templates/dashboard/super_admin.html` uses: `{% url 'criar_loja' %}` (missing namespace)
   - `templates/planos/listar.html` uses: `{% url 'criar_loja' %}` (missing namespace)
   - Should be: `{% url 'lojas:criar_loja' %}` (with proper namespace)
   - This causes `NoReverseMatch` errors when super admin users access the dashboard

### 2. URL Pattern Mapping

**Dashboard URLs (dashboard/urls.py):**
- Existing: `admin_usuarios_editar`
- Template expects: `editar_usuario_super_admin`

**Required Changes:**
1. Add URL pattern aliases for backward compatibility
2. Update template references to use correct namespace and names
3. Ensure consistent naming conventions

### 3. Template URL Reference Patterns

**Current Pattern:**
```html
{% url 'editar_usuario_super_admin' usuario.id %}
```

**Should be:**
```html
{% url 'dashboard:admin_usuarios_editar' usuario.id %}
```

## Data Models

No data model changes are required. This is purely a URL routing and template reference issue.

## Error Handling

### 1. URL Resolution Errors
- **Current**: `NoReverseMatch` exceptions cause 500 errors
- **Solution**: Add proper URL patterns and fix template references

### 2. Missing URL Pattern Detection
- **Implementation**: Add URL pattern validation during development
- **Fallback**: Provide meaningful error messages for missing patterns

### 3. Template Reference Validation
- **Strategy**: Use consistent namespace prefixes
- **Validation**: Ensure all URL references use proper Django URL naming conventions

## Testing Strategy

### 1. URL Pattern Testing
- **Unit Tests**: Test each URL pattern resolves correctly
- **Integration Tests**: Test template rendering with correct URL generation
- **Regression Tests**: Ensure existing functionality remains intact

### 2. Template Rendering Tests
- **Test Cases**: 
  - Store listing page renders without errors
  - User management page renders without errors
  - All URL references resolve correctly

### 3. Error Handling Tests
- **Scenarios**:
  - Missing URL patterns
  - Invalid URL parameters
  - Namespace resolution issues

## Implementation Plan

### Phase 1: Fix Template References
1. Update `templates/dashboard/usuarios_super_admin.html` to use correct URL names with namespace
2. Verify `templates/lojas/listar.html` URL references

### Phase 2: Add Missing URL Patterns (if needed)
1. Add URL pattern aliases for backward compatibility
2. Ensure all referenced URL patterns exist

### Phase 3: Validation and Testing
1. Test all affected pages
2. Verify URL resolution works correctly
3. Add regression tests

## URL Pattern Corrections Needed

### Dashboard URLs
```python
# Current template references (incorrect):
'editar_usuario_super_admin'
'alterar_senha_usuario_super_admin' 
'excluir_usuario_super_admin'

# Correct URL names (with namespace):
'dashboard:admin_usuarios_editar'
'dashboard:admin_usuarios_alterar_senha'
'dashboard:admin_usuarios_excluir'
```

### Store Management URLs
```python
# Current (incorrect in some templates):
'criar_loja'  # Missing namespace in dashboard/super_admin.html and planos/listar.html

# Correct (with namespace):
'lojas:criar_loja'

# Already correct:
'dashboard:loja_especifica'
```

## Security Considerations

- **URL Parameter Validation**: Ensure user IDs and store IDs are properly validated
- **Permission Checks**: Maintain existing permission decorators on views
- **CSRF Protection**: Ensure all forms maintain CSRF token protection

## Performance Impact

- **Minimal Impact**: URL routing fixes have negligible performance impact
- **Template Rendering**: Proper URL resolution improves template rendering efficiency
- **Error Reduction**: Fewer 500 errors improve overall application performance