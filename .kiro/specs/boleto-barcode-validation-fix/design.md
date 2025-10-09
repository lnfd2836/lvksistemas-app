# Design Document

## Overview

The current boleto barcode generation system has critical flaws that produce invalid barcodes, preventing customers from making payments. The main issues identified are:

1. **Incorrect DV (Digit Verification) calculations** - The current modulo 10 and modulo 11 algorithms don't follow FEBRABAN standards
2. **Invalid campo livre structure** - The 25-digit free field doesn't match Caixa Econômica Federal specifications
3. **Missing validation** - No validation occurs before saving barcodes to the database
4. **Inconsistent nosso número generation** - The "nosso número" generation doesn't include proper digit verification

The solution involves fixing the BoletoCaixaService class, adding comprehensive validation, and implementing proper error handling and logging.

## Architecture

### Current Architecture Issues
- `BoletoCaixaService` generates invalid barcodes due to incorrect algorithms
- No validation layer between generation and storage
- Missing error handling for edge cases
- No logging for debugging barcode generation issues

### Proposed Architecture
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Views Layer   │───▶│ Validation Layer │───▶│ Service Layer   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
                       ┌──────────────────┐    ┌─────────────────┐
                       │ Error Handling   │    │ Logging System  │
                       └──────────────────┘    └─────────────────┘
```

## Components and Interfaces

### 1. Enhanced BoletoCaixaService
**Purpose**: Generate valid barcodes following FEBRABAN and Caixa specifications

**Key Methods**:
- `gerar_boleto_caixa()` - Main generation method with validation
- `_calcular_dv_modulo11_febraban()` - Correct modulo 11 calculation
- `_calcular_dv_modulo10_febraban()` - Correct modulo 10 calculation
- `_gerar_campo_livre_caixa()` - Generate proper 25-digit free field
- `_validar_codigo_barras()` - Validate generated barcode

### 2. BarcodeValidator Class
**Purpose**: Comprehensive validation of generated barcodes

**Methods**:
- `validate_barcode_format()` - Check 44-digit format
- `validate_dv_calculations()` - Verify all digit verifications
- `validate_campo_livre()` - Validate free field structure
- `validate_linha_digitavel()` - Validate typeable line

### 3. BoletoLogger Class
**Purpose**: Detailed logging for debugging and monitoring

**Methods**:
- `log_generation_steps()` - Log each step of barcode generation
- `log_validation_results()` - Log validation outcomes
- `log_errors()` - Log errors with context

### 4. BoletoFixService Class
**Purpose**: Fix existing invalid boletos

**Methods**:
- `identify_invalid_boletos()` - Find boletos with invalid barcodes
- `regenerate_boleto()` - Regenerate valid barcode for existing boleto
- `batch_fix_boletos()` - Fix multiple boletos in batch

## Data Models

### Enhanced BoletoGerado Model
Add validation fields:
```python
class BoletoGerado(models.Model):
    # ... existing fields ...
    
    # New validation fields
    barcode_valid = models.BooleanField(default=False)
    validation_errors = models.JSONField(default=list, blank=True)
    generation_log = models.JSONField(default=dict, blank=True)
    last_validation = models.DateTimeField(null=True, blank=True)
```

## Error Handling

### Validation Errors
- **Format Errors**: Invalid length, non-numeric characters
- **DV Errors**: Incorrect digit verification calculations
- **Campo Livre Errors**: Invalid free field structure
- **Configuration Errors**: Missing or invalid bank configuration

### Error Response Strategy
1. **Generation Phase**: Raise specific exceptions with detailed messages
2. **Validation Phase**: Return validation results with error details
3. **Storage Phase**: Only save valid barcodes, log invalid attempts
4. **User Interface**: Display clear error messages with corrective actions

## Testing Strategy

### Unit Tests
- Test each DV calculation method with known valid inputs
- Test barcode generation with various configurations
- Test validation methods with both valid and invalid barcodes
- Test error handling for edge cases

### Integration Tests
- Test complete boleto generation flow
- Test validation integration with database operations
- Test error handling in views and services

### Validation Tests
- Test against known valid Caixa barcodes
- Test with real bank configurations
- Test edge cases (minimum/maximum values, special dates)

### Performance Tests
- Test batch validation of existing boletos
- Test generation performance under load

## Implementation Details

### FEBRABAN Barcode Structure (44 digits)
```
Positions: AAABCCCCCDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD
A (1-3):   Bank code (104 for Caixa)
B (4):     Currency code (9 for Real)
C (5):     General DV (calculated using modulo 11)
D (6-44):  Due date factor (4) + Amount (10) + Free field (25)
```

### Caixa Free Field Structure (25 digits)
```
Positions: CCCCCCNNNNNNNNNNAAAAAADDD
C (1-6):   Beneficiary code (6 digits)
N (7-16):  Our number without DV (10 digits)
A (17-22): Agency (4) + zeros (2)
D (23-25): Wallet code (3 digits)
```

### DV Calculation Algorithms

#### Modulo 11 (General DV)
```python
def _calcular_dv_modulo11_febraban(self, codigo):
    """FEBRABAN standard modulo 11 calculation"""
    sequence = "4329876543298765432987654329876543298765432"
    soma = 0
    
    for i, digit in enumerate(reversed(codigo)):
        if digit.isdigit():
            produto = int(digit) * int(sequence[i % len(sequence)])
            soma += produto
    
    resto = soma % 11
    
    # FEBRABAN rules for modulo 11
    if resto in [0, 10, 11]:
        return 1
    else:
        return 11 - resto
```

#### Modulo 10 (Linha Digitável DVs)
```python
def _calcular_dv_modulo10_febraban(self, codigo):
    """FEBRABAN standard modulo 10 calculation"""
    soma = 0
    multiplicador = 2
    
    for digit in reversed(codigo):
        if digit.isdigit():
            produto = int(digit) * multiplicador
            if produto > 9:
                produto = sum(int(d) for d in str(produto))
            soma += produto
            multiplicador = 3 - multiplicador  # Alternate between 2 and 1
    
    resto = soma % 10
    return 0 if resto == 0 else 10 - resto
```

## Migration Strategy

### Phase 1: Fix Generation Service
1. Update BoletoCaixaService with correct algorithms
2. Add comprehensive validation
3. Implement proper error handling

### Phase 2: Add Validation Layer
1. Create BarcodeValidator class
2. Integrate validation into generation flow
3. Add validation to existing boletos

### Phase 3: Fix Existing Data
1. Identify invalid boletos in database
2. Regenerate valid barcodes
3. Update boleto records with valid data

### Phase 4: Monitoring and Logging
1. Add detailed logging
2. Create monitoring dashboard
3. Set up alerts for validation failures

## Security Considerations

- Validate all input parameters before processing
- Sanitize bank configuration data
- Log security-relevant events (failed validations, suspicious patterns)
- Ensure generated barcodes don't expose sensitive information

## Performance Considerations

- Cache validation results for frequently accessed boletos
- Optimize DV calculations for batch processing
- Use database indexes for validation queries
- Implement async processing for batch operations