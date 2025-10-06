# Design Document

## Overview

O sistema de envio de emails está funcionalmente correto, mas falha devido a credenciais incorretas no arquivo de configuração. O design foca em corrigir a configuração, melhorar a robustez do sistema e implementar ferramentas de diagnóstico para facilitar a manutenção.

## Architecture

### Current Email System
- **Email Backend**: Django SMTP backend configurado para Gmail
- **Templates**: Templates HTML e texto já implementados
- **Integration**: Signals automáticos para envio quando usuários/lojas são criados
- **Utilities**: Funções centralizadas em `usuarios/email_utils.py`

### Proposed Improvements
- **Configuration Management**: Atualização segura das credenciais no .env
- **Error Handling**: Melhor tratamento de erros com logging detalhado
- **Diagnostics**: Comandos de teste aprimorados
- **Resilience**: Sistema que não falha se email não funcionar

## Components and Interfaces

### 1. Configuration Component
**File**: `.env`
**Purpose**: Armazenar credenciais corretas do email
**Changes**:
- Atualizar EMAIL_HOST_USER para `lvksistemas82@gmail.com`
- Atualizar EMAIL_HOST_PASSWORD para a senha fornecida
- Manter configurações existentes do Gmail SMTP

### 2. Email Utilities Component
**File**: `usuarios/email_utils.py`
**Purpose**: Funções centralizadas para envio de email
**Improvements**:
- Melhor logging de erros
- Validação de configurações antes do envio
- Tratamento gracioso de falhas
- Retry mechanism para falhas temporárias

### 3. Testing Component
**File**: `usuarios/management/commands/test_email_system.py`
**Purpose**: Diagnóstico e teste do sistema de email
**Enhancements**:
- Validação completa de configurações
- Testes mais detalhados
- Sugestões de correção para problemas comuns
- Verificação de conectividade

### 4. Signal Handlers
**Files**: `usuarios/signals.py`, `lojas/signals.py`
**Purpose**: Envio automático de emails quando entidades são criadas
**Improvements**:
- Melhor tratamento de exceções
- Logging mais detalhado
- Não interromper criação se email falhar

## Data Models

### Email Configuration
```python
# Environment Variables (.env)
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'lvksistemas82@gmail.com'
EMAIL_HOST_PASSWORD = '[senha_fornecida]'
DEFAULT_FROM_EMAIL = 'noreply@lvksistemas.com.br'
```

### Email Context Data
```python
# User Credentials Email Context
{
    'user': User object,
    'senha_provisoria': str,
    'tipo_usuario': str,
    'site_url': str,
    'login_url': str
}

# Store Credentials Email Context
{
    'loja': Loja object,
    'senha_provisoria': str,
    'site_url': str,
    'login_url': str
}
```

## Error Handling

### Email Send Failures
1. **Authentication Errors**: Log detailed error and suggest credential check
2. **Network Errors**: Implement retry mechanism with exponential backoff
3. **Template Errors**: Validate template rendering before sending
4. **Configuration Errors**: Provide clear diagnostic messages

### Graceful Degradation
- User/Store creation continues even if email fails
- Failed emails are logged for manual follow-up
- Admin notifications for persistent email failures
- Fallback to console output in development

## Testing Strategy

### Unit Tests
- Test email utility functions with mocked SMTP
- Validate template rendering with test data
- Test error handling scenarios
- Verify configuration validation

### Integration Tests
- Test complete email flow with test SMTP server
- Validate signal-triggered email sending
- Test email content and formatting
- Verify error recovery mechanisms

### Manual Testing
- Use improved test command to validate configuration
- Send test emails to verify delivery
- Test with invalid credentials to verify error handling
- Validate email content in different email clients

### Test Commands
```bash
# Test basic email functionality
python manage.py test_email_system --tipo=basico --email=test@example.com

# Test user credential emails
python manage.py test_email_system --tipo=usuario --email=test@example.com

# Test store credential emails
python manage.py test_email_system --tipo=loja --email=test@example.com
```

## Security Considerations

### Credential Management
- Store email password securely in .env file
- Use app-specific passwords for Gmail
- Avoid hardcoding credentials in source code
- Consider using environment-specific configurations

### Email Content Security
- Sanitize user data in email templates
- Use secure SMTP connection (TLS)
- Validate email addresses before sending
- Implement rate limiting for email sending

## Performance Considerations

### Email Sending
- Asynchronous email sending to avoid blocking requests
- Connection pooling for SMTP connections
- Batch email sending for multiple recipients
- Timeout configuration for SMTP operations

### Resource Management
- Limit email template size and complexity
- Optimize image usage in HTML emails
- Monitor email sending rates and quotas
- Implement circuit breaker for persistent failures

## Monitoring and Logging

### Email Activity Logging
```python
# Success logging
logger.info(f"Email sent successfully to {recipient}")

# Error logging
logger.error(f"Failed to send email to {recipient}: {error_details}")

# Configuration logging
logger.warning(f"Email configuration issue: {config_problem}")
```

### Metrics to Track
- Email send success/failure rates
- Email delivery times
- Authentication failures
- Template rendering errors
- SMTP connection issues