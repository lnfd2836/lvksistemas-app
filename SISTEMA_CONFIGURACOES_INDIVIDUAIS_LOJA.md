# Sistema de Configurações Individuais por Loja

## Visão Geral

Implementação completa de configurações individuais por loja, permitindo que cada loja tenha suas próprias configurações de produtos, clientes, vendas e dashboard personalizados.

## Funcionalidades Implementadas

### 1. Configurações de Produto por Loja
- **Campos Obrigatórios**: Definir quais campos são obrigatórios no cadastro
- **Categorias Personalizadas**: Cada loja pode ter suas próprias categorias
- **Configurações de Preço**: Preço mínimo, máximo, permitir preço zero
- **Configurações de Estoque**: Controle de estoque, estoque mínimo, alertas
- **Configurações de Código**: Geração automática, prefixos personalizados
- **Campos Personalizados**: Campos extras específicos da loja

### 2. Configurações de Cliente por Loja
- **Campos Obrigatórios**: Definir campos obrigatórios no cadastro
- **Validações de Documento**: CPF/CNPJ obrigatório e validação
- **Configurações de Contato**: Telefone, email, endereço obrigatórios
- **Segmentação**: Segmentos personalizados de clientes
- **Auto-cadastro**: Permitir cadastro automático de clientes
- **Campos Personalizados**: Campos extras específicos da loja

### 3. Configurações de Venda por Loja
- **Numeração**: Numeração automática com prefixos personalizados
- **Descontos**: Limites de desconto por percentual e valor
- **Formas de Pagamento**: Formas aceitas por cada loja
- **Estoque**: Baixa automática, venda sem estoque
- **Cliente**: Exigir cliente, permitir cliente genérico
- **Impressão**: Modelos de impressão personalizados
- **Campos Personalizados**: Campos extras específicos da loja

### 4. Configurações de Dashboard por Loja
- **Widgets**: Escolher quais widgets exibir
- **Layout**: Número de colunas (1-4)
- **Período**: Período padrão para relatórios
- **Métricas**: Métricas principais a destacar
- **Gráficos**: Tipos de gráficos habilitados
- **Tema**: Esquema de cores personalizado
- **Configurações Personalizadas**: Configurações específicas da loja

## Estrutura Técnica

### Models Criados
```python
# lojas/models_configuracoes.py
- ConfiguracaoProduto
- ConfiguracaoCliente  
- ConfiguracaoVenda
- ConfiguracaoDashboard
```

### Views Criadas
```python
# lojas/views_configuracoes.py
- gerenciar_configuracoes_loja()
- salvar_configuracao_produto()
- salvar_configuracao_cliente()
- salvar_configuracao_venda()
- salvar_configuracao_dashboard()
- preview_dashboard()
```

### Templates Criados
```html
# templates/lojas/configuracoes/
- gerenciar.html (template principal com abas)
- produto.html (configurações de produto)
- cliente.html (configurações de cliente) - A CRIAR
- venda.html (configurações de venda) - A CRIAR
- dashboard.html (configurações de dashboard) - A CRIAR
- preview_dashboard.html (preview do dashboard) - A CRIAR
```

### URLs Adicionadas
```python
# lojas/urls.py
- configuracoes/ - Gerenciar todas as configurações
- configuracoes/produto/ - Salvar configurações de produto
- configuracoes/cliente/ - Salvar configurações de cliente
- configuracoes/venda/ - Salvar configurações de venda
- configuracoes/dashboard/ - Salvar configurações de dashboard
- configuracoes/preview-dashboard/ - Preview do dashboard
```

## Como Usar

### 1. Acessar Configurações
1. Acesse `/lojas/` como super admin
2. Clique em "Ver Detalhes" de uma loja
3. Clique no botão "Configurações da Loja"

### 2. Configurar por Abas
- **Aba Produtos**: Configure campos, preços, estoque, códigos
- **Aba Clientes**: Configure campos, validações, segmentação
- **Aba Vendas**: Configure numeração, descontos, pagamentos
- **Aba Dashboard**: Configure widgets, layout, métricas

### 3. Salvar Configurações
- Cada aba tem seu próprio formulário
- Configurações são salvas via AJAX
- Feedback visual de sucesso/erro

## Benefícios

### Para o Sistema
- **Flexibilidade**: Cada loja pode ter configurações únicas
- **Escalabilidade**: Fácil adicionar novas configurações
- **Manutenibilidade**: Código organizado e modular
- **Extensibilidade**: Campos personalizados via JSON

### Para as Lojas
- **Personalização**: Configurações específicas do negócio
- **Autonomia**: Cada loja controla suas próprias regras
- **Eficiência**: Dashboard e formulários otimizados
- **Flexibilidade**: Adaptar o sistema às necessidades

## Próximos Passos

### Templates Pendentes
1. **cliente.html** - Formulário de configurações de cliente
2. **venda.html** - Formulário de configurações de venda
3. **dashboard.html** - Formulário de configurações de dashboard
4. **preview_dashboard.html** - Preview do dashboard personalizado

### Funcionalidades Futuras
1. **Importar/Exportar Configurações** - Entre lojas
2. **Templates de Configuração** - Configurações pré-definidas por tipo de loja
3. **Histórico de Alterações** - Rastrear mudanças nas configurações
4. **Validações Avançadas** - Regras de negócio complexas
5. **API de Configurações** - Acesso programático às configurações

## Status Atual

✅ **Concluído:**
- Models de configuração
- Views básicas
- Admin interface
- URLs configuradas
- Template principal
- Template de produto
- Migrações aplicadas
- Botão de acesso adicionado

⏳ **Em Desenvolvimento:**
- Templates restantes (cliente, venda, dashboard)
- Funcionalidades avançadas
- Testes automatizados

🚀 **Pronto para Deploy:**
- Estrutura básica funcional
- Configurações de produto operacionais
- Interface administrativa disponível

## Como Testar

1. **Localmente:**
   ```bash
   python manage.py runserver
   # Acesse: http://localhost:8000/lojas/
   ```

2. **Em Produção:**
   ```bash
   # Deploy já realizado
   # Acesse: https://lvksistemas-app-4f6fa281e217.herokuapp.com/lojas/
   ```

3. **Fluxo de Teste:**
   - Login como super admin
   - Acesse uma loja específica
   - Clique em "Configurações da Loja"
   - Configure produtos na primeira aba
   - Salve e verifique as configurações

## Arquivos Modificados/Criados

### Criados:
- `lojas/models_configuracoes.py`
- `lojas/admin_configuracoes.py`
- `lojas/views_configuracoes.py`
- `templates/lojas/configuracoes/gerenciar.html`
- `templates/lojas/configuracoes/produto.html`
- `lojas/migrations/0010_configuracaocliente_configuracaodashboard_and_more.py`

### Modificados:
- `lojas/urls.py` - Adicionadas URLs de configuração
- `templates/lojas/detalhar.html` - Adicionado botão de configurações

## Conclusão

O sistema de configurações individuais por loja está implementado e funcional. Cada loja agora pode ter suas próprias configurações personalizadas, proporcionando maior flexibilidade e autonomia para os usuários do sistema.