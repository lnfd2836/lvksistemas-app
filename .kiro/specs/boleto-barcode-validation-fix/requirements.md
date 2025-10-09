# Requirements Document

## Introduction

O sistema está apresentando erro de "código de barras inválido" ao processar boletos válidos da Caixa Econômica Federal. A linha digitável `10492.67014 51500.171429 22946.570144 7 22600000002990` está sendo rejeitada pelo sistema, mesmo sendo um código válido conforme padrão FEBRABAN.

**Informação Crítica do Suporte Caixa:** O banco informou que é necessário usar o layout CAIXA SIGCB para processamento correto dos boletos.

O objetivo é corrigir a validação de códigos de barras e linhas digitáveis para aceitar corretamente o layout CAIXA SIGCB e outros formatos válidos de boletos bancários brasileiros.

## Requirements

### Requirement 1

**User Story:** Como usuário do sistema, eu quero que códigos de barras válidos sejam aceitos corretamente, para que eu possa processar pagamentos de boletos sem erros.

#### Acceptance Criteria

1. WHEN inserindo uma linha digitável válida THEN o sistema SHALL aceitar e processar corretamente
2. WHEN a linha digitável segue o padrão FEBRABAN THEN o sistema SHALL validar os dígitos verificadores
3. WHEN há espaços ou pontos na linha digitável THEN o sistema SHALL normalizar automaticamente
4. IF a linha digitável é inválida THEN o sistema SHALL mostrar mensagem de erro específica
5. WHEN convertendo linha digitável para código de barras THEN o sistema SHALL seguir as regras FEBRABAN

### Requirement 2

**User Story:** Como desenvolvedor, eu quero implementar validação robusta de códigos de barras com suporte ao layout CAIXA SIGCB, para que o sistema funcione corretamente com boletos da Caixa Econômica Federal.

#### Acceptance Criteria

1. WHEN processando boletos da Caixa THEN o sistema SHALL usar layout CAIXA SIGCB conforme orientação do banco
2. WHEN validando dígito verificador THEN o sistema SHALL usar algoritmo módulo 10 e módulo 11 apropriado para cada banco
3. WHEN identificando banco 104 (Caixa) THEN o sistema SHALL aplicar regras específicas do SIGCB
4. IF o código tem formato SIGCB THEN o sistema SHALL processar campos específicos deste layout
5. WHEN há erro de validação THEN o sistema SHALL log detalhado incluindo layout detectado

### Requirement 3

**User Story:** Como administrador, eu quero feedback claro sobre erros de código de barras, para que eu possa orientar usuários sobre o formato correto.

#### Acceptance Criteria

1. WHEN há erro de formato THEN o sistema SHALL mostrar exemplo de formato correto
2. WHEN dígito verificador está incorreto THEN o sistema SHALL indicar qual campo tem erro
3. WHEN linha digitável é muito curta/longa THEN o sistema SHALL mostrar tamanho esperado
4. IF há caracteres inválidos THEN o sistema SHALL indicar quais caracteres são permitidos
5. WHEN validação falha THEN o sistema SHALL sugerir verificar se código foi digitado corretamente

### Requirement 4

**User Story:** Como usuário, eu quero que o sistema aceite diferentes formatos de entrada, para que eu possa colar códigos com ou sem formatação.

#### Acceptance Criteria

1. WHEN colando código com espaços THEN o sistema SHALL remover espaços automaticamente
2. WHEN código tem pontos e espaços THEN o sistema SHALL normalizar para apenas números
3. WHEN há quebras de linha THEN o sistema SHALL limpar automaticamente
4. IF código tem 44 dígitos THEN o sistema SHALL aceitar como código de barras direto
5. WHEN código tem 47-48 dígitos THEN o sistema SHALL tratar como linha digitável

### Requirement 5

**User Story:** Como sistema, eu quero converter corretamente entre linha digitável e código de barras, para que ambos formatos sejam suportados.

#### Acceptance Criteria

1. WHEN recebendo linha digitável THEN o sistema SHALL converter para código de barras
2. WHEN recebendo código de barras THEN o sistema SHALL validar diretamente
3. WHEN convertendo formatos THEN o sistema SHALL preservar todos os dados
4. IF conversão falha THEN o sistema SHALL manter formato original para validação
5. WHEN validando qualquer formato THEN o sistema SHALL usar mesmas regras de negócio
### R
equirement 6

**User Story:** Como sistema, eu quero implementar suporte específico ao layout CAIXA SIGCB, para que boletos da Caixa Econômica Federal sejam processados corretamente.

#### Acceptance Criteria

1. WHEN detectando banco 104 (Caixa) THEN o sistema SHALL usar layout SIGCB
2. WHEN processando layout SIGCB THEN o sistema SHALL interpretar campos conforme especificação da Caixa
3. WHEN validando SIGCB THEN o sistema SHALL usar algoritmos de validação específicos deste layout
4. IF boleto é SIGCB THEN o sistema SHALL extrair nosso número, vencimento e valor corretamente
5. WHEN há dúvida sobre layout THEN o sistema SHALL priorizar SIGCB para banco 104