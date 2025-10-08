# Design Document

## Overview

This design addresses the missing "Tipo de Loja" (Store Type) field in the store edit template. The issue is that while the backend properly supports store types through the LojaForm and Loja model, the frontend template (`templates/lojas/editar.html`) does not render this field, making it impossible for users to edit the store type.

## Architecture

The fix involves a simple template modification without requiring changes to the backend logic, as the form and model already support the store type functionality correctly.

### Current State Analysis
- **LojaForm**: Already includes `tipo_loja` in the fields list ✓
- **Loja Model**: Has proper ForeignKey relationship to `modulos.TipoLoja` ✓
- **Edit View**: Uses LojaForm correctly ✓
- **Edit Template**: Missing the `tipo_loja` field rendering ✗

## Components and Interfaces

### Template Modification
The `templates/lojas/editar.html` template needs to be updated to include the store type field rendering.

**Location for the field**: The store type field should be positioned logically within the form, ideally after the basic store information (name, CNPJ) but before the address section.

**Field Structure**: Following the existing pattern used by other fields in the template:
```html
<div class="col-md-6 mb-3">
    <label for="{{ form.tipo_loja.id_for_label }}" class="form-label">{{ form.tipo_loja.label }}</label>
    {{ form.tipo_loja }}
    {% if form.tipo_loja.errors %}
        <div class="text-danger">{{ form.tipo_loja.errors.0 }}</div>
    {% endif %}
</div>
```

### Form Configuration Verification
Ensure the LojaForm properly configures the tipo_loja field with:
- Appropriate widget styling (`form-control` class)
- Helpful empty label text
- Proper queryset for available store types

## Data Models

No changes required to data models as they already support the functionality:

- **Loja Model**: Contains `tipo_loja` ForeignKey to `modulos.TipoLoja`
- **TipoLoja Model**: Properly defined with choices and display methods

## Error Handling

### Template Error Handling
- Display validation errors consistently with other fields
- Handle cases where no store types are available
- Graceful handling of missing or invalid store type selections

### Form Validation
- Leverage existing Django form validation
- Ensure proper error messages are displayed for invalid selections

## Testing Strategy

### Manual Testing
1. **Edit Form Rendering**: Verify the store type field appears in the edit form
2. **Field Population**: Confirm existing store type is pre-selected when editing
3. **Save Functionality**: Test that changes to store type are persisted
4. **Error Display**: Verify error messages display correctly for validation failures

### Template Verification
1. **Visual Consistency**: Ensure the field matches the styling of other form fields
2. **Responsive Layout**: Verify the field works properly on different screen sizes
3. **Accessibility**: Confirm proper label association and form structure

### Cross-Reference Testing
1. **Create Form**: Verify the create form also works correctly (should already work)
2. **List View**: Confirm store type displays correctly in the store list
3. **Detail View**: Verify store type shows in the store detail view

## Implementation Approach

### Phase 1: Template Update
1. Add the store type field to the edit template
2. Position it appropriately within the existing form layout
3. Follow the established pattern for field rendering and error handling

### Phase 2: Form Enhancement (if needed)
1. Verify the LojaForm configuration is optimal
2. Ensure proper widget styling and empty label
3. Add any necessary form customizations

### Phase 3: Testing and Validation
1. Test the edit functionality thoroughly
2. Verify both create and edit forms work correctly
3. Confirm data persistence and error handling

## Risk Mitigation

### Low Risk Implementation
This is a low-risk change as it only involves adding a missing template field that the backend already supports.

### Rollback Strategy
If issues arise, the change can be easily reverted by removing the added template code.

### Compatibility
The change maintains full backward compatibility as it only adds missing functionality without modifying existing behavior.