"""
Comando para criar e configurar o tipo de loja CRM de Vendas
"""
from django.core.management.base import BaseCommand
from modulos.models import TipoLoja, ModuloLoja


class Command(BaseCommand):
    help = 'Cria e configura o tipo de loja CRM de Vendas com todos os módulos'

    def handle(self, *args, **options):
        self.stdout.write('Criando tipo de loja CRM de Vendas...')
        
        # Criar tipo de loja CRM de Vendas
        # O banco no Heroku ainda tem os campos antigos que são NOT NULL
        # Então precisamos usar SQL direto ou verificar se já existe
        from django.db import connection
        import uuid
        
        # Primeiro verifica se já existe
        try:
            crm_vendas = TipoLoja.objects.get(nome='crm_vendas')
            created = False
            self.stdout.write(self.style.WARNING(f'⚠️  Tipo de loja {crm_vendas.get_nome_display()} já existe.'))
        except TipoLoja.DoesNotExist:
            # Não existe, cria via SQL direto
            tipo_id = uuid.uuid4()
            with connection.cursor() as cursor:
                # Contagem: 6 básicos + 24 campos booleanos = 30 campos
                cursor.execute("""
                    INSERT INTO modulos_tipoloja (
                        id, nome, descricao, icone, cor_primaria, cor_secundaria,
                        tem_categoria_produto, tem_marca_produto, tem_tamanho_produto,
                        tem_cor_produto, tem_peso_produto, tem_volume_produto,
                        tem_data_validade, tem_codigo_barras, tem_estoque_minimo,
                        tem_data_nascimento_cliente, tem_sexo_cliente, tem_cpf_cliente,
                        tem_rg_cliente, tem_cnpj_cliente, tem_crm_cliente,
                        tem_desconto_venda, tem_taxa_entrega, tem_mesa_venda,
                        tem_garcom_venda, ativo, data_criacao
                    ) VALUES (
                        %s::uuid, %s, %s, %s, %s, %s,
                        FALSE, FALSE, FALSE,
                        FALSE, FALSE, FALSE,
                        FALSE, FALSE, FALSE,
                        TRUE, TRUE, TRUE,
                        FALSE, TRUE, FALSE,
                        TRUE, FALSE, FALSE,
                        FALSE, TRUE, NOW()
                    )
                """, [
                    str(tipo_id),
                    'crm_vendas',
                    'Sistema CRM completo para gestão de vendas, leads, orçamentos, propostas e contratos',
                    'fas fa-briefcase',
                    '#007bff',
                    '#0056b3',
                ])
            crm_vendas = TipoLoja.objects.get(id=tipo_id)
            created = True
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'✅ Criado tipo de loja: {crm_vendas.get_nome_display()}'))
        else:
            self.stdout.write(self.style.WARNING(f'⚠️  Tipo de loja {crm_vendas.get_nome_display()} já existe. Atualizando configurações...'))
            crm_vendas.descricao = 'Sistema CRM completo para gestão de vendas, leads, orçamentos, propostas e contratos'
            crm_vendas.icone = 'fas fa-briefcase'
            crm_vendas.cor_primaria = '#007bff'
            crm_vendas.cor_secundaria = '#0056b3'
            crm_vendas.ativo = True
            crm_vendas.save()
        
        # Criar módulos para CRM de Vendas
        modulos_crm = [
            {
                'nome': 'Dashboard',
                'descricao': 'Dashboard principal do CRM',
                'icone': 'fas fa-tachometer-alt',
                'url': '/crm/dashboard/',
                'ordem': 1,
            },
            {
                'nome': 'Leads',
                'descricao': 'Gerenciamento de leads e oportunidades',
                'icone': 'fas fa-user-plus',
                'url': '/crm/leads/',
                'ordem': 2,
            },
            {
                'nome': 'Orçamentos',
                'descricao': 'Criação e gestão de orçamentos',
                'icone': 'fas fa-file-invoice-dollar',
                'url': '/crm/orcamentos/',
                'ordem': 3,
            },
            {
                'nome': 'Propostas',
                'descricao': 'Gerenciamento de propostas comerciais',
                'icone': 'fas fa-file-contract',
                'url': '/crm/propostas/',
                'ordem': 4,
            },
            {
                'nome': 'Contratos',
                'descricao': 'Gestão de contratos e fechamentos',
                'icone': 'fas fa-handshake',
                'url': '/crm/contratos/',
                'ordem': 5,
            },
            {
                'nome': 'Relatórios',
                'descricao': 'Relatórios e análises de vendas',
                'icone': 'fas fa-chart-bar',
                'url': '/crm/relatorios/',
                'ordem': 6,
            },
        ]
        
        modulos_criados = 0
        modulos_atualizados = 0
        
        for modulo_info in modulos_crm:
            modulo, modulo_created = ModuloLoja.objects.get_or_create(
                tipo_loja=crm_vendas,
                nome=modulo_info['nome'],
                defaults={
                    'descricao': modulo_info['descricao'],
                    'icone': modulo_info['icone'],
                    'url': modulo_info['url'],
                    'ordem': modulo_info['ordem'],
                    'ativo': True,
                }
            )
            
            if modulo_created:
                modulos_criados += 1
            else:
                # Atualizar módulo existente
                modulo.descricao = modulo_info['descricao']
                modulo.icone = modulo_info['icone']
                modulo.url = modulo_info['url']
                modulo.ordem = modulo_info['ordem']
                modulo.ativo = True
                modulo.save()
                modulos_atualizados += 1
        
        if modulos_criados > 0:
            self.stdout.write(self.style.SUCCESS(f'✅ Criados {modulos_criados} módulos'))
        
        if modulos_atualizados > 0:
            self.stdout.write(self.style.SUCCESS(f'✅ Atualizados {modulos_atualizados} módulos'))
        
        self.stdout.write(self.style.SUCCESS(f'\n✅ Tipo de loja CRM de Vendas configurado com sucesso!'))
        self.stdout.write(f'   ID: {crm_vendas.id}')
        self.stdout.write(f'   Módulos: {ModuloLoja.objects.filter(tipo_loja=crm_vendas, ativo=True).count()} ativos')

