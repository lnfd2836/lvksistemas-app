# Design Document

## Overview

O problema identificado é uma discrepância entre os DNS targets configurados no Heroku e os registros DNS atuais. O Heroku mostra:
- www.lvksistemas.com.br → `octagonal-brook-oqbuqqt97582c9psm8wscgs8.herokudns.com`
- lvksistemas.com.br → `tetrahedral-goose-lm4se1i5s96qkuaqu2fz67jz.herokudns.com`

Mas o DNS atual aponta para um target ligeiramente diferente, causando falha na resolução.

## Architecture

### Componentes Envolvidos
1. **Heroku App**: lvksistemas-app-4f6fa281e217.herokuapp.com
2. **Domínios Customizados**: lvksistemas.com.br e www.lvksistemas.com.br
3. **Provedor DNS**: Onde o domínio lvksistemas.com.br está registrado
4. **Django Settings**: Configuração ALLOWED_HOSTS

### Fluxo de Resolução DNS
```
Usuário → DNS Provider → Heroku DNS → Heroku App → Django
```

## Components and Interfaces

### 1. Verificação de Configuração Heroku
- Comando: `heroku domains --app lvksistemas-app`
- Verificar se os domínios estão corretamente adicionados
- Confirmar os DNS targets corretos

### 2. Atualização de Registros DNS
- Tipo CNAME para www.lvksistemas.com.br
- Tipo ALIAS/ANAME para lvksistemas.com.br
- Verificação de propagação DNS

### 3. Configuração Django
- Verificar ALLOWED_HOSTS inclui ambos os domínios
- Configurar redirecionamentos se necessário

## Data Models

### DNS Records Structure
```
www.lvksistemas.com.br:
  Type: CNAME
  Target: [correct_heroku_dns_target]

lvksistemas.com.br:
  Type: ALIAS/ANAME  
  Target: [correct_heroku_dns_target]
```

### Django Settings
```python
ALLOWED_HOSTS = [
    'localhost', 
    '127.0.0.1', 
    'lvksistemas-app-4f6fa281e217.herokuapp.com',
    'lvksistemas.com.br', 
    'www.lvksistemas.com.br'
]
```

## Error Handling

### DNS Propagation Issues
- Aguardar até 24 horas para propagação completa
- Usar ferramentas de verificação DNS online
- Testar em diferentes servidores DNS

### Heroku Configuration Issues
- Verificar se os domínios estão corretamente adicionados
- Remover e re-adicionar domínios se necessário
- Verificar certificados SSL

### Django Configuration Issues
- Verificar ALLOWED_HOSTS
- Verificar configurações de segurança (SECURE_SSL_REDIRECT)
- Testar localmente com diferentes hosts

## Testing Strategy

### 1. Verificação DNS
```bash
# Verificar registros CNAME
dig www.lvksistemas.com.br CNAME

# Verificar registros A/ALIAS
dig lvksistemas.com.br A

# Verificar propagação
nslookup www.lvksistemas.com.br
nslookup lvksistemas.com.br
```

### 2. Teste de Conectividade
```bash
# Testar HTTPS
curl -I https://www.lvksistemas.com.br
curl -I https://lvksistemas.com.br

# Verificar certificados SSL
openssl s_client -connect www.lvksistemas.com.br:443
```

### 3. Teste de Aplicação
- Acessar ambos os domínios no navegador
- Verificar redirecionamentos
- Testar funcionalidades principais

## Implementation Steps

1. **Diagnóstico Completo**: Verificar configuração atual do Heroku e DNS
2. **Correção de Registros DNS**: Atualizar registros no provedor DNS
3. **Verificação Heroku**: Confirmar configuração de domínios
4. **Atualização de Documentação**: Corrigir documentação com valores corretos
5. **Testes de Validação**: Verificar funcionamento completo
6. **Monitoramento**: Implementar verificações automáticas