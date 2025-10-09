# Implementation Plan

- [x] 1. Analyze and document current functionality usage
  - Identify all references to the "Pagar com Código" functionality in the codebase
  - Document the current modal implementation in dashboard.html
  - Map the processar_pagamento_codigo_barras view and its dependencies
  - Verify URL configuration and routing for the payment code feature
  - _Requirements: 1.1, 1.2, 1.3_

- [x] 2. Remove frontend components from dashboard template
  - [x] 2.1 Remove the "Pagar com Código" button from dashboard header
    - Delete the button element with data-bs-target="#pagarCodigoBarrasModal"
    - Remove the associated icon and text elements
    - _Requirements: 4.1, 4.2, 5.1_

  - [x] 2.2 Remove the payment code modal from dashboard template
    - Delete the entire pagarCodigoBarrasModal div and its contents
    - Remove the form with action pointing to processar_pagamento_codigo_barras
    - Clean up any associated JavaScript event handlers
    - _Requirements: 4.1, 4.2, 5.2_

  - [x] 2.3 Clean up any remaining HTML references
    - Search for any other references to the modal or payment code functionality
    - Remove unused CSS classes or styles related to the modal
    - _Requirements: 4.3, 5.3_

- [x] 3. Remove backend view and URL configuration
  - [x] 3.1 Remove processar_pagamento_codigo_barras view from views.py
    - Delete the entire view function and its logic
    - Remove any imports that are no longer needed
    - _Requirements: 4.1, 4.2_

  - [x] 3.2 Remove URL pattern from urls.py
    - Delete the path for 'pagamento-codigo-barras/'
    - Remove the URL name 'processar_pagamento_codigo_barras'
    - _Requirements: 4.1, 4.3_

  - [x] 3.3 Clean up any remaining backend references
    - Search for any other references to the removed view
    - Remove unused imports or dependencies
    - _Requirements: 4.3, 4.4_

- [x] 4. Verify and enhance alternative payment confirmation methods
  - [x] 4.1 Test the "Marcar como Pago" functionality in boleto listing
    - Verify the marcar_boleto_pago view works correctly
    - Test the confirmation dialog and success messages
    - Ensure proper permission checks are in place
    - _Requirements: 2.1, 2.2, 3.1_

  - [x] 4.2 Test payment confirmation in boleto details page
    - Verify the payment confirmation button in boleto_detalhes.html
    - Test the form submission and redirect behavior
    - Ensure audit trail is properly maintained
    - _Requirements: 2.1, 2.2, 3.2_

  - [x] 4.3 Test quick actions in dashboard boleto list
    - Verify the quick action buttons work for recent boletos
    - Test the confirmation dialogs and user feedback
    - Ensure consistent behavior across all payment methods
    - _Requirements: 2.1, 3.1, 3.3_

- [x] 5. Update and improve user interface consistency
  - [x] 5.1 Enhance visual feedback for payment confirmations
    - Improve success/error message styling and positioning
    - Add consistent confirmation dialogs across all payment methods
    - Ensure loading states are properly handled
    - _Requirements: 2.3, 5.1, 5.2_

  - [x] 5.2 Optimize dashboard layout after button removal
    - Adjust button group spacing and alignment
    - Ensure remaining buttons are properly styled
    - Test responsive behavior on different screen sizes
    - _Requirements: 5.1, 5.3, 5.5_

- [x] 6. Perform comprehensive testing
  - [x] 6.1 Execute regression tests for payment functionality
    - Test all alternative payment confirmation methods
    - Verify that boleto status updates correctly
    - Ensure financial control updates are working
    - _Requirements: 2.4, 2.5, 4.5_

  - [x] 6.2 Test user interface and user experience
    - Verify dashboard loads correctly without the removed components
    - Test all remaining boleto management features
    - Ensure no broken links or JavaScript errors
    - _Requirements: 5.1, 5.4, 5.5_

  - [ ]* 6.3 Perform user acceptance testing
    - Test complete admin workflow for boleto management
    - Verify that removal doesn't impact productivity
    - Gather feedback on interface simplification
    - _Requirements: 5.1, 5.2, 5.4_

- [x] 7. Documentation and cleanup
  - [x] 7.1 Update system documentation
    - Remove references to "Pagar com Código" from user guides
    - Update admin documentation with alternative methods
    - Document the change in system changelog
    - _Requirements: 4.3, 5.5_

  - [x] 7.2 Clean up any remaining code references
    - Search entire codebase for any missed references
    - Remove unused imports or variables
    - Update comments that reference the removed functionality
    - _Requirements: 4.3, 4.4_

  - [ ]* 7.3 Performance validation
    - Measure dashboard load time before and after removal
    - Verify that page performance has improved
    - Document performance improvements achieved
    - _Requirements: 4.5, 5.5_