from django.db import models
from django.contrib.auth.models import User
from lojas.models import Loja


class DashboardStats(models.Model):
    """Modelo para estatísticas do dashboard"""
    
    loja = models.ForeignKey(Loja, on_delete=models.CASCADE, related_name='stats', null=True, blank=True)
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    
    # Estatísticas de vendas
    total_vendas = models.IntegerField(default=0, verbose_name="Total de Vendas")
    vendas_mes = models.IntegerField(default=0, verbose_name="Vendas do Mês")
    vendas_semana = models.IntegerField(default=0, verbose_name="Vendas da Semana")
    vendas_hoje = models.IntegerField(default=0, verbose_name="Vendas de Hoje")
    
    # Estatísticas financeiras
    receita_total = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Receita Total")
    receita_mes = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Receita do Mês")
    receita_semana = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Receita da Semana")
    receita_hoje = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Receita de Hoje")
    
    # Estatísticas de clientes
    total_clientes = models.IntegerField(default=0, verbose_name="Total de Clientes")
    clientes_novos_mes = models.IntegerField(default=0, verbose_name="Clientes Novos do Mês")
    
    # Estatísticas de produtos
    total_produtos = models.IntegerField(default=0, verbose_name="Total de Produtos")
    produtos_estoque_baixo = models.IntegerField(default=0, verbose_name="Produtos com Estoque Baixo")
    
    class Meta:
        verbose_name = "Estatística do Dashboard"
        verbose_name_plural = "Estatísticas do Dashboard"
        ordering = ['-data_criacao']
    
    def __str__(self):
        if self.loja:
            return f"Stats - {self.loja.nome}"
        return "Stats - Sistema"


class Notificacao(models.Model):
    """Modelo para notificações do sistema"""
    
    TIPO_CHOICES = [
        ('info', 'Informação'),
        ('success', 'Sucesso'),
        ('warning', 'Aviso'),
        ('error', 'Erro'),
    ]
    
    PRIORIDADE_CHOICES = [
        ('baixa', 'Baixa'),
        ('media', 'Média'),
        ('alta', 'Alta'),
        ('critica', 'Crítica'),
    ]
    
    titulo = models.CharField(max_length=200, verbose_name="Título")
    mensagem = models.TextField(verbose_name="Mensagem")
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES, default='info', verbose_name="Tipo")
    prioridade = models.CharField(max_length=10, choices=PRIORIDADE_CHOICES, default='media', verbose_name="Prioridade")
    
    # Destinatário
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='notificacoes', null=True, blank=True)
    loja = models.ForeignKey(Loja, on_delete=models.CASCADE, related_name='notificacoes', null=True, blank=True)
    
    # Controle
    lida = models.BooleanField(default=False, verbose_name="Lida")
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    data_leitura = models.DateTimeField(null=True, blank=True, verbose_name="Data de Leitura")
    
    class Meta:
        verbose_name = "Notificação"
        verbose_name_plural = "Notificações"
        ordering = ['-data_criacao']
    
    def __str__(self):
        return self.titulo
    
    def marcar_como_lida(self):
        """Marca a notificação como lida"""
        from django.utils import timezone
        self.lida = True
        self.data_leitura = timezone.now()
        self.save()

