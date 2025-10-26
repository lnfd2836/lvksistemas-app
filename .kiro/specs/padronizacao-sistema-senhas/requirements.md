# Requirements Document

## Introduction

Este documento especifica os requisitos para padronizar o sistema de envio de senhas provisórias por email em todos os módulos do sistema LVK Sistemas. O objetivo é criar uma experiência consistente e segura para todos os tipos de usuários.

## Glossary

- **Sistema LVK**: Plataforma completa de gestão de lojas e módulos
- **Senha Provisória**: Senha temporária gerada automaticamente que deve ser alterada no primeiro acesso
- **Super Admin**: Usuário com acesso total ao sistema, pode criar lojas
- **Admin Loja**: Usuário administrador de uma loja específica
- **Usuário de Loja**: Funcionário de uma loja específica com acesso ao banco de dados individual da loja
- **Perfil de Acesso**: Nível de permissão dentro da loja (secretaria, coordenação, professor, etc.)
- **Banco Individual**: Cada loja possui seu próprio banco de dados isolado
- **Isolamento Total**: Nenhuma loja pode acessar dados de outra loja
- **Email Service**: Serviço centralizado para envio de emails com credenciais
- **Middleware Senha**: Componente que força alteração de senha no primeiro acesso

## Requirements

### Requirement 1: Padronização do Envio de Emails

**User Story:** Como administrador do sistema, eu quero que todos os usuários criados recebam suas credenciais por email automaticamente, para que o processo seja consistente e seguro.

#### Acceptance Criteria

1. WHEN um Super Admin é criado, THE Sistema LVK SHALL enviar email com credenciais provisórias
2. WHEN uma Loja é criada com Admin, THE Sistema LVK SHALL enviar email com credenciais para o Admin da Loja
3. WHEN um Usuário de Loja é criado pelo admin da loja, THE Sistema LVK SHALL enviar email com credenciais provisórias
4. WHEN qualquer usuário é criado no sistema, THE Sistema LVK SHALL gerar senha provisória automaticamente
5. THE Email Service SHALL incluir informações específicas do contexto do usuário (loja, módulo, etc.)

### Requirement 2: Serviço Centralizado de Email

**User Story:** Como desenvolvedor, eu quero um serviço centralizado para envio de emails de credenciais, para que o código seja reutilizável e consistente.

#### Acceptance Criteria

1. THE Sistema LVK SHALL implementar classe EmailCredentialsService centralizada
2. THE EmailCredentialsService SHALL suportar diferentes tipos de usuário (super_admin, loja_admin, loja_user)
3. THE EmailCredentialsService SHALL personalizar templates de email por tipo de usuário
4. THE EmailCredentialsService SHALL incluir informações de contexto (nome da loja, módulo, etc.)
5. THE EmailCredentialsService SHALL registrar logs de envio de email

### Requirement 3: Geração Segura de Senhas

**User Story:** Como usuário do sistema, eu quero receber senhas provisórias seguras, para que minha conta esteja protegida.

#### Acceptance Criteria

1. THE Sistema LVK SHALL gerar senhas com mínimo de 12 caracteres
2. THE Sistema LVK SHALL incluir letras maiúsculas, minúsculas e números nas senhas
3. THE Sistema LVK SHALL garantir unicidade das senhas geradas
4. THE Sistema LVK SHALL marcar todas as senhas como provisórias
5. THE Sistema LVK SHALL registrar data/hora de criação da senha provisória

### Requirement 4: Controle de Primeira Alteração

**User Story:** Como usuário que recebeu senha provisória, eu quero ser obrigado a alterar minha senha no primeiro acesso, para garantir a segurança da minha conta.

#### Acceptance Criteria

1. THE Middleware Senha SHALL detectar usuários com senha provisória
2. WHEN usuário com senha provisória acessa o sistema, THE Sistema LVK SHALL redirecionar para alteração de senha
3. THE Sistema LVK SHALL permitir alteração sem senha atual na primeira vez
4. WHEN senha é alterada pela primeira vez, THE Sistema LVK SHALL marcar como senha definitiva
5. THE Sistema LVK SHALL permitir acesso normal após primeira alteração

### Requirement 5: Templates de Email Personalizados

**User Story:** Como usuário que recebe credenciais, eu quero receber um email claro e informativo, para que eu saiba como acessar o sistema.

#### Acceptance Criteria

1. THE Sistema LVK SHALL usar template específico para Super Admin
2. THE Sistema LVK SHALL usar template específico para Admin de Loja
3. THE Sistema LVK SHALL usar template específico para Usuário de Loja (adaptado por tipo de loja)
4. THE Sistema LVK SHALL incluir instruções de primeiro acesso em todos os templates
5. THE Sistema LVK SHALL incluir informações de contato para suporte

### Requirement 6: Integração com Módulos Existentes

**User Story:** Como desenvolvedor, eu quero que a padronização funcione com todos os módulos existentes, para que não haja quebra de funcionalidade.

#### Acceptance Criteria

1. THE Sistema LVK SHALL manter compatibilidade com todos os tipos de loja existentes
2. THE Sistema LVK SHALL integrar com criação de lojas existente
3. THE Sistema LVK SHALL integrar com criação de Super Admins existente
4. THE Sistema LVK SHALL preservar funcionalidades de middleware existentes
5. THE Sistema LVK SHALL manter isolamento de dados por loja

### Requirement 7: Configuração e Personalização

**User Story:** Como administrador do sistema, eu quero poder configurar o envio de emails, para que possa personalizar conforme necessário.

#### Acceptance Criteria

1. THE Sistema LVK SHALL permitir configurar templates de email via settings
2. THE Sistema LVK SHALL permitir desabilitar envio de email para desenvolvimento
3. THE Sistema LVK SHALL permitir configurar remetente dos emails
4. THE Sistema LVK SHALL permitir configurar URLs de acesso por ambiente
5. THE Sistema LVK SHALL registrar tentativas de envio e erros

### Requirement 8: Tratamento de Erros

**User Story:** Como administrador, eu quero que falhas no envio de email não impeçam a criação de usuários, para que o sistema seja resiliente.

#### Acceptance Criteria

1. IF envio de email falhar, THEN THE Sistema LVK SHALL criar usuário mesmo assim
2. IF envio de email falhar, THEN THE Sistema LVK SHALL registrar erro em log
3. IF envio de email falhar, THEN THE Sistema LVK SHALL mostrar credenciais na tela como fallback
4. THE Sistema LVK SHALL permitir reenvio de credenciais posteriormente
5. THE Sistema LVK SHALL notificar administrador sobre falhas de email

### Requirement 9: Auditoria e Logs

**User Story:** Como administrador do sistema, eu quero ter logs de todas as ações relacionadas a senhas, para auditoria e segurança.

#### Acceptance Criteria

1. THE Sistema LVK SHALL registrar criação de usuários com senha provisória
2. THE Sistema LVK SHALL registrar tentativas de envio de email
3. THE Sistema LVK SHALL registrar alterações de senha provisória para definitiva
4. THE Sistema LVK SHALL registrar falhas de envio de email
5. THE Sistema LVK SHALL incluir timestamp e IP em todos os logs

### Requirement 10: Recuperação de Senha na Tela de Login

**User Story:** Como usuário que esqueceu sua senha, eu quero poder solicitar uma nova senha provisória na tela de login, para que possa acessar o sistema novamente.

#### Acceptance Criteria

1. THE Sistema LVK SHALL exibir botão "Esqueceu a senha?" em todas as telas de login
2. WHEN usuário clica em "Esqueceu a senha?", THE Sistema LVK SHALL solicitar email ou username
3. WHEN email/username válido é fornecido, THE Sistema LVK SHALL gerar nova senha provisória
4. THE Sistema LVK SHALL enviar nova senha provisória por email
5. THE Sistema LVK SHALL marcar usuário para alterar senha no próximo login

### Requirement 11: Suporte a Todos os Tipos de Loja com Isolamento

**User Story:** Como usuário criado pelo admin de uma loja, eu quero receber credenciais por email e ter acesso apenas à minha loja específica, com perfil de acesso apropriado.

#### Acceptance Criteria

1. THE Sistema LVK SHALL suportar envio de email para usuários de lojas tipo "conveniencia"
2. THE Sistema LVK SHALL suportar envio de email para usuários de lojas tipo "farmacia"
3. THE Sistema LVK SHALL suportar envio de email para usuários de lojas tipo "lanchonete"
4. THE Sistema LVK SHALL suportar envio de email para usuários de lojas tipo "controle_qualidade" (FATESA)
5. WHEN usuário de loja faz login, THE Sistema LVK SHALL restringir acesso apenas à sua loja associada

### Requirement 13: Isolamento Total com Banco Individual por Loja

**User Story:** Como admin de loja, eu quero que minha loja tenha banco de dados completamente isolado, para que nenhuma outra loja possa acessar nossos dados.

#### Acceptance Criteria

1. WHEN admin de loja cria usuário, THE Sistema LVK SHALL criar usuário no banco individual da loja
2. THE Sistema LVK SHALL garantir que usuário acesse apenas o banco de dados da sua loja
3. THE Sistema LVK SHALL impedir qualquer acesso cruzado entre bancos de lojas diferentes
4. THE Sistema LVK SHALL manter credenciais de banco separadas por loja
5. THE Sistema LVK SHALL personalizar email com informações específicas da loja individual

### Requirement 14: Gerenciamento de Múltiplos Bancos de Dados

**User Story:** Como sistema, eu preciso gerenciar múltiplos bancos de dados individuais por loja, para garantir isolamento total de dados.

#### Acceptance Criteria

1. THE Sistema LVK SHALL manter configuração de banco individual para cada loja
2. THE Sistema LVK SHALL rotear conexões de banco baseado na loja do usuário
3. THE Sistema LVK SHALL aplicar migrações em todos os bancos individuais das lojas
4. THE Sistema LVK SHALL manter backup separado para cada banco de loja
5. THE Sistema LVK SHALL registrar logs de acesso por banco individual

### Requirement 12: Migração de Dados Existentes

**User Story:** Como administrador, eu quero que usuários existentes sejam migrados para o novo sistema, para que todos tenham a mesma experiência.

#### Acceptance Criteria

1. THE Sistema LVK SHALL identificar usuários existentes sem controle de senha provisória
2. THE Sistema LVK SHALL migrar usuários existentes para novo sistema
3. THE Sistema LVK SHALL preservar senhas atuais de usuários existentes
4. THE Sistema LVK SHALL marcar usuários migrados como não precisando alterar senha
5. THE Sistema LVK SHALL permitir reset manual para senha provisória se necessário