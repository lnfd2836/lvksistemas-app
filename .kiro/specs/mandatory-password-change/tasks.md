# Implementation Plan

- [x] 1. Add password management fields to PerfilUsuario model
  - Add requires_password_change boolean field with default False
  - Add provisional_password_created datetime field
  - Add password_changed_at datetime field  
  - Add password_change_reminders_sent integer field with default 0
  - Create and run database migration
  - _Requirements: 3.1, 3.2_

- [x] 2. Update user creation signals to set password change requirement
  - Modify usuarios/signals.py to set requires_password_change=True for new users
  - Set provisional_password_created timestamp when creating provisional passwords
  - Ensure super admin and store admin users are marked for password change
  - Test signal behavior with different user types
  - _Requirements: 1.1, 2.1_

- [x] 3. Create mandatory password change form and validation
  - Create MandatoryPasswordChangeForm extending Django's PasswordChangeForm
  - Add custom password strength validation (minimum 8 chars, letters + numbers)
  - Customize field labels and help text for Portuguese
  - Add form validation for password requirements
  - _Requirements: 4.2, 4.4_

- [x] 4. Implement password change views and templates
  - Create change_mandatory_password view with proper authentication
  - Create template with clear instructions and user-friendly interface
  - Handle form submission and password update logic
  - Update user profile to remove password change requirement
  - Add success messages and proper redirects
  - _Requirements: 4.1, 4.3, 1.3, 2.3_

- [x] 5. Create middleware to enforce password change
  - Implement MandatoryPasswordChangeMiddleware class
  - Add logic to check if user needs password change
  - Define exempt URLs (login, logout, static files, etc.)
  - Redirect users to password change page when required
  - Handle edge cases and error scenarios gracefully
  - _Requirements: 1.2, 2.2, 1.4, 2.4_

- [x] 6. Add middleware to Django settings and URL configuration
  - Add middleware to MIDDLEWARE setting in correct position
  - Create URL pattern for mandatory password change view
  - Test middleware activation and URL routing
  - Ensure proper order in middleware stack
  - _Requirements: 1.2, 2.2_

- [ ] 7. Update user creation processes to use new system
  - Update dashboard/views.py super admin creation to set password requirement
  - Update lojas/views.py store creation to set password requirement for admin user
  - Ensure both user types get provisional passwords and email notifications
  - Test user creation flows end-to-end
  - _Requirements: 1.1, 2.1_

- [ ] 8. Add admin interface indicators for password change status
  - Update user list templates to show password change requirement status
  - Add visual indicators (badges/icons) for users needing password change
  - Create admin actions to manually reset password change requirements
  - Add filtering options for users by password status
  - _Requirements: 3.1, 3.3_

- [ ] 9. Test complete password change flow for all user types
  - Test super admin user creation and mandatory password change
  - Test store admin user creation and mandatory password change  
  - Test middleware enforcement and redirect behavior
  - Test password validation and error handling
  - Test session management after password change
  - _Requirements: 1.1, 1.2, 1.3, 2.1, 2.2, 2.3, 4.1, 4.2, 4.3, 4.4_

- [ ] 10. Add logging and monitoring for password changes
  - Log all mandatory password changes with user and timestamp
  - Log middleware redirects for monitoring
  - Add error logging for password change failures
  - Create monitoring for users who haven't changed passwords
  - _Requirements: 3.2, 3.4_