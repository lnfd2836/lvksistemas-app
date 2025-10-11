# Design Document

## Overview

The mandatory password change system currently has inconsistent behavior between different login methods. The middleware works correctly for super admin logins but may not execute properly for store (loja) admin logins. This design addresses the middleware execution flow, user profile management, and debugging capabilities to ensure consistent security enforcement across all login types.

## Architecture

### Current System Components

1. **MandatoryPasswordChangeMiddleware**: Intercepts requests and enforces password changes
2. **PerfilUsuario Model**: Stores user profile data including password change requirements
3. **Login Views**: Multiple login endpoints (simple_login, loja_login)
4. **Signal Handlers**: Automatic profile creation and password change detection
5. **AuthenticationService**: Determines user types and dashboard routing

### Problem Areas Identified

1. **Middleware Execution**: May not execute consistently for all login paths
2. **Profile Creation**: Store admin users may lack proper profiles
3. **Signal Connectivity**: Password change signals may not trigger for all user types
4. **URL Routing**: Namespace issues in middleware redirects

## Components and Interfaces

### Enhanced Middleware Design

```python
class MandatoryPasswordChangeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.exempt_urls = [
            '/login/',
            '/loja-login/',  # Add store login
            '/logout/',
            '/usuarios/change-mandatory-password/',
            # ... other exempt URLs
        ]
    
    def __call__(self, request):
        # Enhanced logging for debugging
        if request.user.is_authenticated:
            self.log_middleware_execution(request)
        
        response = self.process_request(request)
        if response:
            return response
        
        return self.get_response(request)
    
    def user_needs_password_change(self, user):
        """Enhanced user check with profile creation fallback"""
        try:
            if not hasattr(user, 'perfil'):
                # Create missing profile for store admins
                self.create_missing_profile(user)
                return False  # Don't force change immediately after creation
            
            perfil = user.perfil
            return perfil.requires_password_change or perfil.deve_trocar_senha
            
        except Exception as e:
            logger.error(f'Error checking password change requirement: {e}')
            return False
    
    def create_missing_profile(self, user):
        """Create missing profile for users who should have one"""
        from lojas.models import Loja
        
        try:
            # Check if user is a store admin
            loja = Loja.objects.get(admin_user=user)
            PerfilUsuario.objects.create(
                user=user,
                is_loja_admin=True,
                requires_password_change=True,
                provisional_password_created=timezone.now()
            )
            logger.info(f'Created missing profile for store admin: {user.username}')
        except Loja.DoesNotExist:
            # Not a store admin, check if super admin
            if user.is_superuser:
                PerfilUsuario.objects.create(
                    user=user,
                    is_super_admin=True,
                    requires_password_change=True,
                    provisional_password_created=timezone.now()
                )
                logger.info(f'Created missing profile for super admin: {user.username}')
```

### Enhanced Signal Handlers

```python
@receiver(user_logged_in)
def verificar_troca_senha_obrigatoria(sender, request, user, **kwargs):
    """Enhanced signal handler for all login types"""
    try:
        # Ensure user has a profile
        profile, created = PerfilUsuario.objects.get_or_create(
            user=user,
            defaults={
                'is_super_admin': user.is_superuser,
                'is_loja_admin': hasattr(user, 'loja_admin'),
                'requires_password_change': False,  # Will be set based on conditions
            }
        )
        
        # Check if this is first login or provisional password
        if created or not profile.ultimo_acesso:
            # First login detected
            profile.requires_password_change = True
            profile.deve_trocar_senha = True
            profile.provisional_password_created = timezone.now()
            profile.save()
            
            logger.info(f'First login detected for {user.username} - password change required')
            
            # Send reminder email
            try:
                enviar_email_troca_senha_obrigatoria(user)
            except Exception as e:
                logger.error(f'Failed to send password change email: {e}')
        
        # Check for provisional password in store login
        if hasattr(user, 'loja_admin'):
            loja = user.loja_admin
            if hasattr(loja, 'senha_provisoria') and loja.senha_provisoria:
                profile.requires_password_change = True
                profile.save()
                logger.info(f'Provisional password detected for store admin: {user.username}')
                
    except Exception as e:
        logger.error(f'Error in password change verification signal: {e}')
```

### Profile Management Service

```python
class ProfileManagementService:
    @staticmethod
    def ensure_user_profile(user):
        """Ensure user has proper profile configuration"""
        try:
            profile, created = PerfilUsuario.objects.get_or_create(
                user=user,
                defaults=ProfileManagementService.get_default_profile_data(user)
            )
            
            if created:
                logger.info(f'Created profile for user: {user.username}')
            
            return profile
            
        except Exception as e:
            logger.error(f'Error ensuring profile for user {user.username}: {e}')
            return None
    
    @staticmethod
    def get_default_profile_data(user):
        """Get default profile data based on user type"""
        from lojas.models import Loja
        
        defaults = {
            'requires_password_change': False,
            'is_super_admin': user.is_superuser,
            'is_loja_admin': False,
        }
        
        # Check if user is store admin
        try:
            loja = Loja.objects.get(admin_user=user)
            defaults['is_loja_admin'] = True
            defaults['requires_password_change'] = True  # Store admins need password change
        except Loja.DoesNotExist:
            pass
        
        return defaults
    
    @staticmethod
    def fix_missing_profiles():
        """Utility to fix missing profiles for existing users"""
        from lojas.models import Loja
        
        # Fix store admin profiles
        store_admins = User.objects.filter(loja_admin__isnull=False)
        for user in store_admins:
            if not hasattr(user, 'perfil'):
                ProfileManagementService.ensure_user_profile(user)
        
        # Fix super admin profiles
        super_admins = User.objects.filter(is_superuser=True)
        for user in super_admins:
            if not hasattr(user, 'perfil'):
                ProfileManagementService.ensure_user_profile(user)
```

## Data Models

### Enhanced PerfilUsuario Model

The existing model is adequate but needs consistent population:

```python
class PerfilUsuario(models.Model):
    # Existing fields...
    
    # Enhanced password management
    requires_password_change = models.BooleanField(default=False)
    provisional_password_created = models.DateTimeField(blank=True, null=True)
    password_changed_at = models.DateTimeField(blank=True, null=True)
    password_change_reminders_sent = models.IntegerField(default=0)
    
    # User type flags
    is_loja_admin = models.BooleanField(default=False)
    is_super_admin = models.BooleanField(default=False)
    
    def mark_password_changed(self):
        """Mark password as changed and clear requirements"""
        self.requires_password_change = False
        self.deve_trocar_senha = False
        self.password_changed_at = timezone.now()
        self.save()
```

## Error Handling

### Middleware Error Handling

```python
def process_request(self, request):
    try:
        # Main middleware logic
        if not request.user.is_authenticated:
            return None
        
        if self.is_exempt_url(request.path):
            return None
        
        if self.user_needs_password_change(request.user):
            return redirect('change_mandatory_password')
        
        return None
        
    except Exception as e:
        # Log error but don't block user
        logger.error(f'Middleware error for {request.path}: {e}')
        
        # In debug mode, show error details
        if settings.DEBUG:
            logger.exception('Middleware exception details:')
        
        return None  # Allow request to continue
```

### Profile Creation Error Handling

```python
def create_missing_profile(self, user):
    try:
        # Profile creation logic
        pass
    except IntegrityError:
        # Profile already exists (race condition)
        logger.warning(f'Profile already exists for user {user.username}')
    except Exception as e:
        logger.error(f'Failed to create profile for {user.username}: {e}')
        # Don't raise exception - log and continue
```

## Testing Strategy

### Unit Tests

1. **Middleware Tests**
   - Test middleware execution for different login types
   - Test exempt URL handling
   - Test user profile detection
   - Test redirect behavior

2. **Signal Handler Tests**
   - Test profile creation on user login
   - Test password change requirement detection
   - Test email sending functionality

3. **Profile Management Tests**
   - Test profile creation for different user types
   - Test missing profile detection and creation
   - Test profile update operations

### Integration Tests

1. **Login Flow Tests**
   - Test super admin login with password change requirement
   - Test store admin login with password change requirement
   - Test middleware execution after different login types

2. **End-to-End Tests**
   - Test complete password change flow
   - Test redirect behavior after password change
   - Test email notifications

### Debug and Monitoring Tools

```python
class PasswordChangeDebugger:
    @staticmethod
    def check_user_status(username):
        """Debug utility to check user password change status"""
        try:
            user = User.objects.get(username=username)
            profile = getattr(user, 'perfil', None)
            
            return {
                'user_exists': True,
                'has_profile': profile is not None,
                'requires_change': profile.requires_password_change if profile else False,
                'is_store_admin': profile.is_loja_admin if profile else False,
                'is_super_admin': profile.is_super_admin if profile else False,
                'last_login': user.last_login,
                'provisional_created': profile.provisional_password_created if profile else None,
            }
        except User.DoesNotExist:
            return {'user_exists': False}
    
    @staticmethod
    def test_middleware_for_user(user):
        """Test middleware behavior for specific user"""
        middleware = MandatoryPasswordChangeMiddleware(lambda r: None)
        needs_change = middleware.user_needs_password_change(user)
        
        return {
            'needs_password_change': needs_change,
            'has_profile': hasattr(user, 'perfil'),
            'profile_data': user.perfil.__dict__ if hasattr(user, 'perfil') else None,
        }
```

### Logging Strategy

```python
# Enhanced logging configuration
LOGGING = {
    'loggers': {
        'usuarios.mandatory_password_middleware': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
        'usuarios.signals': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
    }
}
```

This design ensures consistent middleware execution across all login types, proper profile management for all user types, and comprehensive debugging capabilities to identify and resolve issues quickly.