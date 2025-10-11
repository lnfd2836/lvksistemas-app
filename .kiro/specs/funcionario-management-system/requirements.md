# Requirements Document

## Introduction

Este documento define os requisitos para o sistema de cadastro e gerenciamento de funcionários no dashboard da loja. O sistema deve permitir que cada tipo de loja (Lanchonete, Loja de Conveniência, Loja de Roupas, Supermercado, Loja de Tintas, Eletrônicos) tenha tipos específicos de funcionários com diferentes funções e permissões.

## Requirements

### Requirement 1

**User Story:** Como administrador de loja, eu quero cadastrar funcionários com tipos específicos para meu tipo de negócio, para que eu possa organizar melhor minha equipe e definir responsabilidades adequadas.

#### Acceptance Criteria

1. WHEN o administrador acessa a seção de funcionários THEN o sistema SHALL exibir uma interface de cadastro de funcionários
2. WHEN o administrador seleciona "Novo Funcionário" THEN o sistema SHALL apresentar um formulário com campos obrigatórios (nome, email, telefone, tipo de funcionário)
3. WHEN o sistema carrega os tipos de funcionário THEN o sistema SHALL filtrar apenas os tipos compatíveis com o tipo da loja atual
4. WHEN o administrador preenche todos os campos obrigatórios THEN o sistema SHALL validar os dados antes de salvar
5. IF o email já existe no sistema THEN o sistema SHALL exibir mensagem de erro informando duplicidade

### Requirement 2

**User Story:** Como administrador de loja, eu quero visualizar uma lista de todos os funcionários cadastrados, para que eu possa gerenciar minha equipe de forma eficiente.

#### Acceptance Criteria

1. WHEN o administrador acessa a lista de funcionários THEN o sistema SHALL exibir todos os funcionários da loja atual
2. WHEN a lista é carregada THEN o sistema SHALL mostrar nome, tipo de funcionário, status (ativo/inativo) e data de cadastro
3. WHEN o administrador clica em um funcionário THEN o sistema SHALL permitir visualizar detalhes completos
4. WHEN há mais de 20 funcionários THEN o sistema SHALL implementar paginação
5. WHEN o administrador usa a busca THEN o sistema SHALL filtrar funcionários por nome ou tipo

### Requirement 3

**User Story:** Como administrador de loja, eu quero editar informações dos funcionários, para que eu possa manter os dados atualizados.

#### Acceptance Criteria

1. WHEN o administrador clica em "Editar" funcionário THEN o sistema SHALL abrir formulário preenchido com dados atuais
2. WHEN o administrador modifica os dados THEN o sistema SHALL validar as alterações
3. WHEN o administrador salva as alterações THEN o sistema SHALL atualizar os dados e exibir confirmação
4. IF o tipo de funcionário for alterado THEN o sistema SHALL verificar compatibilidade com o tipo da loja
5. WHEN o administrador cancela a edição THEN o sistema SHALL retornar à lista sem salvar alterações### Requ
irement 4

**User Story:** Como administrador de loja, eu quero desativar funcionários que não trabalham mais na empresa, para que eu mantenha apenas funcionários ativos no sistema.

#### Acceptance Criteria

1. WHEN o administrador clica em "Desativar" funcionário THEN o sistema SHALL solicitar confirmação da ação
2. WHEN a desativação é confirmada THEN o sistema SHALL alterar status para "inativo" sem excluir dados
3. WHEN um funcionário é desativado THEN o sistema SHALL manter histórico de atividades do funcionário
4. WHEN o administrador visualiza a lista THEN o sistema SHALL permitir filtrar por funcionários ativos/inativos
5. IF necessário reativar THEN o sistema SHALL permitir alterar status de volta para "ativo"

### Requirement 5

**User Story:** Como sistema, eu preciso definir tipos de funcionários específicos para cada tipo de loja, para que as opções sejam relevantes ao negócio.

#### Acceptance Criteria

1. WHEN o tipo da loja é "Lanchonete" THEN o sistema SHALL oferecer tipos: Atendente, Cozinheiro, Gerente, Caixa
2. WHEN o tipo da loja é "Loja de Conveniência" THEN o sistema SHALL oferecer tipos: Atendente, Repositor, Gerente, Caixa, Segurança
3. WHEN o tipo da loja é "Loja de Roupas" THEN o sistema SHALL oferecer tipos: Vendedor, Provador, Gerente, Caixa, Visual Merchandising
4. WHEN o tipo da loja é "Supermercado" THEN o sistema SHALL oferecer tipos: Operador de Caixa, Repositor, Açougueiro, Padeiro, Gerente, Segurança
5. WHEN o tipo da loja é "Loja de Tintas" THEN o sistema SHALL oferecer tipos: Vendedor Técnico, Colorista, Gerente, Caixa, Estoquista
6. WHEN o tipo da loja é "Eletrônicos" THEN o sistema SHALL oferecer tipos: Vendedor Técnico, Técnico em Eletrônicos, Gerente, Caixa, Estoquista

### Requirement 6

**User Story:** Como administrador de loja, eu quero definir permissões específicas para cada tipo de funcionário, para que cada um tenha acesso apenas às funcionalidades necessárias.

#### Acceptance Criteria

1. WHEN um tipo de funcionário é selecionado THEN o sistema SHALL definir permissões padrão baseadas no tipo
2. WHEN o tipo é "Gerente" THEN o sistema SHALL conceder acesso total ao dashboard da loja
3. WHEN o tipo é "Caixa" THEN o sistema SHALL conceder acesso apenas ao módulo de vendas e relatórios básicos
4. WHEN o tipo é "Vendedor" THEN o sistema SHALL conceder acesso a vendas, clientes e produtos
5. WHEN o tipo é "Estoquista/Repositor" THEN o sistema SHALL conceder acesso apenas ao módulo de estoque
6. IF necessário personalizar THEN o sistema SHALL permitir ajustar permissões individualmente

### Requirement 7

**User Story:** Como funcionário cadastrado, eu quero fazer login no sistema com minhas credenciais, para que eu possa acessar as funcionalidades permitidas para meu tipo.

#### Acceptance Criteria

1. WHEN o funcionário acessa a página de login THEN o sistema SHALL aceitar email e senha como credenciais
2. WHEN as credenciais são válidas THEN o sistema SHALL redirecionar para dashboard com permissões do tipo de funcionário
3. WHEN o funcionário não tem permissão para uma funcionalidade THEN o sistema SHALL exibir mensagem de acesso negado
4. WHEN o funcionário está inativo THEN o sistema SHALL impedir login e exibir mensagem apropriada
5. IF a senha está expirada THEN o sistema SHALL forçar alteração de senha no primeiro login