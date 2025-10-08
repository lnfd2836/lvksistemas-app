# Requirements Document

## Introduction

There are two critical issues with the store login system:
1. Store administrators cannot access the system using their provisional credentials
2. The email sent to stores contains 3 different login URLs when only one should be provided

## Requirements

### Requirement 1

**User Story:** As a store administrator, I want to be able to log in using my provisional credentials, so that I can access my store dashboard.

#### Acceptance Criteria

1. WHEN I use my email and provisional password THEN I SHALL be able to log in successfully
2. WHEN I log in with provisional credentials THEN I SHALL be redirected to my store dashboard
3. WHEN my credentials are invalid THEN I SHALL see a clear error message
4. WHEN I log in successfully THEN the system SHALL log the access attempt

### Requirement 2

**User Story:** As a store administrator, I want to receive an email with only the correct login URL, so that I don't get confused with multiple URLs.

#### Acceptance Criteria

1. WHEN I receive credentials email THEN it SHALL contain only one login URL
2. WHEN the email is sent THEN the URL SHALL be https://www.lvksistemas.com.br/loja/login/
3. WHEN I click the URL THEN it SHALL take me to the correct login page
4. WHEN the email is formatted THEN it SHALL be clear and professional