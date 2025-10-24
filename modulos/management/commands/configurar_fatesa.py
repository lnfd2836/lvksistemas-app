from django.core.management.base import BaseCommand
from modulos.models import TipoLoja, ModuloLoja


class Command(BaseCommand):
    help = 'Configura o tipo de loja Controle de Qualidade para usar o sistema FATESA'

    def handle(self, *args, **options):
        try:
            # Buscar o tipo de loja controle_qualidade
            tipo_loja = TipoLoja.objects.get(nome='controle_qualidade')
            
            self.stdout.write(f"✅ Tipo de loja encontrado: {tipo_loja.get_nome_display()}")
            
            # Configurar as funcionalidades específicas para FATESA
            tipo_loja.descricao = "Sistema FATESA - Controle de Qualidade Educacional"
            tipo_loja.icone = "fas fa-graduation-cap"
            tipo_loja.cor_primaria = "#1f4e79"  # Azul FATESA
            tipo_loja.cor_secundaria = "#2980b9"  # Azul claro FATESA
            
            # Desabilitar funcionalidades padrão de loja (não aplicáveis ao FATESA)
            tipo_loja.tem_categoria_produto = False
            tipo_loja.tem_marca_produto = False
            tipo_loja.tem_tamanho_produto = False
            tipo_loja.tem_cor_produto = False
            tipo_loja.tem_peso_produto = False
            tipo_loja.tem_volume_produto = False
            tipo_loja.tem_data_validade = False
            tipo_loja.tem_codigo_barras = False
            tipo_loja.tem_estoque_minimo = False
            
            # Configurar campos de cliente específicos para FATESA (alunos)
            tipo_loja.tem_data_nascimento_cliente = True  # Data de nascimento do aluno
            tipo_loja.tem_sexo_cliente = True  # Sexo do aluno
            tipo_loja.tem_cpf_cliente = True  # CPF do aluno
            tipo_loja.tem_rg_cliente = True  # RG do aluno
            tipo_loja.tem_cnpj_cliente = False  # Não aplicável
            tipo_loja.tem_crm_cliente = False  # Não aplicável
            
            # Desabilitar funcionalidades de venda (não aplicáveis ao FATESA)
            tipo_loja.tem_desconto_venda = False
            tipo_loja.tem_taxa_entrega = False
            tipo_loja.tem_mesa_venda = False
            tipo_loja.tem_garcom_venda = False
            
            tipo_loja.save()
            
            self.stdout.write("✅ Configurações básicas do tipo de loja atualizadas")
            
            # Remover módulos padrão que não se aplicam ao FATESA
            modulos_para_remover = [
                'Gestão de Produtos',
                'Gestão de Vendas',
                'Gestão de Estoque',
                'Relatórios de Vendas',
                'Controle de Caixa'
            ]
            
            removidos = 0
            for nome_modulo in modulos_para_remover:
                count = ModuloLoja.objects.filter(
                    tipo_loja=tipo_loja,
                    nome__icontains=nome_modulo
                ).delete()[0]
                removidos += count
            
            if removidos > 0:
                self.stdout.write(f"✅ {removidos} módulos padrão removidos")
            
            # Criar módulos específicos do FATESA
            modulos_fatesa = [
                {
                    'nome': 'Sistema de Avaliação de Qualidade',
                    'descricao': 'Módulo principal para criação e gerenciamento de avaliações de qualidade educacional',
                    'icone': 'fas fa-clipboard-check',
                    'url': '/avaliacao-qualidade/',
                    'ativo': True,
                    'ordem': 1
                },
                {
                    'nome': 'Dashboard de Coordenação',
                    'descricao': 'Dashboard específico para coordenadores de curso',
                    'icone': 'fas fa-user-graduate',
                    'url': '/avaliacao-qualidade/dashboard/coordenacao/',
                    'ativo': True,
                    'ordem': 2
                },
                {
                    'nome': 'Dashboard de Professores',
                    'descricao': 'Dashboard específico para professores',
                    'icone': 'fas fa-chalkboard-teacher',
                    'url': '/avaliacao-qualidade/dashboard/professor/',
                    'ativo': True,
                    'ordem': 3
                },
                {
                    'nome': 'Dashboard da Diretoria',
                    'descricao': 'Dashboard executivo com visão geral das avaliações',
                    'icone': 'fas fa-chart-line',
                    'url': '/avaliacao-qualidade/dashboard/diretoria/',
                    'ativo': True,
                    'ordem': 4
                },
                {
                    'nome': 'Gerenciamento de Usuários',
                    'descricao': 'Gestão de usuários do sistema FATESA (coordenadores, professores, etc.)',
                    'icone': 'fas fa-users',
                    'url': '/avaliacao-qualidade/usuarios/',
                    'ativo': True,
                    'ordem': 5
                },
                {
                    'nome': 'Relatórios de Qualidade',
                    'descricao': 'Relatórios detalhados das avaliações em PDF e Excel',
                    'icone': 'fas fa-file-alt',
                    'url': '/avaliacao-qualidade/relatorios/',
                    'ativo': True,
                    'ordem': 6
                }
            ]
            
            criados = 0
            for modulo_data in modulos_fatesa:
                modulo, created = ModuloLoja.objects.get_or_create(
                    tipo_loja=tipo_loja,
                    nome=modulo_data['nome'],
                    defaults=modulo_data
                )
                if created:
                    criados += 1
                    self.stdout.write(f"✅ Módulo criado: {modulo.nome}")
                else:
                    # Atualizar módulo existente
                    for key, value in modulo_data.items():
                        setattr(modulo, key, value)
                    modulo.save()
                    self.stdout.write(f"🔄 Módulo atualizado: {modulo.nome}")
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'\n🎓 FATESA configurado com sucesso!\n'
                    f'- Tipo de loja atualizado\n'
                    f'- {removidos} módulos padrão removidos\n'
                    f'- {criados} módulos FATESA criados/atualizados\n'
                    f'- Todas as lojas do tipo "controle_qualidade" agora usam o sistema FATESA'
                )
            )
            
        except TipoLoja.DoesNotExist:
            self.stdout.write(
                self.style.ERROR('Tipo de loja "controle_qualidade" não encontrado!')
            )