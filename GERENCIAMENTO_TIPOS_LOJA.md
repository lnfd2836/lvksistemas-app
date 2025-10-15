# Gerenciamento de Tipos de Loja

## 🎯 Visão Geral

Sistema completo para gerenciar tipos de loja e suas funcionalidades específicas, incluindo a **Clínica de Estética** com todas as suas particularidades.

## ✅ Tipos de Loja Disponíveis

### **1. Clínica de Estética** 🏥
- **ID**: `clinica_estetica`
- **Status**: ✅ Ativo
- **Descrição**: Sistema completo de agendamentos, tratamentos faciais e corporais, protocolos de emagrecimento e gestão de clientes
- **Ícone**: `fas fa-spa`
- **Cores**: Rosa (#e91e63) e Rosa Claro (#f8bbd9)

#### **Módulos Configurados (7):**
1. **Agendamentos** - `/estetica/agendamentos/`
2. **Serviços** - `/estetica/servicos/`
3. **Protocolos de Emagrecimento** - `/estetica/protocolos/`
4. **Clientes** - `/estetica/clientes/`
5. **Pacotes de Tratamento** - `/estetica/pacotes/`
6. **Retornos** - `/estetica/retornos/`
7. **Relatórios** - `/estetica/relatorios/`

#### **Campos Personalizados (7):**
1. **Tipo de Pele** (Escolha Única) - 🔴 Obrigatório
2. **Fator de Proteção Solar (FPS)** (Número)
3. **Princípio Ativo** (Texto)
4. **Indicação de Uso** (Texto)
5. **Contraindicações** (Texto)
6. **Modo de Uso** (Texto)
7. **Requer Receita Médica** (Sim/Não)

#### **Configurações Específicas:**
- **Produtos**: Categoria ✅, Marca ✅, Peso ✅, Volume ✅, Data Validade ✅, Código de Barras ✅, Estoque Mínimo ✅
- **Clientes**: Data Nascimento ✅, Sexo ✅, CPF ✅, RG ✅
- **Vendas**: Desconto ✅

### **2. Loja de Conveniência** 🏪
- **ID**: `conveniencia`
- **Status**: ✅ Ativo
- **Descrição**: Loja de conveniência com produtos diversos

## 🛠️ Comandos de Gerenciamento

### **Listar Tipos de Loja**
```bash
python manage.py gerenciar_tipos_loja --acao=listar
```
**Saída:**
```
📋 Tipos de Loja Disponíveis:
============================================================
🏪 Clínica de Estética
   ID: clinica_estetica
   Status: ✅ Ativo
   Descrição: Clínica de estética com sistema completo...
   Módulos: 7
   Campos personalizados: 7

🏪 Loja de Conveniência
   ID: conveniencia
   Status: ✅ Ativo
   Descrição: Teste
   Módulos: 0
   Campos personalizados: 0
```

### **Ver Detalhes de um Tipo**
```bash
python manage.py gerenciar_tipos_loja --acao=detalhes --tipo=clinica_estetica
```
**Saída:**
```
🏪 Detalhes do Tipo de Loja: Clínica de Estética
============================================================
ID: clinica_estetica
Descrição: Clínica de estética com sistema completo...
Ícone: fas fa-spa
Cor Primária: #e91e63
Cor Secundária: #f8bbd9
Status: ✅ Ativo
Data de Criação: 15/10/2025 20:00

📦 Configurações de Produto:
   Categoria: ✅
   Marca: ✅
   Tamanho: ❌
   Cor: ❌
   Peso: ✅
   Volume: ✅
   Data Validade: ✅
   Código de Barras: ✅
   Estoque Mínimo: ✅

👥 Configurações de Cliente:
   Data Nascimento: ✅
   Sexo: ✅
   CPF: ✅
   RG: ✅
   CNPJ: ❌

💰 Configurações de Venda:
   Desconto: ✅
   Taxa Entrega: ❌
   Mesa: ❌
   Garçom: ❌

🔧 Módulos:
   ✅ Agendamentos - /estetica/agendamentos/
   ✅ Serviços - /estetica/servicos/
   ✅ Protocolos de Emagrecimento - /estetica/protocolos/
   ✅ Clientes - /estetica/clientes/
   ✅ Pacotes de Tratamento - /estetica/pacotes/
   ✅ Retornos - /estetica/retornos/
   ✅ Relatórios - /estetica/relatorios/

📝 Campos Personalizados:
   ✅ 🔴 Tipo de Pele (Escolha Única)
   ✅ 🟡 Fator de Proteção Solar (FPS) (Número)
   ✅ 🟡 Princípio Ativo (Texto)
   ✅ 🟡 Indicação de Uso (Texto)
   ✅ 🟡 Contraindicações (Texto)
   ✅ 🟡 Modo de Uso (Texto)
   ✅ 🟡 Requer Receita Médica (Sim/Não)
```

### **Criar Novo Tipo de Loja**
```bash
python manage.py gerenciar_tipos_loja --acao=criar --nome=restaurante --descricao="Restaurante com sistema de mesas e garçons"
```

### **Ativar/Desativar Tipo de Loja**
```bash
# Ativar
python manage.py gerenciar_tipos_loja --acao=ativar --tipo=clinica_estetica

# Desativar
python manage.py gerenciar_tipos_loja --acao=desativar --tipo=clinica_estetica
```

## 🎛️ Interface Admin

### **Acesso ao Admin**
- URL: `/admin/modulos/tipoloja/`
- Interface completa para gerenciar tipos de loja
- Filtros por status, data de criação
- Busca por nome e descrição

### **Modelos Disponíveis no Admin**
1. **TipoLoja** - Tipos de loja
2. **ModuloLoja** - Módulos específicos
3. **CampoPersonalizado** - Campos personalizados
4. **ServicoEstetica** - Serviços de estética
5. **ProtocoloEmagrecimento** - Protocolos de emagrecimento
6. **Agendamento** - Agendamentos
7. **Retorno** - Retornos
8. **FichaAnamnese** - Fichas de anamnese
9. **EvolucaoTratamento** - Evolução de tratamentos
10. **PacoteTratamento** - Pacotes de tratamento

## 🔧 Funcionalidades da Clínica de Estética

### **Sistema de Agendamentos**
- Calendário visual mensal
- Gestão de profissionais e horários
- Status em tempo real
- Observações pré e pós-procedimento

### **Serviços Específicos**
- Botox - Área dos Olhos (R$ 800,00)
- Limpeza de Pele Profunda (R$ 120,00)
- Aplicação de Soro Vitamina C (R$ 80,00)
- Drenagem Linfática (R$ 100,00)
- Criolipólise - Abdômen (R$ 400,00)

### **Protocolos de Emagrecimento**
- Protocolo Drenagem + Massagem Modeladora
- Protocolo Criolipólise Completo
- Controle de sessões e intervalos

### **Gestão de Clientes**
- Ficha de anamnese completa
- Histórico médico detalhado
- Evolução do tratamento
- Controle de peso e medidas

### **Sistema de Retornos**
- Agendamento automático
- Tipos: Avaliação, Manutenção, Complementar, Emergência

### **Pacotes Promocionais**
- Pacote Facial Completo
- Pacote Corporal Premium
- Descontos configuráveis

## 📊 Relatórios e Dashboard
- Estatísticas em tempo real
- Faturamento e performance
- Serviços mais populares
- Profissionais mais ativos

## 🚀 Como Usar

### **1. Verificar Tipos Disponíveis**
```bash
python manage.py gerenciar_tipos_loja --acao=listar
```

### **2. Ver Detalhes da Clínica de Estética**
```bash
python manage.py gerenciar_tipos_loja --acao=detalhes --tipo=clinica_estetica
```

### **3. Acessar Interface Admin**
- Ir para `/admin/`
- Navegar para "Módulos" → "Tipos de Loja"
- Gerenciar configurações e módulos

### **4. Acessar Sistema de Estética**
- URL: `/estetica/`
- Dashboard completo com todas as funcionalidades

## ✅ Status Atual

- ✅ **Clínica de Estética**: Completamente configurada e funcional
- ✅ **7 módulos** específicos implementados
- ✅ **7 campos personalizados** para produtos de estética
- ✅ **Interface admin** completa
- ✅ **Comandos de gerenciamento** funcionais
- ✅ **Sistema de agendamentos** operacional
- ✅ **Serviços e protocolos** pré-configurados

## 🎉 Conclusão

O sistema de gerenciamento de tipos de loja está **100% funcional** com a **Clínica de Estética** completamente implementada e configurada. Todos os módulos, campos personalizados e funcionalidades específicas estão operacionais e prontos para uso em produção.

**Data**: $(date)
**Status**: ✅ **COMPLETO E FUNCIONAL**
