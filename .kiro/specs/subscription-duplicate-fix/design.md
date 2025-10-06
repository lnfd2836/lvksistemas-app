# Design Document

## Overview

The subscription duplicate key constraint error occurs because the current implementation tries to create new `AssinaturaLoja` records without checking if a subscription already exists for the store. The `planos_assinaturaloja` table has a unique constraint on `loja_id`, which prevents multiple active subscriptions per store.

The solution involves implementing proper subscription management logic that:
1. Checks for existing subscriptions before creating new ones
2. Updates existing subscriptions instead of creating duplicates
3. Handles subscription state transitions properly
4. Provides clear user feedback about subscription status

## Architecture

The subscription system follows this flow:
- **User Interface** - Subscription forms and status displays
- **View Layer** - Handles subscription requests and responses
- **Business Logic** - Manages subscription state and transitions
- **Data Layer** - Stores subscription records with proper constraints

## Components and Interfaces

### 1. Current Issue Analysis

**Database Schema:**
```sql
-- Current constraint causing the issue
ALTER TABLE planos_assinaturaloja ADD CONSTRAINT planos_assinaturaloja_loja_id_key UNIQUE (loja_id);
```

**Current Flow (Problematic):**
1. User clicks "Subscribe to Plan"
2. System attempts to create new `AssinaturaLoja` record
3. Database rejects due to unique constraint violation
4. User sees error message

### 2. Proposed Solution Architecture

**New Flow (Fixed):**
1. User clicks "Subscribe to Plan"
2. System checks if subscription exists for the store
3. If exists: Update existing subscription
4. If not exists: Create new subscription
5. Handle state transitions properly
6. Provide user feedback

### 3. Subscription State Management

**Subscription States:**
- `ATIVA` - Currently active subscription
- `CANCELADA` - Cancelled subscription
- `EXPIRADA` - Expired subscription
- `PENDENTE` - Pending activation

**State Transitions:**
- New subscription: `None` → `ATIVA`
- Plan change: `ATIVA` → `ATIVA` (same record, different plan)
- Cancellation: `ATIVA` → `CANCELADA`
- Expiration: `ATIVA` → `EXPIRADA`

## Data Models

### Current Model Issues
```python
class AssinaturaLoja(models.Model):
    loja = models.OneToOneField(Loja, on_delete=models.CASCADE)  # This creates the unique constraint
    plano = models.ForeignKey(PlanoComercial, on_delete=models.CASCADE)
    data_inicio = models.DateTimeField(auto_now_add=True)
    data_fim = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, default='ATIVA')
```

### Proposed Solution
The model structure is correct, but the business logic needs to handle the `OneToOneField` constraint properly by using `get_or_create()` or `update_or_create()` methods.

## Error Handling

### 1. Duplicate Subscription Detection
```python
# Instead of:
AssinaturaLoja.objects.create(loja=loja, plano=plano)

# Use:
subscription, created = AssinaturaLoja.objects.update_or_create(
    loja=loja,
    defaults={'plano': plano, 'status': 'ATIVA', 'data_inicio': timezone.now()}
)
```

### 2. User Feedback Improvements
- **Current Plan Indication**: Show which plan the store currently has
- **Change Confirmation**: Confirm when switching between plans
- **Error Messages**: Clear messages for any issues
- **Success Messages**: Confirm successful subscription changes

### 3. Race Condition Handling
Use database transactions to prevent concurrent subscription attempts:
```python
from django.db import transaction

@transaction.atomic
def handle_subscription(loja, plano):
    # Subscription logic here
```

## Testing Strategy

### 1. Unit Tests
- Test subscription creation for new stores
- Test subscription updates for existing stores
- Test constraint violation handling
- Test state transitions

### 2. Integration Tests
- Test complete subscription flow
- Test concurrent subscription attempts
- Test UI feedback and error handling

### 3. Edge Case Tests
- Multiple rapid subscription attempts
- Subscription to same plan
- Invalid plan/store combinations
- Database constraint violations

## Implementation Plan

### Phase 1: Fix Core Subscription Logic
1. Update subscription view to use `update_or_create()`
2. Add proper transaction handling
3. Implement subscription state management

### Phase 2: Improve User Experience
1. Add current subscription status display
2. Improve error messages and user feedback
3. Add confirmation dialogs for plan changes

### Phase 3: Add Robustness
1. Add comprehensive logging
2. Implement retry mechanisms
3. Add monitoring for subscription errors

## Subscription Management Logic

### Current Subscription Check
```python
def get_current_subscription(loja):
    try:
        return AssinaturaLoja.objects.get(loja=loja, status='ATIVA')
    except AssinaturaLoja.DoesNotExist:
        return None
```

### Subscription Update/Create
```python
def handle_subscription_request(loja, new_plano):
    with transaction.atomic():
        subscription, created = AssinaturaLoja.objects.update_or_create(
            loja=loja,
            defaults={
                'plano': new_plano,
                'status': 'ATIVA',
                'data_inicio': timezone.now(),
                'data_fim': None  # Reset expiration for new/updated subscription
            }
        )
        
        if created:
            message = f"Subscription created for plan {new_plano.nome}"
        else:
            message = f"Subscription updated to plan {new_plano.nome}"
            
        return subscription, message
```

## Security Considerations

- **Authorization**: Ensure only store owners can modify their subscriptions
- **Validation**: Validate plan availability and store eligibility
- **Audit Trail**: Log all subscription changes for compliance
- **Data Integrity**: Use database transactions to maintain consistency

## Performance Impact

- **Minimal Impact**: The fix involves changing the creation logic, not adding heavy operations
- **Database Efficiency**: Using `update_or_create()` is more efficient than separate check + create operations
- **Reduced Errors**: Fewer constraint violations mean fewer error handling overhead

## Monitoring and Logging

### Key Metrics to Track
- Subscription creation/update success rates
- Constraint violation frequency
- User subscription change patterns
- Error rates and types

### Logging Strategy
- Log all subscription state changes
- Log constraint violations with context
- Log user actions for audit purposes
- Monitor for unusual subscription patterns