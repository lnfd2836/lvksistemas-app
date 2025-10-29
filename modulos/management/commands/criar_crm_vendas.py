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
        # Como o modelo atual foi simplificado, criamos com apenas os campos básicos
        # e depois atualizamos via SQL se necessário
        crm_vendas, created = TipoLoja.objects.get_or_create(
            nome='crm_vendas',
            defaults={
                'descricao': 'Sistema CRM completo para gestão de vendas, leads, orçamentos, propostas e contratos',
                'icone': 'fas fa-briefcase',
                'cor_primaria': '#007bff',
                'cor_secundaria': '#0056b3',
                'ativo': True,
            }
        )
        
        # Se o banco ainda tem os campos antigos, atualizamos via SQL direto
        try:
            from django.db import connection
            with connection.cursor() as cursor:
                # Atualiza todos os campos booleanos para valores padrão do CRM
                cursor.execute("""
                    UPDATE modulos_tipoloja 
                    SET 
                        tem_categoria_produto = FALSE,
                        tem_marca_produto = FALSE,
                        tem_tamanho_produto = FALSE,
                        tem_cor_produto = FALSE,
                        tem_peso_produto = FALSE,
                        tem_volume_produto = FALSE,
                        tem_data_validade = FALSE,
                        tem_codigo_barras = FALSE,
                        tem_estoque_minimo = FALSE,
                        tem_data_nascimento_cliente = TRUE,
                        tem_sexo_cliente = TRUE,
                        tem_cpf_cliente = TRUE,
                        tem_rg_cliente = FALSE,
                        tem_cnpj_cliente = TRUE,
                        tem_crm_cliente = FALSE,
                        tem_desconto_venda = TRUE,
                        tem_taxa_entrega = FALSE,
                        tem_mesa_venda = FALSE,
                        tem_garcom_venda = FALSE
                    WHERE id = %s
                """, [str(crm_vendas.id)])
        except Exception as e:
            # Se os campos não existirem mais no banco, ignora
            logger.warning(f"Campos antigos não encontrados no banco (pode ser esperado): {e}")
        
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

