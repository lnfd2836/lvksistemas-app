# Implementation Plan

- [x] 1. Analisar e documentar implementação atual de validação
  - Localizar arquivos que contêm validação de código de barras atual
  - Identificar onde ocorre o erro "código de barras inválido"
  - Documentar algoritmos de validação existentes
  - Mapear fluxo atual de processamento de boletos
  - _Requirements: 1.1, 2.3, 3.4_

- [x] 2. Criar estrutura base para suporte a múltiplos layouts
  - [x] 2.1 Implementar detector de layout de boleto
    - Criar classe BoletoLayoutDetector para identificar tipo de layout
    - Implementar detecção baseada nos primeiros dígitos (banco)
    - Adicionar método específico para detectar SIGCB (banco 104)
    - _Requirements: 2.1, 6.1, 6.5_

  - [x] 2.2 Criar interface comum para validadores
    - Definir interface base ValidationResult para resultados
    - Criar classe abstrata BoletoValidatorBase
    - Implementar estrutura para diferentes tipos de validação
    - _Requirements: 1.1, 2.2, 4.5_

  - [x] 2.3 Implementar normalizador de entrada
    - Criar função para remover espaços, pontos e quebras de linha
    - Implementar detecção automática de formato (44 vs 47-48 dígitos)
    - Adicionar validação básica de caracteres permitidos
    - _Requirements: 4.1, 4.2, 4.3_

- [x] 3. Implementar validador específico para layout CAIXA SIGCB
  - [x] 3.1 Criar classe SIGCBValidator
    - Implementar algoritmo de validação específico para SIGCB
    - Criar método para validar dígitos verificadores do layout Caixa
    - Implementar extração de campos específicos do SIGCB
    - _Requirements: 6.1, 6.2, 6.3_

  - [x] 3.2 Implementar conversão linha digitável para código de barras SIGCB
    - Criar algoritmo de conversão específico para layout SIGCB
    - Implementar validação durante conversão
    - Adicionar tratamento de casos especiais do layout Caixa
    - _Requirements: 5.1, 5.3, 6.4_

  - [x] 3.3 Implementar validação de campos específicos SIGCB
    - Validar estrutura de nosso número SIGCB
    - Implementar validação de agência e conta no formato Caixa
    - Criar validação de carteira específica do SIGCB
    - _Requirements: 6.2, 6.4_

- [x] 4. Criar conversor universal de formatos de boleto
  - [x] 4.1 Implementar classe BoletoFormatConverter
    - Criar método universal linha_to_codigo_barras
    - Implementar método codigo_barras_to_linha
    - Adicionar suporte para diferentes layouts (SIGCB, FEBRABAN padrão)
    - _Requirements: 5.1, 5.2, 5.3_

  - [x] 4.2 Implementar detecção automática de formato de entrada
    - Detectar se entrada é linha digitável ou código de barras
    - Implementar normalização automática baseada no formato
    - Adicionar validação de comprimento por tipo
    - _Requirements: 4.4, 4.5, 5.4_

- [x] 5. Integrar validador unificado no sistema existente
  - [x] 5.1 Criar classe BoletoValidator principal
    - Implementar interface unificada que usa todos os validadores
    - Criar método validate() que detecta layout automaticamente
    - Integrar detector, validadores específicos e conversor
    - _Requirements: 1.1, 1.2, 2.1_

  - [x] 5.2 Substituir validação atual pela nova implementação
    - Localizar pontos no código onde validação atual é chamada
    - Substituir por chamadas ao novo BoletoValidator
    - Manter compatibilidade com interface existente
    - _Requirements: 1.1, 1.4, 2.5_

  - [x] 5.3 Implementar logging detalhado para debug
    - Adicionar logs de detecção de layout
    - Implementar logging de erros específicos por tipo
    - Criar logs para troubleshooting de validação
    - _Requirements: 2.3, 3.1, 3.2_

- [x] 6. Melhorar mensagens de erro e feedback do usuário
  - [x] 6.1 Implementar mensagens de erro específicas
    - Criar mensagens específicas para erros SIGCB
    - Implementar feedback sobre formato esperado
    - Adicionar sugestões de correção para erros comuns
    - _Requirements: 3.1, 3.2, 3.4_

  - [x] 6.2 Adicionar validação de entrada no frontend
    - Implementar validação JavaScript para formato básico
    - Adicionar feedback visual durante digitação
    - Criar exemplos de formato correto na interface
    - _Requirements: 3.1, 3.3, 4.1_

- [ ] 7. Implementar testes abrangentes
  - [x]* 7.1 Criar testes unitários para validador SIGCB
    - Testar validação da linha digitável problema: `10492.67014 51500.171429 22946.570144 7 22600000002990`
    - Criar testes para diferentes casos de boletos Caixa
    - Implementar testes de conversão entre formatos
    - _Requirements: 1.1, 6.1, 6.3_

  - [ ]* 7.2 Criar testes de regressão para outros bancos
    - Testar que Banco do Brasil, Itaú, Bradesco continuam funcionando
    - Implementar testes para diferentes layouts FEBRABAN
    - Validar que mudanças não quebram funcionalidade existente
    - _Requirements: 2.2, 2.5_

  - [ ]* 7.3 Implementar testes de integração
    - Testar fluxo completo de validação no sistema
    - Criar testes end-to-end para processamento de boletos
    - Validar integração com interface de usuário
    - _Requirements: 1.1, 1.5, 5.5_

- [x] 8. Validar correção e otimizar performance
  - [x] 8.1 Testar com casos reais de boletos Caixa
    - Validar especificamente a linha digitável que estava falhando
    - Testar com outros boletos SIGCB reais
    - Confirmar que problema original foi resolvido
    - _Requirements: 1.1, 6.1, 6.4_

  - [x] 8.2 Otimizar performance da validação
    - Implementar cache para validações frequentes
    - Otimizar algoritmos de detecção de layout
    - Medir e melhorar tempo de resposta
    - _Requirements: 2.2, 2.5_

  - [x] 8.3 Documentar implementação e troubleshooting
    - Criar documentação dos algoritmos SIGCB implementados
    - Documentar como adicionar suporte a novos layouts
    - Criar guia de troubleshooting para problemas de validação
    - _Requirements: 3.3, 3.4_
- [ ] 9. Corrigir montagem do campo livre SIGCB para remover dados da conta
  - [ ] 9.1 Analisar implementação atual do campo livre SIGCB
    - Identificar onde dados da conta estão sendo incluídos incorretamente
    - Documentar estrutura atual vs especificação oficial da Caixa
    - Mapear impacto da mudança em códigos existentes
    - _Requirements: 7.1, 7.3_

  - [ ] 9.2 Implementar correção da montagem do campo livre
    - Remover uso de dados da conta corrente na construção do campo livre
    - Implementar estrutura correta: cedente + nosso_numero + agencia_complemento + carteira
    - Adicionar validação para rejeitar campo livre com dados de conta
    - _Requirements: 7.1, 7.2, 7.4_

  - [ ] 9.3 Atualizar validação para detectar códigos com dados de conta
    - Implementar verificação específica para dados de conta no campo livre
    - Adicionar mensagem de erro específica para este problema
    - Criar validação que confirma conformidade com especificação SIGCB
    - _Requirements: 7.3, 7.4, 7.5_

  - [ ] 9.4 Testar correção com código problemático específico
    - Validar que código `10492670145204324981352946570149762600000002990` é corrigido
    - Confirmar que novo código gerado não contém dados de conta
    - Testar conversão entre linha digitável e código de barras corrigido
    - _Requirements: 7.1, 7.2, 7.5_

  - [ ]* 9.5 Criar testes específicos para validação de campo livre SIGCB
    - Implementar testes que verificam ausência de dados de conta
    - Criar casos de teste para diferentes configurações de agência/cedente
    - Validar que códigos antigos com dados de conta são rejeitados
    - _Requirements: 7.3, 7.4_