# Implementation Plan

- [x] 1. Fix template syntax errors in lojas listing template
  - Correct the malformed Django template syntax on lines 127, 129, and 130 in `templates/lojas/listar.html`
  - Replace `status_filter=='ativa'` with proper Django template syntax `status_filter == "ativa"`
  - Apply consistent spacing and quoting for all status filter comparisons
  - _Requirements: 1.1, 1.2, 2.2_

- [x] 2. Create template rendering tests to prevent future syntax errors
  - Write unit test to verify `templates/lojas/listar.html` renders without TemplateSyntaxError
  - Create test cases for different status filter values (ativa, inativa, suspensa, none)
  - Test that correct option is marked as selected based on status_filter context variable
  - _Requirements: 3.1, 3.2, 4.1, 4.2, 4.3_

- [x] 3. Validate template syntax and functionality
  - Run template rendering tests to ensure syntax is correct
  - Test the lojas listing page with different status filter parameters
  - Verify dropdown selections work correctly for all status values
  - _Requirements: 1.1, 1.3, 4.1, 4.2, 4.3_