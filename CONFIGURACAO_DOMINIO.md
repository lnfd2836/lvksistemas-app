# Configuração do Domínio lvksistemas.com.br

## Status Atual
✅ Domínios adicionados ao Heroku:
- `lvksistemas.com.br`
- `www.lvksistemas.com.br`

✅ Certificados SSL automáticos: Habilitados

## Configuração DNS Necessária

Para que os domínios funcionem, você precisa configurar os registros DNS no seu provedor de domínio (onde você comprou o domínio lvksistemas.com.br).

⚠️ **IMPORTANTE**: Os valores abaixo são os corretos obtidos diretamente do Heroku em 05/10/2025.

### Registros DNS a Configurar:

#### 1. Para lvksistemas.com.br (domínio principal)
**Tipo:** ALIAS ou ANAME  
**Nome:** @ (ou deixar em branco)  
**Valor:** `tetrahedral-goose-lm4se1i5s96qkuaqu2fz67jz.herokudns.com`

#### 2. Para www.lvksistemas.com.br (subdomínio www)
**Tipo:** CNAME  
**Nome:** www  
**Valor:** `octagonal-brook-oqbuqqt97582c9psm8wscgs8.herokudns.com`

### ❌ Problema Identificado (05/10/2025)

O registro CNAME atual do www está **incorreto**:
- **Atual (incorreto):** `octagonal-brook-oqbuqq97582c9psm8wscgs8.herokudns.com`
- **Correto:** `octagonal-brook-oqbuqqt97582c9psm8wscgs8.herokudns.com`
- **Diferença:** Falta um "t" na posição 19 (`oqbuqq9` → `oqbuqqt9`)

### Instruções por Provedor:

#### Registro.br (Registro.br)
1. Acesse o painel do Registro.br
2. Vá em "Gerenciar DNS"
3. Adicione os registros conforme especificado acima

#### GoDaddy
1. Acesse o painel do GoDaddy
2. Vá em "DNS Management"
3. Adicione os registros conforme especificado acima

#### Namecheap
1. Acesse o painel do Namecheap
2. Vá em "Advanced DNS"
3. Adicione os registros conforme especificado acima

#### Cloudflare
1. Acesse o painel do Cloudflare
2. Vá em "DNS"
3. Adicione os registros conforme especificado acima

## Verificação Automática

Use nossos scripts para verificar a configuração:

### Verificação Rápida
```bash
python3 scripts/check_domain_status.py
```

### Verificação Completa (Django)
```bash
python manage.py check_dns --verbose --check-ssl
```

### Verificação Manual
```bash
# Verificar CNAME do www
dig www.lvksistemas.com.br CNAME +short

# Verificar domínio raiz
dig lvksistemas.com.br A +short

# Verificar propagação
nslookup www.lvksistemas.com.br
nslookup lvksistemas.com.br
```

## Após Configurar o DNS

1. **Aguarde até 24 horas** para propagação completa
2. **Verifique com os scripts** acima
3. **Teste os domínios**:
   - https://lvksistemas.com.br
   - https://www.lvksistemas.com.br
4. **Certificados SSL** serão gerados automaticamente

## URLs Disponíveis

Após a configuração, o sistema estará disponível em:
- https://lvksistemas.com.br
- https://www.lvksistemas.com.br
- https://lvksistemas-app-4f6fa281e217.herokuapp.com (URL original do Heroku)

## Troubleshooting

### Problema: "Nome ou serviço desconhecido"
**Causa:** Registros DNS não configurados ou incorretos  
**Solução:** Verificar e corrigir registros DNS no provedor

### Problema: "Certificado SSL inválido"
**Causa:** DNS ainda não propagado ou incorreto  
**Solução:** Aguardar propagação DNS, certificados são gerados automaticamente

### Problema: "Site não carrega"
**Causa:** DNS não propagado ou configuração incorreta  
**Solução:** 
1. Verificar DNS com `dig` ou `nslookup`
2. Aguardar propagação (até 24h)
3. Verificar se ALLOWED_HOSTS no Django inclui os domínios

### Problema: Certificados SSL não são gerados
**Causa:** Heroku não consegue validar o domínio  
**Solução:**
1. Verificar se DNS está correto
2. Aguardar propagação completa
3. Forçar renovação: `heroku certs:auto:refresh --app lvksistemas-app`

## Comandos Úteis

### Verificar Status Heroku
```bash
# Ver domínios configurados
heroku domains --app lvksistemas-app

# Ver status dos certificados SSL
heroku certs:auto --app lvksistemas-app

# Forçar renovação de certificados
heroku certs:auto:refresh --app lvksistemas-app
```

### Verificar Propagação DNS
```bash
# Verificar em diferentes servidores DNS
dig @8.8.8.8 www.lvksistemas.com.br CNAME
dig @1.1.1.1 www.lvksistemas.com.br CNAME
dig @208.67.222.222 www.lvksistemas.com.br CNAME
```

## Histórico de Atualizações

- **05/10/2025**: Identificado e corrigido problema no CNAME do www
- **05/10/2025**: Habilitados certificados SSL automáticos
- **05/10/2025**: Adicionados scripts de verificação automática

## Suporte

Se precisar de ajuda com a configuração DNS, entre em contato com o suporte do seu provedor de domínio.

Para problemas técnicos, use os scripts de verificação para diagnóstico detalhado.
