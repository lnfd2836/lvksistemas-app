# Requirements Document

## Introduction

The mandatory password change system is currently working for super administrators but has issues with store (loja) user logins. The middleware that enforces mandatory password changes may not be executing properly for all login types, specifically for store admin users who should be required to change their provisional passwords on first login.

## Requirements

### Requirement 1

**User Story:** As a store admin user, I want to be forced to change my provisional password on first login, so that my account remains secure and follows the same security standards as super admin accounts.

#### Acceptance Criteria

1. WHEN a store admin user logs in for the first time with provisional credentials THEN the system SHALL redirect them to the mandatory password change page
2. WHEN a store admin user has `requires_password_change=True` in their profile THEN the middleware SHALL detect this condition regardless of login method
3. WHEN a store admin user completes the mandatory password change THEN their profile SHALL be updated to `requires_password_change=False`
4. WHEN a store admin user tries to access any protected page before changing their password THEN they SHALL be redirected to the password change page

### Requirement 2

**User Story:** As a system administrator, I want the mandatory password change middleware to work consistently across all login methods, so that security policies are enforced uniformly.

#### Acceptance Criteria

1. WHEN any user logs in through the super admin login endpoint THEN the middleware SHALL check for mandatory password change requirements
2. WHEN any user logs in through the store login endpoint THEN the middleware SHALL check for mandatory password change requirements
3. WHEN the middleware detects a user needs password change THEN it SHALL redirect to the correct password change URL without namespace issues
4. WHEN a user is on the password change page THEN the middleware SHALL NOT create redirect loops

### Requirement 3

**User Story:** As a store admin user, I want my user profile to be properly created and configured when my store is created, so that the mandatory password change system works correctly for me.

#### Acceptance Criteria

1. WHEN a new store is created with an admin user THEN a PerfilUsuario SHALL be created with `requires_password_change=True`
2. WHEN a store admin user profile is created THEN it SHALL have `is_loja_admin=True` and `is_super_admin=False`
3. WHEN existing store admin users are missing profiles THEN the system SHALL provide a way to create them retroactively
4. IF a store admin user exists without a profile THEN the middleware SHALL handle this gracefully without errors

### Requirement 4

**User Story:** As a developer, I want comprehensive debugging and monitoring capabilities for the mandatory password change system, so that I can quickly identify and resolve issues.

#### Acceptance Criteria

1. WHEN debugging the mandatory password change system THEN there SHALL be tools to verify user profiles and middleware behavior
2. WHEN a user login occurs THEN the system SHALL log relevant information about middleware execution
3. WHEN middleware detects password change requirements THEN it SHALL log the decision and redirect action
4. WHEN troubleshooting login issues THEN there SHALL be utilities to check user profiles, middleware configuration, and URL routing