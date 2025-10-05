from django.core.management.base import BaseCommand
from modulos.models import TipoLoja, ModuloLoja, CampoPersonalizado


class Command(BaseCommand):
    help = 'Cria os tipos de loja padrão com suas configurações'

    def handle(self, *args, **options):
        self.stdout.write('Criando tipos de loja...')
        
        # 1. Loja de Conveniência
        conveniencia, created = TipoLoja.objects.get_or_create(
            nome='conveniencia',
            defaults={
                'descricao': 'Loja de conveniência com produtos diversos',
                'icone': 'fas fa-store',
                'cor_primaria': '#28a745',
                'cor_secundaria': '#6c757d',
                'tem_categoria_produto': True,
                'tem_marca_produto': True,
                'tem_codigo_barras': True,
                'tem_estoque_minimo': True,
                'tem_data_nascimento_cliente': True,
                'tem_sexo_cliente': True,
                'tem_cpf_cliente': True,
                'tem_desconto_venda': True,
            }
        )
        
        if created:
            self.stdout.write(f'✅ Criado: {conveniencia.get_nome_display()}')
            
            # Módulos para conveniência
            ModuloLoja.objects.create(
                tipo_loja=conveniencia,
                nome='Produtos',
                descricao='Gerenciamento de produtos',
                icone='fas fa-box',
                url='/lojas/produtos/',
                ordem=1
            )
            
            ModuloLoja.objects.create(
                tipo_loja=conveniencia,
                nome='Clientes',
                descricao='Gerenciamento de clientes',
                icone='fas fa-users',
                url='/lojas/clientes/',
                ordem=2
            )
            
            ModuloLoja.objects.create(
                tipo_loja=conveniencia,
                nome='Vendas',
                descricao='Gerenciamento de vendas',
                icone='fas fa-shopping-cart',
                url='/lojas/vendas/',
                ordem=3
            )
        
        # 2. Loja de Roupas
        roupas, created = TipoLoja.objects.get_or_create(
            nome='roupas',
            defaults={
                'descricao': 'Loja de roupas e acessórios',
                'icone': 'fas fa-tshirt',
                'cor_primaria': '#e83e8c',
                'cor_secundaria': '#6c757d',
                'tem_categoria_produto': True,
                'tem_marca_produto': True,
                'tem_tamanho_produto': True,
                'tem_cor_produto': True,
                'tem_codigo_barras': True,
                'tem_estoque_minimo': True,
                'tem_data_nascimento_cliente': True,
                'tem_sexo_cliente': True,
                'tem_cpf_cliente': True,
                'tem_desconto_venda': True,
            }
        )
        
        if created:
            self.stdout.write(f'✅ Criado: {roupas.get_nome_display()}')
            
            # Módulos para roupas
            ModuloLoja.objects.create(
                tipo_loja=roupas,
                nome='Produtos',
                descricao='Gerenciamento de produtos',
                icone='fas fa-tshirt',
                url='/lojas/produtos/',
                ordem=1
            )
            
            ModuloLoja.objects.create(
                tipo_loja=roupas,
                nome='Clientes',
                descricao='Gerenciamento de clientes',
                icone='fas fa-users',
                url='/lojas/clientes/',
                ordem=2
            )
            
            ModuloLoja.objects.create(
                tipo_loja=roupas,
                nome='Vendas',
                descricao='Gerenciamento de vendas',
                icone='fas fa-shopping-cart',
                url='/lojas/vendas/',
                ordem=3
            )
            
            # Campos personalizados para roupas
            CampoPersonalizado.objects.create(
                tipo_loja=roupas,
                nome='Tamanho',
                slug='tamanho',
                tipo_campo='escolha',
                obrigatorio=True,
                opcoes='PP\nP\nM\nG\nGG\nXG\nXXG',
                ordem=1
            )
            
            CampoPersonalizado.objects.create(
                tipo_loja=roupas,
                nome='Cor',
                slug='cor',
                tipo_campo='escolha',
                obrigatorio=True,
                opcoes='Branco\nPreto\nAzul\nVermelho\nVerde\nAmarelo\nRosa\nRoxo',
                ordem=2
            )
        
        # 3. Loja de Tintas
        tintas, created = TipoLoja.objects.get_or_create(
            nome='tintas',
            defaults={
                'descricao': 'Loja especializada em tintas e materiais de pintura',
                'icone': 'fas fa-paint-brush',
                'cor_primaria': '#ffc107',
                'cor_secundaria': '#6c757d',
                'tem_categoria_produto': True,
                'tem_marca_produto': True,
                'tem_volume_produto': True,
                'tem_codigo_barras': True,
                'tem_estoque_minimo': True,
                'tem_data_nascimento_cliente': True,
                'tem_sexo_cliente': True,
                'tem_cpf_cliente': True,
                'tem_desconto_venda': True,
            }
        )
        
        if created:
            self.stdout.write(f'✅ Criado: {tintas.get_nome_display()}')
            
            # Módulos para tintas
            ModuloLoja.objects.create(
                tipo_loja=tintas,
                nome='Produtos',
                descricao='Gerenciamento de produtos',
                icone='fas fa-paint-brush',
                url='/lojas/produtos/',
                ordem=1
            )
            
            ModuloLoja.objects.create(
                tipo_loja=tintas,
                nome='Clientes',
                descricao='Gerenciamento de clientes',
                icone='fas fa-users',
                url='/lojas/clientes/',
                ordem=2
            )
            
            ModuloLoja.objects.create(
                tipo_loja=tintas,
                nome='Vendas',
                descricao='Gerenciamento de vendas',
                icone='fas fa-shopping-cart',
                url='/lojas/vendas/',
                ordem=3
            )
            
            # Campos personalizados para tintas
            CampoPersonalizado.objects.create(
                tipo_loja=tintas,
                nome='Volume (Litros)',
                slug='volume',
                tipo_campo='decimal',
                obrigatorio=True,
                ordem=1
            )
            
            CampoPersonalizado.objects.create(
                tipo_loja=tintas,
                nome='Tipo de Tinta',
                slug='tipo_tinta',
                tipo_campo='escolha',
                obrigatorio=True,
                opcoes='Acrílica\nEsmalte\nVerniz\nPrimer\nBase\nAcabamento',
                ordem=2
            )
        
        # 4. Supermercado
        supermercado, created = TipoLoja.objects.get_or_create(
            nome='supermercado',
            defaults={
                'descricao': 'Supermercado com produtos alimentícios e diversos',
                'icone': 'fas fa-shopping-basket',
                'cor_primaria': '#17a2b8',
                'cor_secundaria': '#6c757d',
                'tem_categoria_produto': True,
                'tem_marca_produto': True,
                'tem_peso_produto': True,
                'tem_data_validade': True,
                'tem_codigo_barras': True,
                'tem_estoque_minimo': True,
                'tem_data_nascimento_cliente': True,
                'tem_sexo_cliente': True,
                'tem_cpf_cliente': True,
                'tem_desconto_venda': True,
            }
        )
        
        if created:
            self.stdout.write(f'✅ Criado: {supermercado.get_nome_display()}')
            
            # Módulos para supermercado
            ModuloLoja.objects.create(
                tipo_loja=supermercado,
                nome='Produtos',
                descricao='Gerenciamento de produtos',
                icone='fas fa-shopping-basket',
                url='/lojas/produtos/',
                ordem=1
            )
            
            ModuloLoja.objects.create(
                tipo_loja=supermercado,
                nome='Clientes',
                descricao='Gerenciamento de clientes',
                icone='fas fa-users',
                url='/lojas/clientes/',
                ordem=2
            )
            
            ModuloLoja.objects.create(
                tipo_loja=supermercado,
                nome='Vendas',
                descricao='Gerenciamento de vendas',
                icone='fas fa-shopping-cart',
                url='/lojas/vendas/',
                ordem=3
            )
            
            # Campos personalizados para supermercado
            CampoPersonalizado.objects.create(
                tipo_loja=supermercado,
                nome='Peso (kg)',
                slug='peso',
                tipo_campo='decimal',
                obrigatorio=False,
                ordem=1
            )
            
            CampoPersonalizado.objects.create(
                tipo_loja=supermercado,
                nome='Data de Validade',
                slug='data_validade',
                tipo_campo='data',
                obrigatorio=False,
                ordem=2
            )
        
        # 5. Lanchonete
        lanchonete, created = TipoLoja.objects.get_or_create(
            nome='lanchonete',
            defaults={
                'descricao': 'Lanchonete com cardápio e mesas',
                'icone': 'fas fa-utensils',
                'cor_primaria': '#fd7e14',
                'cor_secundaria': '#6c757d',
                'tem_categoria_produto': True,
                'tem_marca_produto': False,
                'tem_codigo_barras': False,
                'tem_estoque_minimo': True,
                'tem_data_nascimento_cliente': False,
                'tem_sexo_cliente': False,
                'tem_cpf_cliente': False,
                'tem_desconto_venda': True,
                'tem_taxa_entrega': True,
                'tem_mesa_venda': True,
                'tem_garcom_venda': True,
            }
        )
        
        if created:
            self.stdout.write(f'✅ Criado: {lanchonete.get_nome_display()}')
            
            # Módulos para lanchonete
            ModuloLoja.objects.create(
                tipo_loja=lanchonete,
                nome='Cardápio',
                descricao='Gerenciamento do cardápio',
                icone='fas fa-utensils',
                url='/lojas/produtos/',
                ordem=1
            )
            
            ModuloLoja.objects.create(
                tipo_loja=lanchonete,
                nome='Mesas',
                descricao='Gerenciamento de mesas',
                icone='fas fa-chair',
                url='/lojas/mesas/',
                ordem=2
            )
            
            ModuloLoja.objects.create(
                tipo_loja=lanchonete,
                nome='Pedidos',
                descricao='Gerenciamento de pedidos',
                icone='fas fa-clipboard-list',
                url='/lojas/pedidos/',
                ordem=3
            )
            
            # Campos personalizados para lanchonete
            CampoPersonalizado.objects.create(
                tipo_loja=lanchonete,
                nome='Tempo de Preparo (min)',
                slug='tempo_preparo',
                tipo_campo='numero',
                obrigatorio=True,
                ordem=1
            )
            
            CampoPersonalizado.objects.create(
                tipo_loja=lanchonete,
                nome='Ingredientes',
                slug='ingredientes',
                tipo_campo='texto',
                obrigatorio=False,
                ordem=2
            )
        
        self.stdout.write(
            self.style.SUCCESS('✅ Tipos de loja criados com sucesso!')
        )
