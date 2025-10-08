# Implementation Plan

- [x] 1. Add store type field to edit template
  - Modify `templates/lojas/editar.html` to include the `tipo_loja` field rendering
  - Position the field logically within the existing form layout (after basic info, before address)
  - Follow the established template pattern for field rendering and error handling
  - Ensure proper Bootstrap styling and responsive layout
  - _Requirements: 1.1, 1.2, 2.1, 2.2, 2.3_

- [x] 2. Verify and test create template consistency
  - Check if `templates/lojas/criar.html` already includes the store type field
  - If missing, add the store type field to maintain consistency between create and edit forms
  - Ensure both templates use the same field rendering pattern
  - _Requirements: 3.1, 3.2_

- [x] 3. Test form functionality and data persistence
  - Create automated tests to verify the store type field saves correctly
  - Test that existing store types are properly pre-selected in edit mode
  - Verify form validation and error handling for the store type field
  - Test both create and edit operations to ensure consistency
  - _Requirements: 1.3, 2.4, 3.3, 3.4_

- [x] 4. Verify form configuration and styling
  - Review `lojas/forms.py` to ensure optimal LojaForm configuration for tipo_loja field
  - Confirm proper widget styling and empty label text
  - Ensure the field queries available store types correctly
  - Test dropdown functionality and option display
  - _Requirements: 1.4, 2.1, 2.4_