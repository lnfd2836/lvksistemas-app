# Design Document

## Overview

This design enhances the store creation process by adding plan selection as a required step, ensuring consistent financial control records are created from the beginning. The solution addresses the current inconsistency where stores can exist with ControleFinanceiro but without AssinaturaLoja records.

## Architecture

The solution involves modifying the store creation workflow to include plan selection and ensuring both financial control systems are created atomically during store creation.

### Current Problem Analysis
- **ControleFinanceiro**: Created automatically with a default "Básico" plan
- **AssinaturaLoja**: Not created during store creation, leading to inconsistencies
- **Result**: Dashboard shows plan info, but detail page shows "No Active Plan"

### Solution Approach
1. **Enhanced Form**: Add plan selection field to LojaForm
2. **Unified Creation**: Create both ControleFinanceiro and AssinaturaLoja during store creation
3. **Plan Mapping**: Ensure both systems reference compatible plan information
4. **Data Consistency**: Use database transactions to maintain consistency

## Components and Interfaces

### Form Layer
- **Enhanced LojaForm**: Add `plano_comercial` field for plan selection
- **Plan Display**: Show plan details (name, price, features) in the form
- **Validation**: Ensure plan selection is required and valid

### View Layer
- **Modified criar_loja view**: 
  - Load available plans for form display
  - Validate plan selection
  - Create both financial control records atomically
- **Plan Information**: Display plan details to help with selection

### Model Integration
- **PlanoComercial**: Used for AssinaturaLoja creation
- **PlanoFinanceiro**: Used for ControleFinanceiro creation
- **Mapping Logic**: Ensure both plans have compatible information

## Data Models

### Plan Relationship Mapping
```python
# Current structure analysis needed:
# PlanoComercial (used by AssinaturaLoja)
# PlanoFinanceiro (used by ControleFinanceiro)
# Need to establish relationship or mapping between these models
```

### Store Creation Flow
1. **Form Submission**: Include selected plan
2. **User Creation**: Create admin user (existing logic)
3. **Store Creation**: Create store record (existing logic)
4. **Financial Records**: Create both ControleFinanceiro and AssinaturaLoja
5. **Boleto Generation**: Generate initial boleto (existing logic)

## Error Handling

### Plan Selection Validation
- Verify plan exists and is active
- Ensure plan is available for new stores
- Handle cases where no plans are available

### Transaction Management
- Use database transactions for atomic operations
- Rollback all changes if any step fails
- Maintain data consistency across all related models

### Existing Store Handling
- Identify stores with missing AssinaturaLoja records
- Provide migration/fix functionality for existing inconsistent data
- Preserve existing financial data during fixes

## Testing Strategy

### Form Testing
- Test plan selection field rendering
- Validate required plan selection
- Test form submission with valid/invalid plans

### Integration Testing
- Test complete store creation workflow
- Verify both financial records are created
- Test transaction rollback on failures

### Data Consistency Testing
- Verify dashboard and detail views show consistent information
- Test existing store identification and fixing
- Validate plan information mapping

## Implementation Details

### Form Enhancement
```python
class LojaForm(forms.ModelForm):
    plano_comercial = forms.ModelChoiceField(
        queryset=PlanoComercial.objects.filter(ativo=True),
        required=True,
        empty_label="Selecione um plano comercial",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
```

### View Modification
```python
def criar_loja(request):
    if request.method == 'POST':
        form = LojaForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                # Create user (existing logic)
                # Create store (existing logic)
                
                # Get selected plan
                plano_comercial = form.cleaned_data['plano_comercial']
                
                # Create AssinaturaLoja
                assinatura = AssinaturaLoja.objects.create(
                    loja=loja,
                    plano=plano_comercial,
                    status='ativa',
                    data_vencimento=timezone.now() + timedelta(days=30)
                )
                
                # Create ControleFinanceiro (map from PlanoComercial)
                controle = ControleFinanceiro.objects.create(
                    loja=loja,
                    plano=get_or_create_plano_financeiro(plano_comercial),
                    valor_mensal=plano_comercial.preco_mensal
                )
```

### Plan Mapping Strategy
- **Option 1**: Create PlanoFinanceiro records that mirror PlanoComercial
- **Option 2**: Modify ControleFinanceiro to reference PlanoComercial directly
- **Option 3**: Create a mapping table between the two plan types

### Template Enhancement
```html
<!-- Plan selection with details -->
<div class="form-group">
    <label for="plano_comercial">Plano Comercial *</label>
    <select name="plano_comercial" class="form-control" required>
        <option value="">Selecione um plano</option>
        {% for plano in planos_disponiveis %}
        <option value="{{ plano.id }}" data-preco="{{ plano.preco_mensal }}" data-descricao="{{ plano.descricao }}">
            {{ plano.nome }} - R$ {{ plano.preco_mensal|floatformat:2 }}/mês
        </option>
        {% endfor %}
    </select>
</div>

<!-- Plan details display -->
<div id="plan-details" class="mt-3" style="display: none;">
    <div class="card">
        <div class="card-body">
            <h6>Detalhes do Plano</h6>
            <p id="plan-description"></p>
            <p><strong>Valor Mensal:</strong> R$ <span id="plan-price"></span></p>
        </div>
    </div>
</div>
```

## Migration Strategy

### For Existing Stores
1. **Identification**: Query stores with ControleFinanceiro but no AssinaturaLoja
2. **Data Migration**: Create AssinaturaLoja based on existing ControleFinanceiro
3. **Validation**: Ensure data consistency after migration

### Migration Command
```python
# Management command to fix existing inconsistencies
def handle(self):
    stores_to_fix = Loja.objects.filter(
        controle_financeiro__isnull=False
    ).exclude(
        assinaturaloja__isnull=False
    )
    
    for loja in stores_to_fix:
        # Create AssinaturaLoja based on ControleFinanceiro
        pass
```

## Security Considerations

### Plan Selection Validation
- Verify user has permission to assign plans
- Validate plan availability and pricing
- Prevent manipulation of plan selection

### Data Integrity
- Use database constraints to prevent orphaned records
- Implement proper foreign key relationships
- Ensure atomic operations for data consistency

## Performance Impact

### Form Loading
- Minimal impact: Load available plans once per form display
- Consider caching plan information if needed

### Store Creation
- Slight increase due to additional record creation
- Transaction overhead for atomic operations
- Overall impact should be negligible for typical usage