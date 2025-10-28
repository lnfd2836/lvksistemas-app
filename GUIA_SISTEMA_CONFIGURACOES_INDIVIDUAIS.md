# 📋 Guia Completo: Sistema de Configurações Individuais por Loja

## 🎯 Visão Geral

O sistema agora possui **configurações individuais por loja**, permitindo que cada loja tenha suas próprias configurações específicas de produtos, clientes, vendas e dashboard, independente do tipo de loja.

## 🔐 Como Acessar

### 1. **Login do Administrador da Loja**
**URL**: `http://0.0.0.0:8000/dashboard/loja/login/`

**Credenciais disponíveis:**
- **Fatesa**: `pjluiz25@hotmail.com` / `A0aDCEipGkby`
- **Clinica Harmonis**: `consultorluizfelix@hotmail.com` / `2Cb68tqXzAOt`
- **FELIX**: `financeiroluiz@hotmail.com` / `hr94sM3duiM2`

### 2. **Acesso às Configurações**
Após o login, acesse as configurações através do dashboard ou diretamente:

**URLs diretas:**
- **Fatesa**: `http://0.0.0.0:8000/lojas/78e5360e-142a-4f93-90bb-8617468ff8e9/configuracoes/`
- **Clinica Harmonis**: `http://0.0.0.0:8000/lojas/88fe37a5-6282-4cf5-bc16-b04df0dce8d7/configuracoes/`
- **FELIX**: `http://0.0.0.0:8000/lojas/feeac6c9-0af3-4885-9592-9c6cd196d39c/configuracoes/`

## 🛠️ Funcionalidades Disponíveis

### 📦 **Configurações de Produtos**
- Campos obrigatórios (nome, preço, categoria, código)
- Configurações de preço (mínimo, máximo, permite zero)
- Controle de estoque (ativar/desativar, estoque mínimo)
- Geração automática de códigos com prefixo

### 👥 **Configurações de Clientes**
- Campos obrigatórios (nome, CPF/CNPJ, telefone, email, endereço)
- Validações (CPF/CNPJ, telefone, email, endereço)
- Segmentação de clientes (VIP, Premium, Regular, etc.)

### 💰 **Configurações de Vendas**
- Numeração automática com prefixo
- Configurações de desconto (permitir, percentual máximo)
- Formas de pagamento disponíveis
- Controle de estoque automático
- Exigir cliente na venda

### 📊 **Configurações de Dashboard**
- Widgets habilitados (vendas hoje, vendas mês, clientes novos, etc.)
- Layout (2, 3 ou 4 colunas)
- Tema de cores (padrão, azul, verde, roxo, escuro)
- Período padrão de análise
- Métricas principais
- Gráficos habilitados
- **Preview do dashboard** disponível

## 🎨 **Tipos de Loja Simplificados**

**URL**: `http://0.0.0.0:8000/modulos/tipos-loja/`

**Agora serve apenas para:**
- ✅ Categorização das lojas
- ✅ Informações visuais (ícone, cores)
- ✅ Descrição do tipo de negócio

**Removido (agora individual por loja):**
- ❌ Configurações específicas de produtos
- ❌ Configurações específicas de clientes  
- ❌ Configurações específicas de vendas

## 🔄 **Fluxo de Uso**

### Para Administradores de Loja:
1. **Acesse**: `http://0.0.0.0:8000/dashboard/loja/login/`
2. **Faça login** com suas credenciais
3. **No dashboard**, procure por "Configurações" ou acesse diretamente a URL de configurações
4. **Configure** cada aba conforme suas necessidades:
   - **Produtos**: Defina campos obrigatórios, preços, estoque
   - **Clientes**: Configure validações e segmentação
   - **Vendas**: Configure numeração, descontos, pagamentos
   - **Dashboard**: Personalize widgets, layout e tema

### Para Super Administradores:
1. **Acesse**: `http://0.0.0.0:8000/`
2. **Gerencie tipos de loja**: `http://0.0.0.0:8000/modulos/tipos-loja/`
3. **Acesse configurações de qualquer loja** através do painel administrativo

## 📊 **Recursos Especiais**

### 🎨 **Preview do Dashboard**
Cada loja pode visualizar como ficará seu dashboard personalizado:
- Acesse a aba "Dashboard" nas configurações
- Clique em "Visualizar Preview"
- Veja como ficará com os widgets e tema escolhidos

### 💾 **Salvamento Automático**
- Configurações são salvas automaticamente via AJAX
- Feedback visual imediato
- Sem necessidade de recarregar a página

### 🎨 **Temas Personalizados**
- Padrão, Azul, Verde, Roxo, Escuro
- Cores personalizáveis por tipo de loja
- Interface adaptável

## ✅ **Status do Sistema**

### 🎉 **100% Funcional**
- ✅ 3 lojas configuradas e testadas
- ✅ Login das lojas funcionando
- ✅ Configurações individuais implementadas
- ✅ Templates criados e validados
- ✅ Tipos de loja simplificados
- ✅ Sistema de preview funcionando
- ✅ Banco de dados migrado
- ✅ URLs configuradas corretamente

### 🚀 **Pronto para Uso**
O sistema está **completamente funcional** e pronto para ser usado pelos administradores das lojas para configurar suas operações de forma individual e personalizada.

## 🔗 **Links Rápidos**

- **Login das Lojas**: `http://0.0.0.0:8000/dashboard/loja/login/`
- **Tipos de Loja**: `http://0.0.0.0:8000/modulos/tipos-loja/`
- **Super Admin**: `http://0.0.0.0:8000/`