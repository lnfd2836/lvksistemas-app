# Configuração do Domínio lvksistemas.com.br

## Status Atual
✅ Domínios adicionados ao Heroku:
- `lvksistemas.com.br`
- `www.lvksistemas.com.br`

## Configuração DNS Necessária

Para que os domínios funcionem, você precisa configurar os registros DNS no seu provedor de domínio (onde você comprou o domínio lvksistemas.com.br).

### Registros DNS a Configurar:

#### 1. Para lvksistemas.com.br (domínio principal)
**Tipo:** ALIAS ou ANAME  
**Nome:** @ (ou deixar em branco)  
**Valor:** `tetrahedral-goose-lm4se1i5s96qkuaqu2fz67jz.herokudns.com`

#### 2. Para www.lvksistemas.com.br (subdomínio www)
**Tipo:** CNAME  
**Nome:** www  
**Valor:** `octagonal-brook-oqbuqqt97582c9psm8wscgs8.herokudns.com`

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

## Verificação

Após configurar o DNS, aguarde até 24 horas para a propagação completa.

Para verificar se está funcionando:
- Acesse: https://lvksistemas.com.br
- Acesse: https://www.lvksistemas.com.br

## URLs Disponíveis

Após a configuração, o sistema estará disponível em:
- https://lvksistemas.com.br
- https://www.lvksistemas.com.br
- https://lvksistemas-app-4f6fa281e217.herokuapp.com (URL original do Heroku)

## Suporte

Se precisar de ajuda com a configuração DNS, entre em contato com o suporte do seu provedor de domínio.
