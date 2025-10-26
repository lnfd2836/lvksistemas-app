# Arquitetura de Isolamento por Loja - LVK Sistemas

## 🏗️ **Visão Geral da Arquitetura**

O sistema LVK utiliza uma arquitetura **híbrida** que combina:
1. **Banco Principal** - Para dados compartilhados e configurações globais
2. **Bancos Isolados por Loja** - Para dados específicos de cada loja

## 📊 **Estrutura de Dados**

### 🗄️ **Banco Principal (PostgreSQL)**
Contém dados **compartilhados** e **configurações globais**:

```
┌─────────────────────────────────────────┐
│           BANCO PRINCIPAL               │
├─────────────────────────────────────────┤
│ • auth_user                             │
│ • lojas_loja                            │
│ • lojas_loginpersonalizado              │
│ • controle_financeiro_controlefinanceiro│
│ • controle_financeiro_boletogerado      │
│ • modulos_tipoloja                      │
│ • planos_planocomercial                 │
│ • usuarios_perfilusuario                │
└─────────────────────────────────────────┘
```

### 🏪 **Bancos Isolados por Loja**
Cada loja tem seu próprio banco para dados específicos:

```
┌─────────────────────────────────────────┐
│         BANCO LOJA_[UUID]               │
├─────────────────────────────────────────┤
│ • lojas_cliente                         │
│ • lojas_produto                         │
│ • lojas_venda                           │
│ • lojas_funcionario                     │
│ • avaliacao_qualidade_curso             │
│ • avaliacao_qualidade_professor         │
│ • modulos_agendamento                   │
│ • modulos_servicoestetica               │
└─────────────────────────────────────────┘
```

## 🔗 **Vinculação de Boletos às Lojas**

### 1. **Modelo ControleFinanceiro**
```python
class ControleFinanceiro(models.Model):
    loja = models.OneToOneField(Loja, on_delete=models.CASCADE)
    plano = models.ForeignKey(PlanoFinanceiro, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    valor_mensal = models.DecimalField(max_digits=10, decimal_places=2)
    data_vencimento = models.DateTimeField()
    # ... outros campos
```

### 2. **Modelo BoletoGerado**
```python
class BoletoGerado(models.Model):
    controle_financeiro = models.ForeignKey('ControleFinanceiro', on_delete=models.CASCADE)
    numero_boleto = models.CharField(max_length=50)
    linha_digitavel = models.CharField(max_length=54)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    data_vencimento = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    # ... outros campos
```

### 3. **Fluxo de Vinculação**
```
Loja (UUID) ←→ ControleFinanceiro (OneToOne) ←→ BoletoGerado (ForeignKey)
     ↓
LoginPersonalizado (OneToOne)
```

## 🔐 **Login Personalizado por Loja**

### 1. **Modelo LoginPersonalizado**
```python
class LoginPersonalizado(models.Model):
    loja = models.OneToOneField(Loja, on_delete=models.CASCADE, related_name='login_personalizado')
    url_personalizada = models.CharField(max_length=100, unique=True)
    tema = models.CharField(max_length=20, choices=TEMA_CHOICES)
    titulo = models.CharField(max_length=200)
    # ... configurações visuais
```

### 2. **URLs Personalizadas**
```
/login/loja-felix/                    → Loja Felix
/login/fatesa-escola-ultrassonografia/ → Loja FATESA
/login/[url_personalizada]/           → Qualquer loja
```

## 🎯 **Router de Banco de Dados**

### 1. **LojaIsoladaDBRouter**
```python
class LojaIsoladaDBRouter:
    # Modelos que sempre usam banco principal
    SYSTEM_MODELS = {
        'auth.user',
        'lojas.loja',
        'lojas.loginpersonalizado',
        'controle_financeiro.controlefinanceiro',
        'controle_financeiro.boletogerado',
    }
    
    # Modelos isolados por loja
    LOJA_MODELS = {
        'lojas.cliente',
        'lojas.produto',
        'lojas.venda',
        'avaliacao_qualidade',
    }
```

### 2. **Lógica de Roteamento**
```python
def db_for_read(self, model, **hints):
    model_label = f"{model._meta.app_label}.{model._meta.model_name}"
    
    if model_label in self.SYSTEM_MODELS:
        return 'default'  # Banco principal
    
    if model_label in self.LOJA_MODELS:
        loja_id = get_current_loja_id()
        return f'loja_{loja_id}'  # Banco isolado
    
    return 'default'
```

## 🔄 **Fluxo de Funcionamento**

### 1. **Login Personalizado**
```
1. Usuário acessa /login/loja-felix/
2. Sistema identifica loja pelo URL
3. Carrega configuração LoginPersonalizado
4. Renderiza template personalizado
5. Após login, define contexto da loja
6. Router direciona queries para banco correto
```

### 2. **Geração de Boletos**
```
1. Sistema identifica loja atual
2. Busca ControleFinanceiro da loja (banco principal)
3. Cria BoletoGerado vinculado ao ControleFinanceiro
4. Boleto fica associado à loja específica
5. Dados ficam no banco principal para acesso global
```

### 3. **Dados Operacionais**
```
1. Usuário logado em loja específica
2. Router identifica contexto da loja
3. Queries de clientes/produtos vão para banco isolado
4. Dados ficam completamente separados por loja
```

## 📋 **Tabelas por Localização**

### 🌐 **Banco Principal (Compartilhado)**
- ✅ `auth_user` - Usuários do sistema
- ✅ `lojas_loja` - Cadastro das lojas
- ✅ `lojas_loginpersonalizado` - Configurações de login
- ✅ `controle_financeiro_controlefinanceiro` - Controle financeiro
- ✅ `controle_financeiro_boletogerado` - Boletos gerados
- ✅ `modulos_tipoloja` - Tipos de loja
- ✅ `planos_planocomercial` - Planos disponíveis

### 🏪 **Banco Isolado (Por Loja)**
- ✅ `lojas_cliente` - Clientes da loja
- ✅ `lojas_produto` - Produtos da loja
- ✅ `lojas_venda` - Vendas da loja
- ✅ `lojas_funcionario` - Funcionários da loja
- ✅ `avaliacao_qualidade_*` - Dados de avaliação (FATESA)
- ✅ `modulos_agendamento` - Agendamentos da loja

## 🔧 **Vantagens da Arquitetura**

### ✅ **Isolamento de Dados**
- Cada loja só acessa seus próprios dados operacionais
- Impossível vazamento de dados entre lojas
- Backup e restore independente por loja

### ✅ **Controle Centralizado**
- Boletos e controle financeiro centralizados
- Login personalizado gerenciado centralmente
- Usuários e permissões unificados

### ✅ **Escalabilidade**
- Bancos isolados podem ser distribuídos
- Performance independente por loja
- Manutenção sem afetar outras lojas

### ✅ **Flexibilidade**
- Cada loja pode ter configurações específicas
- Módulos ativados/desativados por loja
- Temas e personalizações independentes

## 🚨 **Considerações Importantes**

### ⚠️ **Dados Financeiros**
- **Boletos ficam no banco principal** para controle centralizado
- Permite cobrança e gestão unificada
- Relatórios financeiros consolidados

### ⚠️ **Login Personalizado**
- **Configurações no banco principal** para acesso global
- URLs únicas por loja
- Temas e personalizações centralizadas

### ⚠️ **Roteamento Automático**
- Router identifica automaticamente qual banco usar
- Context manager define loja atual
- Middleware controla acesso e isolamento

## 📊 **Exemplo Prático**

### Loja FATESA (controle_qualidade)
```
Banco Principal:
├── Loja: "Fatesa Escola de Ultrassonografia"
├── LoginPersonalizado: tema="corporativo", url="fatesa-escola-ultrassonografia"
├── ControleFinanceiro: plano="Premium", status="ativa"
└── BoletoGerado: valor=R$299,00, vencimento=30/11/2025

Banco Isolado (loja_[uuid]):
├── Cursos: "Ultrassonografia Básica", "Doppler Avançado"
├── Professores: "Dr. João Silva", "Dra. Maria Santos"
├── Avaliações: 150 avaliações de qualidade
└── Relatórios: Estatísticas específicas da FATESA
```

### Loja Felix (clinica_estetica)
```
Banco Principal:
├── Loja: "Loja Felix"
├── LoginPersonalizado: tema="moderno", url="loja-felix"
├── ControleFinanceiro: plano="Básico", status="ativa"
└── BoletoGerado: valor=R$99,00, vencimento=15/11/2025

Banco Isolado (loja_[uuid]):
├── Clientes: "Ana Silva", "Carlos Santos"
├── Produtos: "Limpeza de Pele", "Massagem Relaxante"
├── Agendamentos: 25 agendamentos do mês
└── Vendas: R$15.000,00 em outubro
```

## 🎯 **Conclusão**

A arquitetura híbrida permite:
- **Isolamento total** dos dados operacionais
- **Controle centralizado** de aspectos financeiros e administrativos
- **Personalização individual** por loja
- **Escalabilidade** e **segurança** máximas

Cada boleto fica vinculado à loja através do `ControleFinanceiro`, enquanto o login personalizado permite acesso isolado aos dados específicos de cada loja.