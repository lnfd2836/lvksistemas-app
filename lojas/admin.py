from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Loja, Cliente, Produto, Venda, ItemVenda, BackupLoja
from usuarios.models import PerfilUsuario, LogAcesso
from dashboard.models import DashboardStats, Notificacao


# Configuração personalizada do UserAdmin
class PerfilUsuarioInline(admin.StackedInline):
    model = PerfilUsuario
    can_delete = False
    verbose_name_plural = 'Perfil'


class CustomUserAdmin(UserAdmin):
    inlines = (PerfilUsuarioInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_superuser')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'date_joined')
    search_fields = ('username', 'first_name', 'last_name', 'email')


# Re-registra o UserAdmin
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


@admin.register(Loja)
class LojaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'cnpj', 'email', 'cidade', 'estado', 'status', 'data_criacao')
    list_filter = ('status', 'estado', 'data_criacao')
    search_fields = ('nome', 'cnpj', 'email', 'cidade')
    readonly_fields = ('data_criacao', 'data_atualizacao', 'senha_provisoria')
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('nome', 'cnpj', 'email', 'telefone')
        }),
        ('Endereço', {
            'fields': ('endereco', 'cidade', 'estado', 'cep')
        }),
        ('Configurações', {
            'fields': ('status', 'admin_user', 'senha_provisoria', 'senha_provisoria_expirada')
        }),
        ('Banco de Dados', {
            'fields': ('db_name', 'db_host', 'db_port')
        }),
        ('Controle', {
            'fields': ('data_criacao', 'data_atualizacao')
        })
    )


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nome', 'email', 'telefone', 'cidade', 'estado', 'ativo', 'data_cadastro')
    list_filter = ('ativo', 'sexo', 'estado', 'data_cadastro')
    search_fields = ('nome', 'email', 'cpf', 'cidade')
    readonly_fields = ('data_cadastro',)
    fieldsets = (
        ('Informações Pessoais', {
            'fields': ('nome', 'email', 'telefone', 'cpf', 'data_nascimento', 'sexo')
        }),
        ('Endereço', {
            'fields': ('endereco', 'cidade', 'estado', 'cep')
        }),
        ('Controle', {
            'fields': ('loja', 'ativo', 'data_cadastro')
        })
    )


@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'categoria', 'preco', 'estoque', 'ativo', 'data_cadastro')
    list_filter = ('categoria', 'ativo', 'data_cadastro')
    search_fields = ('nome', 'descricao', 'codigo_barras')
    readonly_fields = ('data_cadastro', 'data_atualizacao')
    fieldsets = (
        ('Informações do Produto', {
            'fields': ('nome', 'descricao', 'categoria', 'codigo_barras', 'imagem')
        }),
        ('Preços e Estoque', {
            'fields': ('preco', 'estoque')
        }),
        ('Controle', {
            'fields': ('loja', 'ativo', 'data_cadastro', 'data_atualizacao')
        })
    )


class ItemVendaInline(admin.TabularInline):
    model = ItemVenda
    extra = 0
    readonly_fields = ('subtotal',)


@admin.register(Venda)
class VendaAdmin(admin.ModelAdmin):
    list_display = ('numero_venda', 'cliente', 'valor_total', 'valor_final', 'status', 'data_venda')
    list_filter = ('status', 'data_venda', 'loja')
    search_fields = ('numero_venda', 'cliente__nome', 'cliente__email')
    readonly_fields = ('numero_venda', 'data_venda', 'data_atualizacao')
    inlines = [ItemVendaInline]
    fieldsets = (
        ('Informações da Venda', {
            'fields': ('numero_venda', 'loja', 'cliente', 'status')
        }),
        ('Valores', {
            'fields': ('valor_total', 'desconto', 'valor_final')
        }),
        ('Controle', {
            'fields': ('data_venda', 'data_atualizacao')
        })
    )


@admin.register(BackupLoja)
class BackupLojaAdmin(admin.ModelAdmin):
    list_display = ('loja', 'nome_arquivo', 'tamanho_arquivo', 'sucesso', 'data_backup')
    list_filter = ('sucesso', 'data_backup', 'loja')
    search_fields = ('loja__nome', 'nome_arquivo')
    readonly_fields = ('data_backup',)
    fieldsets = (
        ('Informações do Backup', {
            'fields': ('loja', 'nome_arquivo', 'tamanho_arquivo', 'caminho_arquivo')
        }),
        ('Status', {
            'fields': ('sucesso', 'observacoes', 'data_backup')
        })
    )


@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_loja_admin', 'is_super_admin', 'ultimo_acesso')
    list_filter = ('is_loja_admin', 'is_super_admin', 'ultimo_acesso')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('ultimo_acesso', 'ip_ultimo_acesso')


@admin.register(LogAcesso)
class LogAcessoAdmin(admin.ModelAdmin):
    list_display = ('user', 'acao', 'ip_address', 'sucesso', 'data_acesso')
    list_filter = ('acao', 'sucesso', 'data_acesso')
    search_fields = ('user__username', 'ip_address')
    readonly_fields = ('data_acesso',)


@admin.register(DashboardStats)
class DashboardStatsAdmin(admin.ModelAdmin):
    list_display = ('loja', 'total_vendas', 'receita_total', 'data_criacao')
    list_filter = ('data_criacao', 'loja')
    search_fields = ('loja__nome',)
    readonly_fields = ('data_criacao',)


@admin.register(Notificacao)
class NotificacaoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'tipo', 'prioridade', 'lida', 'data_criacao')
    list_filter = ('tipo', 'prioridade', 'lida', 'data_criacao')
    search_fields = ('titulo', 'mensagem')
    readonly_fields = ('data_criacao', 'data_leitura')
    fieldsets = (
        ('Notificação', {
            'fields': ('titulo', 'mensagem', 'tipo', 'prioridade')
        }),
        ('Destinatário', {
            'fields': ('usuario', 'loja')
        }),
        ('Status', {
            'fields': ('lida', 'data_criacao', 'data_leitura')
        })
    )


# Configurações do admin
admin.site.site_header = "Sistema de Lojas - Administração"
admin.site.site_title = "Sistema de Lojas"
admin.site.index_title = "Painel de Controle"





