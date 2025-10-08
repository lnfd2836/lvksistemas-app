# Requirements Document

## Introduction

This feature enhances the store creation process by requiring plan selection during store creation, ensuring that both ControleFinanceiro and AssinaturaLoja records are created consistently from the beginning. This prevents the current issue where stores can exist without proper plan assignments, leading to inconsistent financial information display.

## Requirements

### Requirement 1

**User Story:** As a system administrator, I want to select a commercial plan when creating a new store, so that the store has proper financial control from the beginning.

#### Acceptance Criteria

1. WHEN creating a new store THEN the system SHALL display available commercial plans for selection
2. WHEN a plan is selected THEN the system SHALL validate that the plan exists and is active
3. WHEN the store creation form is submitted THEN a plan selection SHALL be required
4. WHEN no plan is selected THEN the system SHALL display an error message and prevent store creation

### Requirement 2

**User Story:** As a system administrator, I want both financial control systems to be created automatically when I create a store with a plan, so that there are no inconsistencies between dashboard and detail views.

#### Acceptance Criteria

1. WHEN a store is created with a selected plan THEN the system SHALL create a ControleFinanceiro record
2. WHEN a store is created with a selected plan THEN the system SHALL create an AssinaturaLoja record
3. WHEN both records are created THEN they SHALL reference the same plan information
4. WHEN the creation process fails THEN the system SHALL rollback all changes to maintain data consistency

### Requirement 3

**User Story:** As a system administrator, I want to see plan information and pricing during store creation, so that I can make informed decisions about which plan to assign.

#### Acceptance Criteria

1. WHEN viewing the store creation form THEN the system SHALL display plan names, descriptions, and monthly prices
2. WHEN selecting a plan THEN the system SHALL show plan limits and features
3. WHEN a plan is selected THEN the system SHALL display the calculated monthly cost
4. WHEN no plans are available THEN the system SHALL display an appropriate message and disable store creation

### Requirement 4

**User Story:** As a system administrator, I want existing stores without proper plan assignments to be identified and fixable, so that all stores have consistent financial information.

#### Acceptance Criteria

1. WHEN viewing the store list THEN stores without AssinaturaLoja SHALL be visually identified
2. WHEN a store lacks AssinaturaLoja but has ControleFinanceiro THEN the system SHALL provide a way to create the missing record
3. WHEN fixing inconsistent stores THEN the system SHALL preserve existing financial data
4. WHEN the fix is applied THEN both dashboard and detail views SHALL show consistent information