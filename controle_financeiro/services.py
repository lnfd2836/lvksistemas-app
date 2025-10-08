"""
Serviços para o controle financeiro
"""

from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
import uuid
from .models import BoletoGerado, ConfiguracaoBoleto, ControleFinanceiro


class BoletoService:
    """Serviço para geração e gerenciamento de boletos"""
    
    def gerar_boleto(self, controle_financeiro, configuracao=None, dias_vencimento=30):
        """
        Gera um novo boleto para o controle financeiro
        
        Args:
            controle_financeiro: Instância do ControleFinanceiro
            configuracao: Configuração de boleto (se None, usa a ativa)
            dias_vencimento: Dias para vencimento do boleto (padrão: 30)
        
        Returns:
            BoletoGerado: Instância do boleto criado
        """
        
        if not configuracao:
            configuracao = ConfiguracaoBoleto.objects.filter(ativo=True).first()
            if not configuracao:
                raise ValueError("Nenhuma configuração de boleto ativa encontrada")
        
        # Gera número único do boleto
        numero_boleto = self._gerar_numero_boleto()
        
        # Calcula data de vencimento
        data_vencimento = timezone.now() + timedelta(days=dias_vencimento)
        
        # Gera linha digitável e código de barras (simulados)
        linha_digitavel = self._gerar_linha_digitavel(configuracao, numero_boleto)
        codigo_barras = self._gerar_codigo_barras(linha_digitavel)
        
        # Cria o boleto
        boleto = BoletoGerado.objects.create(
            controle_financeiro=controle_financeiro,
            configuracao=configuracao,
            numero_boleto=numero_boleto,
            linha_digitavel=linha_digitavel,
            codigo_barras=codigo_barras,
            valor=controle_financeiro.valor_mensal,
            data_vencimento=data_vencimento,
            status='pendente'
        )
        
        # Enviar boleto por email automaticamente
        try:
            from .email_service import BoletoEmailService
            
            email_service = BoletoEmailService()
            email_enviado = email_service.enviar_boleto_por_email(boleto, incluir_pdf=True)
            
            if email_enviado:
                print(f"✅ Email do boleto {numero_boleto} enviado para {controle_financeiro.loja.admin_user.email}")
            else:
                print(f"⚠️ Falha ao enviar email do boleto {numero_boleto}")
                
        except Exception as e:
            print(f"❌ Erro ao enviar email do boleto {numero_boleto}: {str(e)}")
        
        return boleto
    
    def _gerar_numero_boleto(self):
        """Gera um número único para o boleto"""
        timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
        random_suffix = str(uuid.uuid4())[:8].upper()
        return f"BOL{timestamp}{random_suffix}"
    
    def _gerar_linha_digitavel(self, configuracao, numero_boleto):
        """
        Gera linha digitável do boleto seguindo padrão FEBRABAN
        """
        banco = str(configuracao.codigo_banco).zfill(3)
        agencia = str(configuracao.agencia).zfill(4)
        conta = str(configuracao.conta).zfill(10)  # Conta com 10 dígitos
        # Extrair apenas números do número do boleto
        nosso_numero = ''.join(filter(str.isdigit, str(numero_boleto)))[-8:].zfill(8)
        
        # Campo 1: Código do banco + moeda + primeiros 5 dígitos do campo livre
        campo1_base = f"{banco}9{agencia[:1]}{conta[:4]}"
        dv1 = self._calcular_dv_modulo10(campo1_base)
        campo1 = f"{campo1_base[:5]}.{campo1_base[5:]}{dv1}"
        
        # Campo 2: Próximos 10 dígitos do campo livre
        campo2_base = f"{conta[4:]}{nosso_numero[:2]}"
        dv2 = self._calcular_dv_modulo10(campo2_base)
        campo2 = f"{campo2_base[:5]}.{campo2_base[5:]}{dv2}"
        
        # Campo 3: Últimos 10 dígitos do campo livre (apenas números)
        nosso_numero_numerico = ''.join(filter(str.isdigit, nosso_numero))[:6].zfill(6)
        campo3_base = f"{nosso_numero_numerico}{agencia[1:].zfill(4)}"
        dv3 = self._calcular_dv_modulo10(campo3_base)
        campo3 = f"{campo3_base[:5]}.{campo3_base[5:]}{dv3}"
        
        # Campo 4: Dígito verificador geral (sempre 1 para simulação)
        dv_geral = "1"
        
        # Campo 5: Fator de vencimento + valor (14 dígitos)
        # Fator de vencimento (4 dígitos) + valor sem vírgula (10 dígitos)
        fator_vencimento = "0000"  # Simplificado
        valor_sem_virgula = f"{int(self.valor * 100):010d}" if hasattr(self, 'valor') else "0000000000"
        campo5 = f"{fator_vencimento}{valor_sem_virgula}"
        
        return f"{campo1} {campo2} {campo3} {dv_geral} {campo5}"
    
    def _calcular_dv_modulo10(self, codigo):
        """Calcula dígito verificador módulo 10"""
        sequencia = "2121212121"
        soma = 0
        
        for i, digito in enumerate(reversed(codigo)):
            produto = int(digito) * int(sequencia[i % len(sequencia)])
            if produto > 9:
                produto = sum(int(d) for d in str(produto))
            soma += produto
        
        resto = soma % 10
        return 0 if resto == 0 else 10 - resto
    
    def _gerar_codigo_barras(self, linha_digitavel):
        """Gera código de barras baseado na linha digitável"""
        # Remove espaços e pontos da linha digitável
        codigo = linha_digitavel.replace(' ', '').replace('.', '')
        return codigo[:44].ljust(44, '0')  # Garante 44 dígitos
    
    def verificar_boletos_vencidos(self):
        """
        Verifica e atualiza status de boletos vencidos
        
        Returns:
            int: Número de boletos atualizados
        """
        agora = timezone.now()
        
        boletos_vencidos = BoletoGerado.objects.filter(
            status='pendente',
            data_vencimento__lt=agora
        )
        
        count = boletos_vencidos.update(status='vencido')
        return count
    
    def gerar_boletos_automaticos(self, dias_antecedencia=10):
        """
        Gera boletos automaticamente para lojas que vencem em X dias
        
        Args:
            dias_antecedencia: Dias de antecedência para gerar o boleto
        
        Returns:
            dict: Resultado da operação com estatísticas
        """
        
        # Data limite para gerar boletos
        data_limite = timezone.now() + timedelta(days=dias_antecedencia)
        
        # Busca controles financeiros que vencem em até X dias
        controles_vencendo = ControleFinanceiro.objects.filter(
            data_vencimento__lte=data_limite,
            data_vencimento__gt=timezone.now(),
            status='ativa'
        )
        
        # Verifica se há configuração de boleto ativa
        configuracao_ativa = ConfiguracaoBoleto.objects.filter(ativo=True).first()
        if not configuracao_ativa:
            raise ValueError("Nenhuma configuração de boleto ativa encontrada")
        
        resultado = {
            'boletos_gerados': 0,
            'boletos_ja_existentes': 0,
            'erros': [],
            'total_processado': controles_vencendo.count()
        }
        
        for controle in controles_vencendo:
            try:
                # Verifica se já existe um boleto pendente para este controle
                boleto_existente = BoletoGerado.objects.filter(
                    controle_financeiro=controle,
                    status__in=['pendente', 'vencido'],
                    data_vencimento__gte=timezone.now()
                ).exists()
                
                if boleto_existente:
                    resultado['boletos_ja_existentes'] += 1
                    continue
                
                # Gera o boleto
                self.gerar_boleto(controle, configuracao_ativa)
                resultado['boletos_gerados'] += 1
                
            except Exception as e:
                resultado['erros'].append({
                    'loja': controle.loja.nome,
                    'erro': str(e)
                })
        
        return resultado


class FinanceiroService:
    """Serviço para operações financeiras gerais"""
    
    def verificar_vencimentos_automatico(self):
        """
        Verifica e atualiza automaticamente os vencimentos de todas as lojas
        
        Returns:
            dict: Resultado da operação
        """
        controles = ControleFinanceiro.objects.all()
        
        resultado = {
            'total_verificados': controles.count(),
            'atualizados': 0,
            'bloqueados': 0,
            'vencidos': 0
        }
        
        for controle in controles:
            status_anterior = controle.status
            novo_status = controle.verificar_status()
            
            if status_anterior != novo_status:
                resultado['atualizados'] += 1
                
                if novo_status == 'bloqueada':
                    resultado['bloqueados'] += 1
                elif novo_status == 'vencida':
                    resultado['vencidos'] += 1
        
        return resultado
    
    def processar_renovacoes_automaticas(self):
        """
        Processa renovações automáticas para lojas com pagamento em dia
        
        Returns:
            dict: Resultado da operação
        """
        # Busca controles com pagamentos recentes que podem ser renovados
        agora = timezone.now()
        data_limite = agora - timedelta(days=1)  # Pagamentos das últimas 24h
        
        from .models import Pagamento
        
        pagamentos_recentes = Pagamento.objects.filter(
            status='aprovado',
            data_aprovacao__gte=data_limite
        ).select_related('controle_financeiro')
        
        resultado = {
            'renovacoes_processadas': 0,
            'erros': []
        }
        
        for pagamento in pagamentos_recentes:
            try:
                controle = pagamento.controle_financeiro
                
                # Verifica se o pagamento cobre o valor mensal
                if pagamento.valor >= controle.valor_mensal:
                    # Renova por mais 30 dias
                    controle.data_vencimento = agora + timedelta(days=30)
                    controle.status = 'ativa'
                    controle.bloqueada = False
                    controle.save()
                    
                    resultado['renovacoes_processadas'] += 1
                    
            except Exception as e:
                resultado['erros'].append({
                    'pagamento_id': str(pagamento.id),
                    'erro': str(e)
                })
        
        return resultado