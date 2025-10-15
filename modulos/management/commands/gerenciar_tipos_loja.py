from django.core.management.base import BaseCommand
from modulos.models import TipoLoja, ModuloLoja, CampoPersonalizado


class Command(BaseCommand):
    help = 'Gerencia tipos de loja - listar, criar, ativar/desativar'

    def add_arguments(self, parser):
        parser.add_argument(
            '--acao',
            type=str,
            choices=['listar', 'criar', 'ativar', 'desativar', 'detalhes'],
            default='listar',
            help='Ação a ser executada'
        )
        parser.add_argument(
            '--tipo',
            type=str,
            help='Nome do tipo de loja (para ações específicas)'
        )
        parser.add_argument(
            '--nome',
            type=str,
            help='Nome do tipo de loja (para criar)'
        )
        parser.add_argument(
            '--descricao',
            type=str,
            help='Descrição do tipo de loja (para criar)'
        )

    def handle(self, *args, **options):
        acao = options['acao']
        
        if acao == 'listar':
            self.listar_tipos_loja()
        elif acao == 'criar':
            self.criar_tipo_loja(options)
        elif acao == 'ativar':
            self.ativar_tipo_loja(options['tipo'])
        elif acao == 'desativar':
            self.desativar_tipo_loja(options['tipo'])
        elif acao == 'detalhes':
            self.detalhes_tipo_loja(options['tipo'])

    def listar_tipos_loja(self):
        """Lista todos os tipos de loja"""
        self.stdout.write(self.style.SUCCESS('📋 Tipos de Loja Disponíveis:'))
        self.stdout.write('=' * 60)
        
        tipos = TipoLoja.objects.all().order_by('nome')
        
        if not tipos:
            self.stdout.write(self.style.WARNING('⚠️  Nenhum tipo de loja encontrado'))
            return
        
        for tipo in tipos:
            status = '✅ Ativo' if tipo.ativo else '❌ Inativo'
            self.stdout.write(f'🏪 {tipo.get_nome_display()}')
            self.stdout.write(f'   ID: {tipo.nome}')
            self.stdout.write(f'   Status: {status}')
            self.stdout.write(f'   Descrição: {tipo.descricao[:80]}...' if len(tipo.descricao) > 80 else f'   Descrição: {tipo.descricao}')
            self.stdout.write(f'   Módulos: {tipo.modulos.count()}')
            self.stdout.write(f'   Campos personalizados: {tipo.campos_personalizados.count()}')
            self.stdout.write('')

    def criar_tipo_loja(self, options):
        """Cria um novo tipo de loja"""
        nome = options.get('nome')
        descricao = options.get('descricao')
        
        if not nome:
            self.stdout.write(self.style.ERROR('❌ Nome é obrigatório para criar tipo de loja'))
            return
        
        if not descricao:
            self.stdout.write(self.style.ERROR('❌ Descrição é obrigatória para criar tipo de loja'))
            return
        
        # Verificar se já existe
        if TipoLoja.objects.filter(nome=nome).exists():
            self.stdout.write(self.style.ERROR(f'❌ Tipo de loja "{nome}" já existe'))
            return
        
        # Criar tipo de loja
        tipo = TipoLoja.objects.create(
            nome=nome,
            descricao=descricao,
            icone='fas fa-store',
            cor_primaria='#007bff',
            cor_secundaria='#6c757d'
        )
        
        self.stdout.write(self.style.SUCCESS(f'✅ Tipo de loja "{tipo.get_nome_display()}" criado com sucesso!'))
        self.stdout.write(f'   ID: {tipo.id}')

    def ativar_tipo_loja(self, tipo_nome):
        """Ativa um tipo de loja"""
        if not tipo_nome:
            self.stdout.write(self.style.ERROR('❌ Nome do tipo é obrigatório'))
            return
        
        try:
            tipo = TipoLoja.objects.get(nome=tipo_nome)
            tipo.ativo = True
            tipo.save()
            self.stdout.write(self.style.SUCCESS(f'✅ Tipo de loja "{tipo.get_nome_display()}" ativado com sucesso!'))
        except TipoLoja.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'❌ Tipo de loja "{tipo_nome}" não encontrado'))

    def desativar_tipo_loja(self, tipo_nome):
        """Desativa um tipo de loja"""
        if not tipo_nome:
            self.stdout.write(self.style.ERROR('❌ Nome do tipo é obrigatório'))
            return
        
        try:
            tipo = TipoLoja.objects.get(nome=tipo_nome)
            tipo.ativo = False
            tipo.save()
            self.stdout.write(self.style.SUCCESS(f'✅ Tipo de loja "{tipo.get_nome_display()}" desativado com sucesso!'))
        except TipoLoja.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'❌ Tipo de loja "{tipo_nome}" não encontrado'))

    def detalhes_tipo_loja(self, tipo_nome):
        """Mostra detalhes de um tipo de loja"""
        if not tipo_nome:
            self.stdout.write(self.style.ERROR('❌ Nome do tipo é obrigatório'))
            return
        
        try:
            tipo = TipoLoja.objects.get(nome=tipo_nome)
            
            self.stdout.write(self.style.SUCCESS(f'🏪 Detalhes do Tipo de Loja: {tipo.get_nome_display()}'))
            self.stdout.write('=' * 60)
            self.stdout.write(f'ID: {tipo.nome}')
            self.stdout.write(f'Descrição: {tipo.descricao}')
            self.stdout.write(f'Ícone: {tipo.icone}')
            self.stdout.write(f'Cor Primária: {tipo.cor_primaria}')
            self.stdout.write(f'Cor Secundária: {tipo.cor_secundaria}')
            self.stdout.write(f'Status: {"✅ Ativo" if tipo.ativo else "❌ Inativo"}')
            self.stdout.write(f'Data de Criação: {tipo.data_criacao.strftime("%d/%m/%Y %H:%M")}')
            self.stdout.write('')
            
            # Configurações de produto
            self.stdout.write('📦 Configurações de Produto:')
            self.stdout.write(f'   Categoria: {"✅" if tipo.tem_categoria_produto else "❌"}')
            self.stdout.write(f'   Marca: {"✅" if tipo.tem_marca_produto else "❌"}')
            self.stdout.write(f'   Tamanho: {"✅" if tipo.tem_tamanho_produto else "❌"}')
            self.stdout.write(f'   Cor: {"✅" if tipo.tem_cor_produto else "❌"}')
            self.stdout.write(f'   Peso: {"✅" if tipo.tem_peso_produto else "❌"}')
            self.stdout.write(f'   Volume: {"✅" if tipo.tem_volume_produto else "❌"}')
            self.stdout.write(f'   Data Validade: {"✅" if tipo.tem_data_validade else "❌"}')
            self.stdout.write(f'   Código de Barras: {"✅" if tipo.tem_codigo_barras else "❌"}')
            self.stdout.write(f'   Estoque Mínimo: {"✅" if tipo.tem_estoque_minimo else "❌"}')
            self.stdout.write('')
            
            # Configurações de cliente
            self.stdout.write('👥 Configurações de Cliente:')
            self.stdout.write(f'   Data Nascimento: {"✅" if tipo.tem_data_nascimento_cliente else "❌"}')
            self.stdout.write(f'   Sexo: {"✅" if tipo.tem_sexo_cliente else "❌"}')
            self.stdout.write(f'   CPF: {"✅" if tipo.tem_cpf_cliente else "❌"}')
            self.stdout.write(f'   RG: {"✅" if tipo.tem_rg_cliente else "❌"}')
            self.stdout.write(f'   CNPJ: {"✅" if tipo.tem_cnpj_cliente else "❌"}')
            self.stdout.write('')
            
            # Configurações de venda
            self.stdout.write('💰 Configurações de Venda:')
            self.stdout.write(f'   Desconto: {"✅" if tipo.tem_desconto_venda else "❌"}')
            self.stdout.write(f'   Taxa Entrega: {"✅" if tipo.tem_taxa_entrega else "❌"}')
            self.stdout.write(f'   Mesa: {"✅" if tipo.tem_mesa_venda else "❌"}')
            self.stdout.write(f'   Garçom: {"✅" if tipo.tem_garcom_venda else "❌"}')
            self.stdout.write('')
            
            # Módulos
            modulos = tipo.modulos.all().order_by('ordem')
            if modulos:
                self.stdout.write('🔧 Módulos:')
                for modulo in modulos:
                    status = '✅' if modulo.ativo else '❌'
                    self.stdout.write(f'   {status} {modulo.nome} - {modulo.url}')
                self.stdout.write('')
            else:
                self.stdout.write('🔧 Módulos: Nenhum módulo configurado')
                self.stdout.write('')
            
            # Campos personalizados
            campos = tipo.campos_personalizados.all().order_by('ordem')
            if campos:
                self.stdout.write('📝 Campos Personalizados:')
                for campo in campos:
                    status = '✅' if campo.ativo else '❌'
                    obrigatorio = '🔴' if campo.obrigatorio else '🟡'
                    self.stdout.write(f'   {status} {obrigatorio} {campo.nome} ({campo.get_tipo_campo_display()})')
                self.stdout.write('')
            else:
                self.stdout.write('📝 Campos Personalizados: Nenhum campo configurado')
                self.stdout.write('')
                
        except TipoLoja.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'❌ Tipo de loja "{tipo_nome}" não encontrado'))
