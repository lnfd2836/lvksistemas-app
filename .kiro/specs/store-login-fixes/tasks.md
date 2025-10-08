# Implementation Plan

- [x] 1. Fix email content to show only one login URL
  - Modify the email message in `lojas/views.py` in the `enviar_credenciais_provisorias` function
  - Remove the multiple login URLs section
  - Keep only the main URL: https://www.lvksistemas.com.br/loja/login/
  - Improve email formatting for better readability
  - _Requirements: 2.1, 2.2, 2.3, 2.4_

- [x] 2. Debug and fix authentication issues
  - Add detailed logging to the login process in `dashboard/loja_login.py`
  - Verify email-based authentication is working correctly
  - Test provisional password validation
  - Ensure user lookup by email functions properly
  - _Requirements: 1.1, 1.2, 1.3, 1.4_

- [x] 3. Test login functionality with real credentials
  - Create test cases for email-based login
  - Verify provisional password authentication
  - Test error handling for invalid credentials
  - Confirm redirect behavior after successful login
  - _Requirements: 1.1, 1.2, 1.3, 1.4_

- [x] 4. Improve error messages and user feedback
  - Enhance error messages in the login form
  - Add specific feedback for different failure scenarios
  - Ensure clear guidance for users experiencing issues
  - Test user experience with various error conditions
  - _Requirements: 1.3, 1.4_