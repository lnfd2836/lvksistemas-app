# Scripts de Verificação DNS

## Visão Geral

Este diretório contém scripts para verificar e monitorar a configuração DNS dos domínios lvksistemas.com.br.

## Scripts Disponíveis

### 1. check_domain_status.py

Script independente para verificação rápida dos domínios.

**Uso:**
```bash
# Verificação básica
python3 scripts/check_domain_status.py

# Tornar executável e rodar diretamente
chmod +x scripts/check_domain_status.py
./scripts/check_domain_status.py
```

**O que verifica:**
- Registros DNS (CNAME e A)
- Conectividade básica
- Status dos domínios no Heroku
- Comparação com configuração esperada

### 2. Django Management Command

Comando Django integrado para verificação avançada.

**Uso:**
```bash
# Verificação básica
python manage.py check_dns

# Verificação detalhada
python manage.py check_dns --verbose

# Incluir verificação SSL
python manage.py check_dns --check-ssl --verbose
```

**Recursos adicionais:**
- Verificação de certificados SSL
- Logs detalhados
- Integração com sistema Django
- Verificação de conectividade HTTP/HTTPS

## Configuração Esperada

### www.lvksistemas.com.br
- **Tipo:** CNAME
- **Target:** `octagonal-brook-oqbuqqt97582c9psm8wscgs8.herokudns.com`

### lvksistemas.com.br
- **Tipo:** ALIAS ou ANAME
- **Target:** `tetrahedral-goose-lm4se1i5s96qkuaqu2fz67jz.herokudns.com`

## Interpretação dos Resultados

### ✅ Status OK
- DNS configurado corretamente
- Conectividade funcionando
- Certificados SSL válidos (se verificado)

### ❌ Status com Problemas
- DNS incorreto ou não encontrado
- Falha de conectividade
- Certificados SSL inválidos ou expirados

### ⚠️ Status de Aviso
- Certificados SSL próximos do vencimento
- Configuração parcialmente funcional

## Troubleshooting

### Problema: DNS não encontrado
**Solução:** Verificar se os registros foram criados no provedor DNS

### Problema: DNS incorreto
**Solução:** Corrigir o target no provedor DNS conforme mostrado

### Problema: Conectividade falha
**Solução:** Aguardar propagação DNS (até 24h) ou verificar firewall

### Problema: SSL falha
**Solução:** Aguardar correção DNS, certificados são gerados automaticamente

## Automação

### Verificação Periódica
```bash
# Adicionar ao crontab para verificação a cada hora
0 * * * * /path/to/project/scripts/check_domain_status.py >> /var/log/dns_check.log 2>&1
```

### Integração CI/CD
```yaml
# Exemplo para GitHub Actions
- name: Check DNS Status
  run: python3 scripts/check_domain_status.py
```

## Dependências

### Script Independente
- Python 3.6+
- Comandos do sistema: `dig`, `nslookup` (opcionais)
- `heroku` CLI (opcional)

### Comando Django
- Django instalado
- Ambiente virtual ativo
- Todas as dependências do projeto