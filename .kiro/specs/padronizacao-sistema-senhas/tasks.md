# Implementation Plan

Convert the feature design into a series of prompts for a code-generation LLM that will implement each step with incremental progress. Make sure that each prompt builds on the previous prompts, and ends with wiring things together. There should be no hanging or orphaned code that isn't integrated into a previous step. Focus ONLY on tasks that involve writing, modifying, or testing code.

- [ ] 1. Create core infrastructure for email credentials system with multi-database support
  - Create EmailCredentialsService class with methods for sending credentials to different user types
  - Implement PasswordGenerator utility class with secure password generation
  - Create EmailTemplateService for managing email templates
  - Create EmailSender class with error handling and logging
  - Implement DatabaseRouter for routing queries to individual loja databases
  - _Requirements: 1.1, 1.4, 2.1, 2.2, 3.1, 3.2, 3.3, 14.1, 14.2_

- [ ] 1.1 Create base models for user profile extension with multi-database support
  - Create ExtendedUserProfile model in main database for access control
  - Create LojaUserProfile model for individual loja databases
  - Add database routing configuration for loja isolation
  - Create EmailLog model for audit trail
  - Generate and apply database migrations for main and loja databases
  - _Requirements: 3.4, 3.5, 9.1, 9.2, 13.1, 13.2, 13.3, 14.1, 14.2_

- [ ] 1.2 Implement password generation and validation
  - Create secure password generation with configurable length
  - Add password strength validation
  - Implement uniqueness checking
  - Add unit tests for password generation
  - _Requirements: 3.1, 3.2, 3.3_

- [ ] 1.3 Create email template system
  - Design HTML email templates for super admin credentials
  - Design HTML email templates for loja admin credentials  
  - Design HTML email templates for loja user credentials
  - Design HTML email template for password recovery
  - Implement template selection logic based on user type and loja type
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 11.5_

- [ ] 1.4 Implement email sending with error handling
  - Create EmailSender class with SMTP integration
  - Add comprehensive error handling and retry logic
  - Implement fallback to display credentials on screen
  - Add email logging for audit purposes
  - _Requirements: 8.1, 8.2, 8.3, 9.3, 9.4_

- [ ] 2. Integrate with Super Admin creation system
  - Modify dashboard views for super admin creation to use EmailCredentialsService
  - Update super admin creation forms to remove password fields
  - Add automatic profile creation with provisional password marking
  - Test super admin creation with email sending
  - _Requirements: 1.1, 6.3_

- [ ] 2.1 Update super admin creation workflow
  - Modify criar_usuario_super_admin view to use new service
  - Remove manual password generation from existing code
  - Add proper error handling for email failures
  - Update success messages to reflect email sending
  - _Requirements: 1.1, 8.1, 8.2_

- [ ] 2.2 Create super admin email template
  - Design professional email template for super admin credentials
  - Include system access instructions and security guidelines
  - Add company branding and contact information
  - Test template rendering with sample data
  - _Requirements: 5.1, 5.5_

- [ ] 3. Integrate with Loja creation system
  - Modify loja creation views to use EmailCredentialsService for admin users
  - Update loja admin creation to send credentials via email
  - Preserve existing loja creation functionality while adding email
  - Test loja creation with different loja types
  - _Requirements: 1.2, 6.2, 11.1, 11.2, 11.3, 11.4_

- [ ] 3.1 Update loja creation workflow
  - Modify criar_loja view to use EmailCredentialsService
  - Remove password display from success messages
  - Add loja context to email templates
  - Handle email failures gracefully with fallback display
  - _Requirements: 1.2, 8.1, 8.3_

- [ ] 3.2 Create loja admin email template
  - Design email template specific to loja administrators
  - Include loja-specific information and branding
  - Add instructions for loja management system access
  - Customize content based on loja type
  - _Requirements: 5.2, 11.5_

- [ ] 4. Update existing FATESA user creation system
  - Modify existing FATESA user creation to use centralized EmailCredentialsService
  - Maintain existing functionality while standardizing email sending
  - Update forms and views to use new service
  - Ensure backward compatibility with existing FATESA users
  - _Requirements: 1.3, 6.1, 6.5_

- [ ] 4.1 Refactor FATESA user creation with loja isolation
  - Update CadastroUsuarioForm to use EmailCredentialsService
  - Ensure users are automatically associated with admin's loja
  - Add loja access profile selection (secretaria, coordenacao, professor)
  - Maintain strict loja isolation for FATESA users
  - _Requirements: 1.3, 6.1, 11.5, 13.1, 13.2, 13.3_

- [ ] 4.2 Update FATESA email template
  - Adapt existing FATESA email template to new template system
  - Ensure FATESA-specific content is preserved
  - Add loja context for FATESA users
  - Test with different FATESA loja configurations
  - _Requirements: 5.3, 11.4_

- [ ] 5. Implement password recovery system
  - Create password recovery views for "Forgot Password" functionality
  - Add recovery forms with email/username input
  - Implement recovery logic with rate limiting
  - Create recovery email template and sending logic
  - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5_

- [ ] 5.1 Create password recovery views
  - Create forgot_password view with form handling
  - Implement user lookup by email or username
  - Add rate limiting to prevent abuse
  - Create success and error pages for recovery flow
  - _Requirements: 10.1, 10.2_

- [ ] 5.2 Implement recovery email system
  - Generate new provisional password for recovery
  - Send recovery email with new credentials
  - Mark user for mandatory password change
  - Log recovery attempts for security monitoring
  - _Requirements: 10.3, 10.4, 10.5_

- [ ] 5.3 Add recovery links to login pages
  - Add "Esqueceu a senha?" button to all login forms
  - Update login templates across all modules
  - Ensure consistent styling and placement
  - Test recovery flow from different login pages
  - _Requirements: 10.1_

- [ ] 6. Create password change enforcement middleware
  - Implement PasswordRecoveryMiddleware to force password changes
  - Add logic to detect provisional passwords
  - Create secure redirect handling for password change
  - Integrate with existing authentication middleware
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_

- [ ] 6.1 Implement middleware for password enforcement
  - Create middleware class to intercept requests
  - Add logic to check for provisional passwords
  - Implement secure redirects to password change page
  - Add exception handling for excluded URLs
  - _Requirements: 4.1, 4.2_

- [ ] 6.2 Create password change views and forms
  - Create unified password change view for provisional passwords
  - Implement form that doesn't require current password for first change
  - Add password strength validation
  - Create success flow after password change
  - _Requirements: 4.3, 4.4, 4.5_

- [ ] 6.3 Update password change templates
  - Create user-friendly password change templates
  - Add clear instructions for first-time password change
  - Include password requirements and security tips
  - Ensure responsive design across devices
  - _Requirements: 4.3, 5.4_

- [ ] 7. Add configuration and settings management
  - Create Django settings for email credentials system
  - Add environment variable support for configuration
  - Implement feature flags for gradual rollout
  - Create admin interface for system configuration
  - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_

- [ ] 7.1 Create configuration system
  - Add EMAIL_CREDENTIALS_CONFIG to Django settings
  - Implement environment variable parsing
  - Create configuration validation
  - Add default values for all settings
  - _Requirements: 7.1, 7.2_

- [ ] 7.2 Implement feature flags
  - Add ability to enable/disable email sending
  - Create fallback mechanisms when disabled
  - Add per-module configuration options
  - Implement gradual rollout capabilities
  - _Requirements: 7.3_

- [ ] 8. Create data migration for existing users across multiple databases
  - Create migration script to update existing users in main database
  - Add ExtendedUserProfile for all existing users
  - Create LojaUserProfile in individual loja databases for existing loja users
  - Set appropriate user types and loja associations with database routing
  - Mark existing passwords as permanent (not provisional)
  - Ensure data consistency across main and individual loja databases
  - _Requirements: 12.1, 12.2, 12.3, 12.4, 14.3, 14.4_

- [ ] 8.1 Implement user migration script
  - Create Django management command for migration
  - Identify all existing users and their contexts
  - Create ExtendedUserProfile records for existing users
  - Set correct user_type based on user permissions and associations
  - _Requirements: 12.1, 12.2_

- [ ] 8.2 Handle existing password states
  - Mark all existing user passwords as permanent
  - Preserve current login functionality for existing users
  - Add option to reset specific users to provisional state
  - Test migration with sample data
  - _Requirements: 12.3, 12.4, 12.5_

- [ ] 9. Add comprehensive logging and monitoring
  - Implement detailed logging for all email operations
  - Create audit trail for password changes and recovery
  - Add monitoring for email success rates and failures
  - Create admin dashboard for system monitoring
  - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5_

- [ ] 9.1 Implement audit logging system
  - Create comprehensive logging for all user creation events
  - Log email sending attempts and results
  - Add IP tracking and user agent logging
  - Create log rotation and cleanup procedures
  - _Requirements: 9.1, 9.2, 9.4_

- [ ] 9.2 Create monitoring dashboard
  - Build admin interface for viewing email logs
  - Add statistics for email success rates
  - Create alerts for high failure rates
  - Implement log search and filtering
  - _Requirements: 9.3, 9.5_

- [ ]* 10. Create comprehensive test suite
  - Write unit tests for all service classes
  - Create integration tests for complete user flows
  - Add performance tests for email sending under load
  - Create end-to-end tests for password recovery
  - _Requirements: All requirements_

- [ ]* 10.1 Unit tests for core services
  - Test EmailCredentialsService with different user types
  - Test PasswordGenerator for security and uniqueness
  - Test EmailTemplateService template selection
  - Test EmailSender error handling and fallbacks
  - _Requirements: 1.1, 1.2, 1.3, 1.4_

- [ ]* 10.2 Integration tests for user workflows
  - Test complete super admin creation flow
  - Test complete loja creation flow
  - Test complete FATESA user creation flow
  - Test password recovery end-to-end flow
  - _Requirements: 1.1, 1.2, 1.3, 10.1-10.5_

- [ ]* 10.3 Performance and security tests
  - Test email sending performance under load
  - Test rate limiting for password recovery
  - Test middleware performance impact
  - Test security of password generation and storage
  - _Requirements: 3.1, 3.2, 3.3, 10.2_

- [ ] 11. Final integration and deployment preparation
  - Integrate all components into unified system
  - Update all existing user creation flows to use new service
  - Add comprehensive error handling and fallbacks
  - Prepare deployment scripts and documentation
  - _Requirements: All requirements_

- [ ] 11.1 System integration
  - Wire all services together into cohesive system
  - Update all user creation entry points
  - Ensure consistent behavior across all modules
  - Add comprehensive error handling at integration points
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_

- [ ] 11.2 Update middleware registration
  - Add PasswordRecoveryMiddleware to Django settings
  - Configure middleware order for proper functionality
  - Test middleware integration with existing auth system
  - Ensure no conflicts with existing middleware
  - _Requirements: 4.1, 6.4_

- [ ] 11.3 Final testing and validation
  - Test complete system with all user types
  - Validate email templates across different scenarios
  - Test error handling and fallback mechanisms
  - Perform security validation of password handling
  - _Requirements: All requirements_

- [ ] 11.4 Documentation and deployment
  - Create deployment guide for new system
  - Document configuration options and environment variables
  - Create troubleshooting guide for common issues
  - Prepare rollback procedures if needed
  - _Requirements: 7.5, 8.1, 8.2, 8.3_