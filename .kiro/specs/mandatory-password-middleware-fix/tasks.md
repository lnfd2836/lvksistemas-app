# Implementation Plan

- [ ] 1. Enhance middleware to handle all login types consistently
  - Update MandatoryPasswordChangeMiddleware to include store login URLs in exempt list
  - Add enhanced logging for middleware execution debugging
  - Implement fallback profile creation for users missing profiles
  - Fix URL redirect issues by removing namespace problems
  - _Requirements: 2.1, 2.2, 2.3, 2.4_

- [ ] 2. Create profile management service for consistent user profile handling
  - [ ] 2.1 Implement ProfileManagementService class with profile creation utilities
    - Create ensure_user_profile method for automatic profile creation
    - Implement get_default_profile_data method for user type detection
    - Add fix_missing_profiles utility for retroactive profile creation
    - _Requirements: 3.1, 3.2, 3.3, 3.4_

  - [ ]* 2.2 Write unit tests for profile management service
    - Test profile creation for different user types
    - Test missing profile detection and creation
    - Test profile update operations
    - _Requirements: 3.1, 3.2, 3.3, 3.4_

- [ ] 3. Fix signal handlers to work consistently across all login types
  - [ ] 3.1 Update verificar_troca_senha_obrigatoria signal handler
    - Ensure profile creation for all user types on login
    - Add first login detection logic
    - Implement provisional password detection for store admins
    - Add proper error handling and logging
    - _Requirements: 1.1, 1.2, 1.3, 1.4_

  - [ ]* 3.2 Write unit tests for enhanced signal handlers
    - Test profile creation on user login
    - Test password change requirement detection
    - Test email sending functionality
    - _Requirements: 1.1, 1.2, 1.3, 1.4_

- [ ] 4. Create debugging and monitoring utilities
  - [ ] 4.1 Implement PasswordChangeDebugger class
    - Create check_user_status method for user status debugging
    - Implement test_middleware_for_user method for middleware testing
    - Add comprehensive logging for troubleshooting
    - _Requirements: 4.1, 4.2, 4.3, 4.4_

  - [ ] 4.2 Create management command for fixing existing user profiles
    - Implement command to identify users missing profiles
    - Add functionality to create missing profiles retroactively
    - Include dry-run option for safe testing
    - _Requirements: 3.3, 3.4_

  - [ ]* 4.3 Write integration tests for complete login flows
    - Test super admin login with password change requirement
    - Test store admin login with password change requirement
    - Test middleware execution after different login types
    - _Requirements: 1.1, 1.2, 2.1, 2.2_

- [ ] 5. Update middleware error handling and logging
  - [ ] 5.1 Enhance middleware exception handling
    - Add comprehensive error logging without blocking users
    - Implement graceful fallbacks for profile-related errors
    - Add debug mode error details
    - _Requirements: 2.4, 4.2, 4.3_

  - [ ] 5.2 Configure enhanced logging for password change system
    - Set up dedicated loggers for middleware and signals
    - Configure appropriate log levels for debugging
    - Add structured logging for better troubleshooting
    - _Requirements: 4.2, 4.3, 4.4_

- [ ] 6. Test and validate the complete system
  - [ ] 6.1 Run comprehensive testing of all login types
    - Test super admin login flow with middleware
    - Test store admin login flow with middleware
    - Verify password change enforcement works consistently
    - _Requirements: 1.1, 1.2, 2.1, 2.2_

  - [ ] 6.2 Execute profile fix utility on existing users
    - Run management command to identify missing profiles
    - Create missing profiles for existing store admins
    - Verify all users have proper profile configuration
    - _Requirements: 3.3, 3.4_

  - [ ]* 6.3 Perform end-to-end testing of password change flows
    - Test complete password change flow for different user types
    - Test redirect behavior after password change
    - Test email notifications and user experience
    - _Requirements: 1.3, 1.4, 4.1_