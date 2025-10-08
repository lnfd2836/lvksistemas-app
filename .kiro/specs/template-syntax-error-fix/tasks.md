# Implementation Plan

- [x] 1. Fix template syntax error in store detail template
  - Update the conditional syntax in `templates/lojas/detalhar.html` from `==` to proper Django template syntax
  - Replace `{% if loja.status=="ativa" %}` with `{% if loja.status == "ativa" %}` (with proper spacing)
  - Apply the same fix to "inativa" and "suspensa" status comparisons
  - _Requirements: 1.1, 1.2, 1.3, 2.1, 2.2_

- [x] 2. Verify template renders correctly
  - Test that the template loads without TemplateSyntaxError
  - Ensure the correct status option is pre-selected based on store status
  - Validate that all three status options (ativa, inativa, suspensa) work correctly
  - _Requirements: 1.1, 1.2, 3.1, 3.3_

- [ ]* 2.1 Create template syntax tests
  - Write unit tests to verify template renders without syntax errors
  - Test template with different status values (ativa, inativa, suspensa, None)
  - Create regression tests to prevent similar syntax errors in the future
  - _Requirements: 1.1, 2.2_

- [x] 3. Search and fix any other template syntax issues
  - Scan all template files for similar `=="` syntax errors
  - Fix any other instances of incorrect comparison operators in templates
  - Ensure consistent Django template syntax across the application
  - _Requirements: 2.1, 2.2_

- [ ]* 3.1 Add template validation to CI/CD
  - Create a script to validate Django template syntax
  - Add template syntax checking to the development workflow
  - Document proper Django template syntax guidelines for the team
  - _Requirements: 2.1, 2.2_