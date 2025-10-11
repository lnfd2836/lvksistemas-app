# Design Document

## Overview

Este documento detalha o design para implemer a valiorte ao layoutos de barraB na validação de eis no sistearras de boemtos. O proble códtual é que o sistema rejeita bolets deviddos da Caixa Econômica Federal porque não reconhece o layout específico SIGCB (Sistema Integrado de Ge Cobncária) usado po.

**Probl da Específico:**.6701a digitável `10492.67010144 7 .1714000002990` é144 7 22600000002990` está sendo rejeitada como inválida.

## Architecture

### Current State Analysis

**Linha Da Identificado:**
- Sistema usa validaçãca FEBRABAN que não contempla especificidades do SIGCB
- B92.67104 (Caixa) requer tratament4 7 226000iado conforme orientação do suporte
```tmos de validação estar inadequados para o layout SIGCB

**Layout ra FEBRABAN:**
- Banco: 104 (Caixa Econômicnco + 4 primeiros dígitos do campo livre + DV)
- Formato específico de campo livre diferente do padrão FEBRABAN genérico
- Cagoritmos de dígito ver(15º ao 2podem ter particularidade+ DV)
- Cstrutura de (Dígito mero específicaal)B

### Target Ahitecte

**Val Hierárquica:**
1. **De60000000e Banco**: Identificar b657o pelos prims 3 dígitos
```Seleção de Layout* regras espr banco
3. **Validação EspecíficaUsar algoritmos apropriados para cada layout
4.# VConversão Algura**: Converter entre linha digitávo de barra

#### mponents and Intertion
```python
def 1. Dalize_barc Layout de Boleto
    """
 ``python
class BolLayoutDetect
    #""Detecta o layout esps, hífens boleto baseado no banco"""
    
    deturn normlayout(self, codigo_barras_ou_linha: str) ->tr:
        
def     Detecta o ype(normalizleto
        Returns: 'S 'FEBRABAN_PADRAO', 'OUTROS'
        """
        pass
    
    def is_caixa_sigcb(self, cod-> bool:
         len(rifica se éinoleto Caixa com layout S"""
        pass
```

### 2. Vador SIGCB Específico

`### 2. Linha Digitável Validation
`lass SIGCBValidator:
    v""Validadonhaspecífico para la:XA SIGCB"""
    
    def validate_linha_vel covel(self, linha: str)N
        """Valida digitável"
      Norass
    
    def validate_codigo_barras(self, r) -> bool:
        """Valida código de in [47, 48CB"""
        pass
    
    # Extraract_fields(self, codigtr) -> dict:
    c   """Extrai campos específicos do SIGCB"""
        pass
```

### 3. Co5 = linha_lFormatos

```py Van
class BoletoFordate_campoer:
    """Converte entre linha digitável e código de barras"""
    
    def linha_toate_campo_rras(seo2, linha: str, l10]):) -> str:
        """Converte linha dig verificada código de barras"""
        pass
    
    def codigo_barras_to_linha(self, codigo: str, l3 iut: str) -> str:
       """Converte código de barrnha digitável"""
    # Valida
```

### 4. Validador Unificado

```python
class BoletoValidato
def v""Interface unificada , dv_esperação de boletos"""
    
    Valida dit__(self):
       or = BoletoLayoutDetector
    somaself.sigcb_valior = SIGCBValidat
        self.febraban_validator = FEBRABANValidator()
      .converter = BoletoFormatConverter()
    for i in range(len(campo) - 1, -1, -1):
    def validate(self, codigo_input: str) -> ValidationResult
        """Valida qualquer formato de boleto"""
        pass
```

#   s

### Estrutura do Lay if SIGCB

**  retuDigitável SIGCB (47-48 dígitos):**
```
10492.67014 515001429 22946.570144 7 22600
│### 3. C││ │││││ Barra││ │││││ ││││ │ ││││││││││││││
│││││ │││││ │││││ │││││││ │││││││││ │ alor (10 dígitos)
│││││ lidate_cod│ │││││││ │││││ │││││││ ncimento (4 dígitos)
││  """│││ │││││ │││││││ │││││ ││││ral
│││││ li│││ ódigo de│││││ │││││ 4 díampo 5 (6 dígi
 ││││ │││││ ││││││ └─ DV Campo 4
    if l│││ │││││ └!= 44: (7 dígitos)
│││││ │││││ └─ DV Campo 3
│││││ └─ Campo 3 (5 dígito
    anco + DV +  (pos 1 + DV Campo 1
```
    
    # Mo de Barras  sem DV padígitos):**
`  
104972000029902670151501429229465701
│││││ Calcular││││││││││││││││o 1││││││││││││
│││└─ DV Geral
││└─ co (104)
│└─ Moeda (9 = Real)
└       re 1-3: Banco, "Díição 4: DVicaosição 5: do. imentado: {dv_calculado}, Informado: {dv_informado}"
   

### Campos Especíos SIGCB

```pyt"
@dataclass
class SI
    baquencia =  "104"  #4329876543ixa
    dv_ge= 0tr
    vencimento:
    folor: str
    nosso_numero: str
    agencstr
    resto: str
    cartei
    
    def __purt_init__(self):
        """Validaçõeicas do SIGCB"""
        if self.b - r != "104":
    raise ValueError é específico da Caixa (104)")
```

##`pyror Handling

    ""pos de Erro Específ
    Converte linha digitável para código de barras
  `python
c   liSIGCBValidationErrorode_intion):
    """ecífico de validaç"""
    passtrair partes da linha digitável
    banco = linha[0:3]
    moBoletoLayoutEr4]r(Exception):
    ""_gera de detecção de layout"""
    pass

class BoletoFormatError(Exception):
    """Ertar campo livre
    campo_livre = (linha[4:9] + linha[10:20] + linha[21:31])
    
    # Montar código de barras
    codigo_barras = banco + moeda + dv_geral + vencimento + valor + campo_livre
    
    return codigo_barras

def convert_codigo_to_linha(codigo_barras):
    """
    Converte código de barras para linha digitável
    """
    if len(codigo_barras) != 44:
        raise ValueError("Código de barras deve ter 44 dígitos")
    
    banco = codigo_barras[0:3]
    moeda = codigo_barras[3:4]
    dv_geral = codigo_barras[4:5]
    vencimento = codigo_barras[5:9]
    valor = codigo_barras[9:19]
   python
class TestSI
    # Montar campos da linha digitável
    campo1_base = banco + moeda + campo_livre[0:5]
    campo1_dv = calculate_dv_modulo10(campo1_base)
    campo1 = campo1_base + str(campo1_dv)
    
    campo2_base = campo_livre[5:15]
    campo2_dv = calculate_dv_modulo10(campo2_base)
    campo2 = campo2_base + str(campo2_dv)
    
    campo3_base = campo_livre[15:25]
    campo3_dv = calculate_dv_modulo10(campo3_base)
    campo3 = campo3_base + str(campo3_dv)
    
    campo4 = dv_geral
    campo5 = vencimento + valor
    
    return campo1 + campo2 + campo3 + campo4 + campo5
```

## Components and Interfaces

### 1. BarcodeValidator Class
```python
class BarcodeValidator:
    """
    Classe principal para validação de códigos de barras e linhas digitáveis
    """
    
    def __init__(self):
        self.errors = []
    
    def validate(self, input_code):
        """
        Método principal de validação
        """
        self.errors = Estrutura Base

1. **Analisar código atual de validação**
   - Localizar onde está a validação atual
   - Identificar pontos de falha com boletos Caixa
   - Documentar algoritmos atuais

2. **Criar estrutura base para múltiplos layouts**
   - Implementar detector de layout
   - Criar interface comum para validadores
   - Preparar estrutura para extensibilidade

### Fase 2: Implementação SIGCB

1. **Implementar validador SIGCB específico**
   - Algoritmos de dígito verificador corretos
   - Validação de campos específicos
   - Tratamento de casos especiais

2. **Implementar conversor de formatos**
   - Conversão linha digitável ↔ código de barras
   - Normalização de entrada (remover espaços, pontos)
   - Validação de formato de entrada

### Fase 3: Integração e Testes

1. **Integrar com sistema existente**
   - Substituir validação atual pela nova
   - Manter compatibilidade com outros bancos
   - Adicionar logs detalhados

2. **Testes abrangentes**
   - Casos de teste para SIGCB
   - Testes de regressão para outros bancos
   - Testes de performance

### Fase 4: Validação e Documentação

1. **Validar com casos reais**
   - Testar com boletos Caixa reais
   - Validar com outros bancos
   - Confirmar correção do problema original

2. **Documentar implementação**
   - Documentar algoritmos SIGCB
   - Criar guia de troubleshooting
   - Atualizar documentação de API

## Security Considerations

### Validação Robusta
- Validar todos os inputs antes do processamento
- Sanitizar entradas para evitar injection
- Validar limites de campos numéricos

### Logging de Segurança
- Log de tentativas de validação
- Registro de códigos rejeitados (sem dados sensíveis)
- Monitoramento de padrões suspeitos

## Performance Considerations

### Otimizações
- Cache de validações frequentes
- Detecção rápida de layout por prefixo
- Validação lazy (só valida campos necessários)

### Métricas
- Tempo de validação por tipo de boleto
- Taxa de sucesso por banco
- Performance comparativa antes/depois

## Success Criteria

### Critérios Técnicos
- [ ] Linha digitável `10492.67014 51500.171429 22946.570144 7 22600000002990` validada com sucesso
- [ ] Outros boletos Caixa SIGCB funcionando
- [ ] Compatibilidade mantida com outros bancos
- [ ] Performance igual ou melhor que implementação atual

### Critérios de Negócio
- [ ] Redução de erros de validação para boletos Caixa
- [ ] Feedback positivo dos usuários
- [ ] Suporte adequado ao layout SIGCB conforme orientação do banco
- [ ] Sistema mais robusto para diferentes layouts de boletot BoletoGerado.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'Boleto não encontrado'})
        else:
            errors = validator.get_errors()
            return JsonResponse({'success': False, 'errors': errors})
```

## Data Models

### No Database Changes Required
- Campos existentes `codigo_barras` e `linha_digitavel` são mantidos
- Apenas melhorar validação e conversão entre formatos
- Adicionar métodos de validação nos models existentes

## Validation
```p
# Adicionar ao modelo existente
class BoletoGerado(models.Model):.. campos existentes ...
    
 def clean(self):
        """
        Validação customizada do modelo
     "
        super().clea)
      
        validator = BarcodeValidator()
        
  lf.codigo_barras:         if not validator.validate(self.digo_barras):
                raise ValidationError(           codigo_barras': validaors()
                })
        
        if self.digitavel:
            ifidator.valself.linha_dig):
                raise ValidationError({                'linha_digitaveldator.get_errors()
       })
    
    def save(self, *args, **kwargs):
        ""
      ncronizar códiha antes de salvar
  
        self.syncigo_linha()
        lean()
        super(save(*args, **kwar``

## Err Handling

### Detailessages
```p
ERROR_MESSAGES = {
    'formato 'Formato álido. Use 44 dígitos (códis) ou 47-48 dígitosinha digitável)',
  anho_incorreto': ncorreto. Cód de barras: 44 dí digitável: 47-48 dígitos',
    'caracteres_invalidos': 'Apen são permitidos',
    'dv_cpo1_invalidoerificador do campotá incorreto',   'dv_2_invalidoverificador do campo 2 está iorreto',
_campo3_invalido': 'Dígito verificador do campo 3 está incorrev_geral_invalido': 'Dígito verifigeral está incor   'banco_invalido': 'Código do banco nãhecido',
    'exemplo_formato': lo de linha digitáv0492.67014 1429 22946.570144 7 200000002990'
}
`
### Ltrategy
```pymport logging
r = logging.getLogger('boleto_validation')alidation_ecode, error_type, details):
    """
    Log detalha debug de vdação
    """
    logger.error(fon failed - Input:put_code[:10]}..., Err {er Details: {details}")

def log_validation_success(input_code, ):
    """
    Log de validação bem-
    """
    lf"Validation success - Type: {result_type}, Input: {inputde[:10]}...")
```

## Testing Strategy

### Unit Tests
```python
class TearcodeValidatio
    
    def setUp(       se.validator = BarcodeValidator()
    
ef tesha_digivel_caiida(self):
    ""
        inha digitável da  que esta
        """
        linha = "10492.67014 51500.171429 27 226000000      self.asserself.valiate(lin)
    
est_cod_caixa_valido(self) """
        Testa código de barras corente
        "
        codigo = "10496000000029902670151500171429229465701"
        self.assertTrue(self.validator.validateigo))
    
    def test_conversao_linha_para_codigo(self):
        """
     nversão entre formatos
            linha = "10492.67011500.171429 229 7 22600000000"
        codigo_esperado = "10497220299026701515001765701"      codigo_convertido = self.validator.get_codigo_ba
        self.assertEqual(cigo_convertido, codigo_esperado)
    
    def test_rentes_bancos(self):
        "" Testa validaç com difercos
        """
        # Bo do Brasil, Itaú, Bradesco, etc.
        linhas_validas = [
            "00190.00009 79001 00000.0 7 84600000001000"BB
            "34191.79001 01043.520.150008 1 84600000001",  # Itaú
     dicionar mais exemplos...
        ]
        for linha in linhas_v            wiubTest(linha=linha):
                self.assertTrue(self.validator.va))
```

#Integn Tests
``class TestBoletoValidationIntegration(Tesse):
    
    def test_processmento_linha_digitavel(self):
        ""   Testa processamento complecom linha digitáve      """
        # Criar de teste
        boleto = BoletoGerado.objec
           barras=72260000000299026701515001714292465701"      # ... outroos
        )
        
      tar processamnha digitável
        response = self.client./processar-pagamento/', {
         'codigo_': '10492.67014 51500.171429 22946.570144 7 22600000002990'
        })
        elf.assertEqual(response.status_code,   data = response.json       self.assertTrue(data['success'])
```

## Performance Considons

### Caching Validation Results
```python
o.core.cacht cache

def valith_cache(input  """
    Vcom cache para evitar reprocessamento
    """
    cache_key = f"barcode_validation_{hash(input_code)}"
    result = cache.get(cache_key)
    
    if result is None:
        validator = BarcodeValidator()
        result = validator.validate(input_code)
        cache.set(cache_key, result, timeout=3600)  # 1 hora
    
    return result
```

### Optimization for Bulk Operations
```python
def validate_bulk_codes(codes_list):
    """
    Validação em lote otimizada
    """
    validator = BarcodeValidator()
    results = []
    
    for code in codes_list:
        try:
            is_valid = validator.validate(code)
            results.append({
                'code': code,
                'valid': is_valid,
                'errors': validator.get_errors() if not is_valid else []
            })
        except Exception as e:
            results.append({
                'code': code,
                'valid': False,
                'errors': [str(e)]
            })
    
    return results
```

## Success Criteria

### Technical Success
- [ ] Linha digitável `10492.67014 51500.171429 22946.570144 7 22600000002990` validada corretamente
- [ ] Conversão bidirecional entre linha digitável e código de barras funcionando
- [ ] Validação de dígitos verificadores implementada conforme FEBRABAN
- [ ] Suporte a todos os principais bancos brasileiros
- [ ] Mensagens de erro claras e específicas

### User Experience Success
- [ ] Códigos podem ser colados com ou sem formatação
- [ ] Feedback imediato sobre erros de validação
- [ ] Exemplos de formato correto mostrados em caso de erro
- [ ] Performance mantida ou melhorada

### Business Success
- [ ] Redução significativa de erros de "código inválido"
- [ ] Maior taxa de sucesso no processamento de boletos
- [ ] Menos suporte necessário para problemas de validação
- [ ] Compatibilidade com todos os bancos do sistema
## Corr
eção Específica do Campo Livre SIGCB

### Problema Identificado

O suporte da Caixa Econômica Federal identificou que a montagem do campo livre está incorreta, especificamente:

1. **Dados da conta corrente estão sendo incluídos no código de barras**
2. **O número da conta não deve ser utilizado no código de barras SIGCB**
3. **A estrutura atual está gerando códigos inválidos**

### Análise do Código Atual

No arquivo `controle_financeiro/boleto_caixa_service.py`, linhas 225-231:

```python
# PROBLEMA: Código atual inclui dados da conta
conta_completa = re.sub(r'[^0-9]', '', str(configuracao.conta))
# Para SIGCB, usar os primeiros 2 dígitos da conta (não do código do cedente)
if len(conta_completa) >= 2:
    conta_limpa = conta_completa[:2]  # INCORRETO: Não deve usar conta
else:
    conta_limpa = conta_completa.zfill(2)

agencia_conta_campo = f"{agencia_limpa}{conta_limpa}"  # INCORRETO
```

### Estrutura Correta do Campo Livre SIGCB

Conforme especificação oficial da Caixa, o campo livre deve ter **25 posições**:

```
Posições 20-44 do código de barras (25 dígitos):
CCCCCC NNNNNNNNNN AAAAAA CCC
│      │          │      └─ Carteira (3 dígitos)
│      │          └─ Agência + complemento (6 dígitos) - SEM CONTA
│      └─ Nosso número (10 dígitos)
└─ Código do cedente (6 dígitos)
```

### Correção Necessária

1. **Remover uso da conta corrente** do campo livre
2. **Usar apenas agência + complemento específico** (não conta)
3. **Validar que o campo livre não contém dados de conta**

### Implementação da Correção

```python
def _gerar_codigo_barras_caixa_corrigido(self, configuracao, nosso_numero, valor, fator_vencimento):
    """
    Versão corrigida que NÃO usa dados da conta corrente
    """
    
    # Código do cedente (6 dígitos)
    cedente_limpo = re.sub(r'[^0-9]', '', str(configuracao.codigo_cedente or ''))
    codigo_cedente = cedente_limpo[-6:].zfill(6) if len(cedente_limpo) > 6 else cedente_limpo.zfill(6)
    
    # Nosso número (10 dígitos)
    nosso_numero_limpo = re.sub(r'[^0-9]', '', str(nosso_numero))[-10:].zfill(10)
    
    # CORREÇÃO: Agência + complemento SEM usar conta
    agencia_limpa = re.sub(r'[^0-9]', '', str(configuracao.agencia))[:4].zfill(4)
    
    # Para SIGCB, usar complemento específico baseado na agência ou cedente
    # NÃO usar dados da conta corrente
    complemento = "00"  # Ou outro valor específico conforme documentação Caixa
    agencia_complemento = f"{agencia_limpa}{complemento}"
    
    # Carteira (3 dígitos)
    carteira_limpa = re.sub(r'[^0-9]', '', str(configuracao.carteira))[:3].zfill(3)
    
    # Campo livre: cedente(6) + nosso_numero(10) + agencia_complemento(6) + carteira(3) = 25
    campo_livre = f"{codigo_cedente}{nosso_numero_limpo}{agencia_complemento}{carteira_limpa}"
    
    # Validar que não há dados de conta
    if any(str(configuracao.conta) in campo_livre for _ in [1] if configuracao.conta):
        raise ValueError("Campo livre SIGCB não deve conter dados da conta corrente")
    
    return campo_livre
```

### Validação da Correção

1. **Testar com o código problemático**: `10492670145204324981352946570149762600000002990`
2. **Verificar que não há dados de conta** no campo livre gerado
3. **Validar com outros boletos Caixa** para garantir compatibilidade
4. **Confirmar aprovação do suporte Caixa** após correção

### Impacto da Mudança

- **Códigos existentes** podem precisar ser regenerados
- **Validação mais rigorosa** para detectar códigos com dados de conta
- **Compatibilidade** mantida com especificação oficial SIGCB