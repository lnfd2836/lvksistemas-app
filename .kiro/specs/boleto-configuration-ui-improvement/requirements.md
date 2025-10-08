# Requirements Document

## Introduction

This feature aims to improve the user experience of the "Configurar Boletos" (Configure Boletos) page by modifying the layout so that after a boleto configuration is successfully saved, the registration form is hidden or minimized, preventing the configuration information from continuously appearing on the screen. This will provide a cleaner interface and better user experience after the initial setup is complete.

## Requirements

### Requirement 1

**User Story:** As a Super Admin, I want the boleto configuration form to be hidden or collapsed after successfully configuring a boleto, so that I have a cleaner interface and don't see the registration fields unnecessarily.

#### Acceptance Criteria

1. WHEN a Super Admin successfully saves a boleto configuration THEN the system SHALL hide or collapse the configuration form
2. WHEN the configuration form is hidden THEN the system SHALL display a success message indicating the configuration was saved
3. WHEN the configuration form is hidden THEN the system SHALL show a button or link to "Add New Configuration" or "Edit Configuration"
4. WHEN a Super Admin clicks "Add New Configuration" THEN the system SHALL expand or show the configuration form again
5. IF there are no existing configurations THEN the system SHALL display the configuration form by default

### Requirement 2

**User Story:** As a Super Admin, I want to easily manage existing boleto configurations without the form cluttering the interface, so that I can focus on viewing and managing the configured boletos.

#### Acceptance Criteria

1. WHEN there are existing boleto configurations THEN the system SHALL prominently display the list of existing configurations
2. WHEN viewing existing configurations THEN the system SHALL show the active configuration clearly marked
3. WHEN a Super Admin wants to edit a configuration THEN the system SHALL provide an easy way to access the edit functionality
4. WHEN editing a configuration THEN the system SHALL pre-populate the form with existing values
5. WHEN a configuration is successfully updated THEN the system SHALL return to the collapsed/hidden form state

### Requirement 3

**User Story:** As a Super Admin, I want the interface to be responsive and intuitive, so that I can efficiently manage boleto configurations without confusion.

#### Acceptance Criteria

1. WHEN the page loads THEN the system SHALL determine whether to show or hide the form based on existing configurations
2. WHEN transitioning between form states THEN the system SHALL provide smooth visual transitions
3. WHEN the form is hidden THEN the system SHALL maintain all existing functionality for viewing and managing configurations
4. WHEN there are validation errors THEN the system SHALL show the form and highlight the errors appropriately
5. WHEN the user navigates away and returns THEN the system SHALL remember the appropriate form state