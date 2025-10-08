# Implementation Plan

- [x] 1. Analyze and map plan models relationship
  - Examine PlanoComercial and PlanoFinanceiro models to understand their structure
  - Determine the best approach for mapping between the two plan systems
  - Create helper functions to convert between plan types if needed
  - _Requirements: 2.1, 2.2, 2.3_

- [x] 2. Enhance LojaForm with plan selection
  - Add plano_comercial field to LojaForm with proper validation
  - Update form widgets and styling for plan selection dropdown
  - Add form validation to ensure plan selection is required
  - _Requirements: 1.1, 1.2, 1.3, 1.4_

- [x] 3. Update store creation template with plan selection UI
  - Modify the criar_loja template to include plan selection field
  - Add JavaScript to show plan details when a plan is selected
  - Display plan information (name, price, features) to help with selection
  - _Requirements: 3.1, 3.2, 3.3_

- [x] 4. Modify criar_loja view to handle plan selection
  - Update the view to load available plans for the form
  - Modify the store creation logic to use the selected plan
  - Ensure both ControleFinanceiro and AssinaturaLoja are created with the selected plan
  - _Requirements: 1.1, 1.2, 2.1, 2.2, 2.3, 2.4_

- [x] 5. Implement atomic transaction for consistent record creation
  - Wrap store creation logic in database transaction
  - Ensure both financial control records are created or both fail
  - Update error handling to provide meaningful feedback on failures
  - _Requirements: 2.4_

- [x] 6. Create management command to fix existing inconsistent stores
  - Identify stores with ControleFinanceiro but missing AssinaturaLoja
  - Create AssinaturaLoja records based on existing ControleFinanceiro data
  - Preserve existing financial information during the fix process
  - _Requirements: 4.1, 4.2, 4.3, 4.4_

- [x] 7. Update store listing to identify inconsistent stores
  - Modify the store list view to identify stores missing AssinaturaLoja
  - Add visual indicators for stores that need fixing
  - Provide action buttons to fix inconsistent stores from the admin interface
  - _Requirements: 4.1, 4.2_

- [ ]* 7.1 Add unit tests for plan selection functionality
  - Test form validation with and without plan selection
  - Test store creation with different plan types
  - Test transaction rollback on creation failures
  - _Requirements: 1.1, 1.2, 2.1, 2.2_

- [ ]* 7.2 Add integration tests for complete workflow
  - Test end-to-end store creation with plan selection
  - Verify both dashboard and detail views show consistent information
  - Test existing store identification and fixing functionality
  - _Requirements: 2.1, 2.2, 4.1, 4.4_