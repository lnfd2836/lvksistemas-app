# Design Document

## Overview

The mandatory password change system will track users who need to change their provisional passwords and enforce this requirement through middleware that intercepts requests and redirects users to a password change page until they complete the process.

## Architecture

The system will use:
- **Database field** to track password change requirement
- **Middleware** to intercept requests and enforce password change
- **Dedicated views** for password change process
- **Email notifications** for provisional passwords and reminders

## Components and Interfaces

### 1. Database Schema Changes

**User Profile Extension:**
```python
class PerfilUsuario(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # ... existing fields ...
    
    # New fields for password management
    requires_password_change = models.BooleanField(default=False)
    provisional_password_created = models.DateTimeField(null=True, blank=True)
    password_changed_at = models.DateTimeField(null=True, blank=True)
    password_change_reminders_sent = models.IntegerField(default=0)
```

### 2. Middleware Implementation

**Password Change Enforcement Middleware:**
```python
class MandatoryPasswordChangeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        # Skip for anonymous users
        if not request.user.is_authenticated:
            return self.get_response(request)
            
        # Skip for certain URLs (login, logout, password change)
        exempt_urls = [
            '/login/', '/logout/', '/change-password/',
            '/static/', '/media/', '/admin/'
        ]
        
        if any(request.path.startswith(url) for url in exempt_urls):
            return self.get_response(request)
            
        # Check if user needs to change password
        if self.user_needs_password_change(request.user):
            return redirect('change_mandatory_password')
            
        return self.get_response(request)
        
    def user_needs_password_change(self, user):
        try:
            profile = user.perfil
            return profile.requires_password_change
        except:
            return False
```

### 3. Views Implementation

**Password Change Views:**
```python
@login_required
def change_mandatory_password(request):
    """Force password change for users with provisional passwords"""
    
    if request.method == 'POST':
        form = MandatoryPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            # Change password
            user = form.save()
            
            # Update profile
            profile = user.perfil
            profile.requires_password_change = False
            profile.password_changed_at = timezone.now()
            profile.save()
            
            # Update session to prevent logout
            update_session_auth_hash(request, user)
            
            messages.success(request, 'Senha alterada com sucesso!')
            return redirect('dashboard:principal')
    else:
        form = MandatoryPasswordChangeForm(request.user)
    
    return render(request, 'auth/change_mandatory_password.html', {
        'form': form,
        'is_mandatory': True
    })
```

### 4. Form Implementation

**Mandatory Password Change Form:**
```python
class MandatoryPasswordChangeForm(PasswordChangeForm):
    def __init__(self, user, *args, **kwargs):
        super().__init__(user, *args, **kwargs)
        
        # Customize field labels and help text
        self.fields['old_password'].label = 'Senha Provisória Atual'
        self.fields['old_password'].help_text = 'Digite a senha provisória que você recebeu por email'
        
        self.fields['new_password1'].label = 'Nova Senha'
        self.fields['new_password1'].help_text = 'Mínimo 8 caracteres, incluindo letras e números'
        
        self.fields['new_password2'].label = 'Confirmar Nova Senha'
        self.fields['new_password2'].help_text = 'Digite a mesma senha novamente'
    
    def clean_new_password1(self):
        password = self.cleaned_data.get('new_password1')
        
        # Custom password validation
        if len(password) < 8:
            raise ValidationError('A senha deve ter pelo menos 8 caracteres.')
            
        if not re.search(r'[A-Za-z]', password):
            raise ValidationError('A senha deve conter pelo menos uma letra.')
            
        if not re.search(r'\d', password):
            raise ValidationError('A senha deve conter pelo menos um número.')
            
        return password
```

## Data Models

### User Profile Updates

The existing `PerfilUsuario` model will be extended with password management fields:

```python
# New fields to add
requires_password_change = models.BooleanField(default=False)
provisional_password_created = models.DateTimeField(null=True, blank=True)
password_changed_at = models.DateTimeField(null=True, blank=True)
password_change_reminders_sent = models.IntegerField(default=0)
```

## Error Handling

### 1. Middleware Error Handling
- Handle users without profiles gracefully
- Skip enforcement for system users
- Provide fallback for database errors

### 2. Password Change Errors
- Validate current password correctly
- Provide clear error messages for password requirements
- Handle session management properly

### 3. Edge Cases
- Users who bypass middleware
- Multiple simultaneous login attempts
- Password change during active sessions

## Testing Strategy

### 1. Unit Tests
- Test middleware logic
- Test password validation
- Test profile updates

### 2. Integration Tests
- Test complete password change flow
- Test email sending
- Test redirect behavior

### 3. User Experience Tests
- Test with different user types
- Test error scenarios
- Test success flows

## Implementation Plan

### Phase 1: Database and Models
1. Add new fields to PerfilUsuario model
2. Create and run migrations
3. Update user creation signals

### Phase 2: Middleware and Views
1. Implement middleware
2. Create password change views and forms
3. Create templates

### Phase 3: Integration
1. Update user creation processes
2. Update email templates
3. Add middleware to settings

### Phase 4: Testing and Refinement
1. Test all user flows
2. Add logging and monitoring
3. Create admin interface for management

## Security Considerations

- **Session Management**: Ensure user stays logged in after password change
- **CSRF Protection**: All forms must include CSRF tokens
- **Password Validation**: Enforce strong password requirements
- **Audit Trail**: Log all password changes for security monitoring
- **Rate Limiting**: Prevent brute force attacks on password change

## User Experience Design

### Password Change Page
- Clear explanation of why password change is required
- Step-by-step instructions
- Password strength indicator
- Success confirmation
- Error handling with helpful messages

### Email Templates
- Welcome email with provisional password
- Password change reminder emails
- Password change confirmation email

## Performance Impact

- **Minimal Impact**: Middleware adds small overhead to each request
- **Database Queries**: One additional query per authenticated request
- **Caching**: Profile data can be cached to reduce database load
- **Optimization**: Exempt static files and API endpoints from middleware