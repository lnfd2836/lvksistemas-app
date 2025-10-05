# Referência Rápida - DNS lvksistemas.com.br

## 🎯 Configuração Correta (Copie e Cole)

### www.lvksistemas.com.br
```
Tipo: CNAME
Nome: www
Valor: octagonal-brook-oqbuqqt97582c9psm8wscgs8.herokudns.com
```

### lvksistemas.com.br
```
Tipo: ALIAS ou ANAME
Nome: @ (ou deixar em branco)
Valor: tetrahedral-goose-lm4se1i5s96qkuaqu2fz67jz.herokudns.com
```

## ⚡ Verificação Rápida

```bash
# Verificar se está funcionando
python3 scripts/check_domain_status.py

# Verificar DNS manualmente
dig www.lvksistemas.com.br CNAME +short
dig lvksistemas.com.br A +short
```

## 🔧 Status Esperado

### ✅ Funcionando
```
✅ DNS CNAME: OK
✅ DNS A: OK  
✅ Conectividade: OK
✅ Heroku CLI disponível
✅ Domínios configurados no Heroku
```

### ❌ Problema Atual
```
❌ DNS CNAME: INCORRETO (falta um "t")
❌ DNS A: NÃO ENCONTRADO
❌ Conectividade: FALHA
```

## 📞 Onde Corrigir

Acesse o painel do seu **provedor de DNS** (onde você comprou o domínio):
- Registro.br → "Gerenciar DNS"
- GoDaddy → "DNS Management"  
- Namecheap → "Advanced DNS"
- Cloudflare → "DNS"

## ⏱️ Tempo de Propagação

- **Mínimo**: 15 minutos
- **Típico**: 2-4 horas
- **Máximo**: 24 horas

## 🚨 Emergência

Se precisar de acesso imediato, use a URL direta do Heroku:
```
https://lvksistemas-app-4f6fa281e217.herokuapp.com
```