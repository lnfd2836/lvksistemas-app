# Requirements Document

## Introduction

The application is experiencing a server error (500) when accessing the `/lojas/` URL on Heroku. The error is a Django TemplateSyntaxError indicating that the template parser cannot parse a comparison operation `status_filter=='ativa'` in one of the templates. This error prevents users from accessing the lojas (stores) listing page, which is a critical functionality of the system.

## Requirements

### Requirement 1

**User Story:** As a user, I want to access the lojas listing page without encountering server errors, so that I can view and manage stores in the system.

#### Acceptance Criteria

1. WHEN a user navigates to `/lojas/` THEN the system SHALL display the lojas listing page without errors
2. WHEN the lojas template is rendered THEN the system SHALL properly parse all template syntax without throwing TemplateSyntaxError
3. WHEN status filtering is applied THEN the system SHALL correctly evaluate filter conditions in templates

### Requirement 2

**User Story:** As a developer, I want to identify and fix the specific template causing the syntax error, so that the application functions correctly in production.

#### Acceptance Criteria

1. WHEN investigating the error THEN the system SHALL identify which template file contains the malformed syntax
2. WHEN examining the template THEN the system SHALL locate the specific line with `status_filter=='ativa'` syntax
3. WHEN fixing the syntax THEN the system SHALL use proper Django template syntax for comparisons

### Requirement 3

**User Story:** As a system administrator, I want to ensure template syntax errors are caught before deployment, so that production issues are prevented.

#### Acceptance Criteria

1. WHEN templates are modified THEN the system SHALL validate template syntax during development
2. WHEN running tests THEN the system SHALL include template rendering tests to catch syntax errors
3. WHEN deploying THEN the system SHALL verify all templates can be parsed successfully

### Requirement 4

**User Story:** As a user, I want status filtering functionality to work correctly, so that I can filter lojas by their status (active, inactive, etc.).

#### Acceptance Criteria

1. WHEN applying status filters THEN the system SHALL correctly filter lojas based on status values
2. WHEN status is 'ativa' THEN the system SHALL display only active stores
3. WHEN no status filter is applied THEN the system SHALL display all stores regardless of status