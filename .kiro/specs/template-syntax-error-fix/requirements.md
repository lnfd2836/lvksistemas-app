# Requirements Document

## Introduction

This feature addresses a critical template syntax error in the Django application where the template is using incorrect comparison syntax (`==`) instead of the proper Django template filter syntax. The error occurs in the store detail template when trying to conditionally select options based on the store's status.

## Requirements

### Requirement 1

**User Story:** As a system administrator, I want the store detail page to load without template syntax errors, so that I can view and manage store information properly.

#### Acceptance Criteria

1. WHEN a user navigates to the store detail page THEN the page SHALL load without TemplateSyntaxError
2. WHEN the status selection modal is rendered THEN the correct status option SHALL be pre-selected based on the store's current status
3. WHEN the template uses comparison logic THEN it SHALL use proper Django template syntax instead of Python comparison operators

### Requirement 2

**User Story:** As a developer, I want all template comparisons to follow Django best practices, so that the application is maintainable and error-free.

#### Acceptance Criteria

1. WHEN template files contain conditional logic THEN they SHALL use Django template filters and tags
2. WHEN comparing values in templates THEN the system SHALL use `ifequal`, `if` with proper syntax, or appropriate template filters
3. WHEN the fix is applied THEN all existing functionality SHALL remain intact

### Requirement 3

**User Story:** As a user, I want the status change modal to work correctly, so that I can update store statuses as needed.

#### Acceptance Criteria

1. WHEN the status modal opens THEN the current status SHALL be visually indicated as selected
2. WHEN I change the status and submit THEN the new status SHALL be saved correctly
3. WHEN the modal displays status options THEN all available statuses SHALL be shown (ativa, inativa, suspensa)