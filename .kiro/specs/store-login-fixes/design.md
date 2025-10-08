# Design Document

## Overview

This design addresses two critical issues with the store login system:
1. Authentication problems preventing store administrators from logging in
2. Confusing email content with multiple login URLs

## Architecture

### Issue Analysis

**Problem 1: Login Authentication**
- Store administrators receive provisional credentials but cannot log in
- The system may have issues with email-based authentication
- Password validation or user lookup might be failing

**Problem 2: Email Content**
- Email contains 3 different login URLs causing confusion
- Only one URL should be provided: https://www.lvksistemas.com.br/loja/login/
- Current email format is unprofessional and confusing

## Components and Interfaces

### Authentication Flow Fix
1. **Email Authentication**: Ensure the system properly authenticates using email as username
2. **Password Validation**: Verify provisional passwords are set correctly
3. **User Lookup**: Improve user resolution by email
4. **Error Handling**: Provide clear feedback for authentication failures

### Email Template Improvement
1. **Single URL**: Remove alternative and Heroku URLs
2. **Clean Format**: Improve email formatting and readability
3. **Clear Instructions**: Provide step-by-step login instructions

## Data Models

No changes required to data models. The issue is in the authentication logic and email content.

## Error Handling

### Authentication Errors
- Invalid credentials: Clear message about email/password mismatch
- Inactive account: Specific message about account status
- Missing store association: Clear guidance for users without stores

### Email Delivery
- Log email sending attempts
- Handle email delivery failures gracefully
- Provide fallback communication methods

## Testing Strategy

### Authentication Testing
1. Test login with email as username
2. Test login with provisional passwords
3. Verify error messages are appropriate
4. Test redirect behavior after successful login

### Email Content Testing
1. Verify only one URL is included
2. Test email formatting and readability
3. Confirm URL functionality