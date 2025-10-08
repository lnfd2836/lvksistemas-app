# Requirements Document

## Introduction

The store editing functionality is missing the "Tipo de Loja" (Store Type) field in the edit form template. While the field is properly defined in the LojaForm and the model supports it, the edit template does not render this field, preventing users from updating the store type when editing a store.

## Requirements

### Requirement 1

**User Story:** As a super admin, I want to be able to edit the store type when editing a store, so that I can properly categorize stores according to their business type.

#### Acceptance Criteria

1. WHEN I access the store edit page THEN the "Tipo de Loja" field SHALL be visible and editable
2. WHEN I select a store type from the dropdown THEN the field SHALL save the selected value correctly
3. WHEN the form loads THEN the current store type SHALL be pre-selected if one exists
4. WHEN no store type is selected THEN the field SHALL show a helpful placeholder text

### Requirement 2

**User Story:** As a super admin, I want the store type field to be properly styled and integrated with the existing form layout, so that it maintains consistency with the rest of the interface.

#### Acceptance Criteria

1. WHEN viewing the store type field THEN it SHALL use the same styling as other form fields
2. WHEN the field has validation errors THEN error messages SHALL be displayed consistently with other fields
3. WHEN the field is rendered THEN it SHALL be positioned logically within the form layout
4. WHEN the dropdown is opened THEN it SHALL show all available store types from the TipoLoja model

### Requirement 3

**User Story:** As a super admin, I want the store type field to work correctly in both create and edit modes, so that I can manage store types consistently across all store operations.

#### Acceptance Criteria

1. WHEN creating a new store THEN the store type field SHALL be available and functional
2. WHEN editing an existing store THEN the store type field SHALL be available and functional
3. WHEN saving changes THEN the store type SHALL be persisted correctly to the database
4. WHEN the store type is changed THEN the change SHALL be reflected immediately after saving