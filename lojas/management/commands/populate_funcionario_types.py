from django.core.management.base import BaseCommand
from django.db import transaction
from modulos.models import TipoLoja
from lojas.models import TipoFuncionario


class Command(BaseCommand):
    help = 'Popula os tipos de funcionários padrão para cada tipo de loja'

    def handle(self, *args, **options):
        self.stdout.write('Iniciando população dos tipos de funcionários...')
        
        # Definição dos tipos de funcionários por tipo de loja
        tipos_funcionarios = {
            'lanchonete': [
                {
                    'nome': 'Atendente',
                    'descricao': 'Responsável pelo atendimento ao cliente e anotação de pedidos',
                    'permissoes': {
                        'dashboard': ['read'],
                        'vendas': ['read', 'write'],
                        'produtos': ['read'],
                        'clientes': ['read', 'write'],
                        'pedidos': ['read', 'write']
                    }
                },
                {
                    'nome': 'Cozinheiro',
                    'descricao': 'Responsável pelo preparo de alimentos e controle de ingredientes',
                    'permissoes': {
                        'dashboard': ['read'],
                        'produtos': ['read'],
                        'pedidos': ['read', 'write'],
                        'estoque': ['read', 'write']
                    }
                },
                {
                    'nome': 'Gerente',
                    'descricao': 'Responsável pela gestão geral da lanchonete',
                    'permissoes': {
                        'dashboard': ['read', 'write'],
                        'vendas': ['read', 'write', 'delete'],
                        'produtos': ['read', 'write', 'delete'],
                        'clientes': ['read', 'write', 'delete'],
                        'funcionarios': ['read', 'write'],
                        'relatorios': ['read', 'write'],
                        'configuracoes': ['read', 'write'],
                        'pedidos': ['read', 'write', 'delete'],
                        'estoque': ['read', 'write']
                    }
                },
                {
                    'nome': 'Caixa',
                    'descricao': 'Responsável pelas operações de pagamento e fechamento',
                    'permissoes': {
                        'dashboard': ['read'],
                        'vendas': ['read', 'write'],
                        'produtos': ['read'],
                        'clientes': ['read'],
                        'relatorios': ['read']
                    }
                }
            ],
            'conveniencia': [
                {
                    'nome': 'Atendente',
                    'descricao': 'Responsável pelo atendimento geral e vendas básicas',
                    'permissoes': {
                        'dashboard': ['read'],
                        'vendas': ['read', 'write'],
                        'produtos': ['read'],
                        'clientes': ['read', 'write']
                    }
                },
                {
                    'nome': 'Repositor',
                    'descricao': 'Responsável pela reposição e organização de produtos',
                    'permissoes': {
                        'dashboard': ['read'],
                        'produtos': ['read', 'write'],
                        'estoque': ['read', 'write']
                    }
                },
                {
                    'nome': 'Gerente',
                    'descricao': 'Responsável pela gestão completa da loja',
                    'permissoes': {
                        'dashboard': ['read', 'write'],
                        'vendas': ['read', 'write', 'delete'],
                        'produtos': ['read', 'write', 'delete'],
                        'clientes': ['read', 'write', 'delete'],
                        'funcionarios': ['read', 'write'],
                        'relatorios': ['read', 'write'],
                        'configuracoes': ['read', 'write'],
                        'estoque': ['read', 'write']
                    }
                },
                {
                    'nome': 'Caixa',
                    'descricao': 'Responsável pelas operações de venda e pagamento',
                    'permissoes': {
                        'dashboard': ['read'],
                        'vendas': ['read', 'write'],
                        'produtos': ['read'],
                        'clientes': ['read'],
                        'relatorios': ['read']
                    }
                },
                {
                    'nome': 'Segurança',
                    'descricao': 'Responsável pela segurança e monitoramento da loja',
                    'permissoes': {
                        'dashboard': ['read'],
                        'relatorios': ['read']
                    }
                }
            ],
            'roupas': [
                {
                    'nome': 'Vendedor',
                    'descricao': 'Responsável pelas vendas e atendimento ao cliente',
                    'permissoes': {
                        'dashboard': ['read'],
                        'vendas': ['read', 'write'],
                        'produtos': ['read'],
                        'clientes': ['read', 'write']
                    }
                },
                {
                    'nome': 'Provador',
                    'descricao': 'Responsável pela assistência em provadores e organização',
                    'permissoes': {
                        'dashboard': ['read'],
                        'produtos': ['read'],
                        'clientes': ['read']
                    }
                },
                {
                    'nome': 'Gerente',
                    'descricao': 'Responsável pela gestão completa da loja de roupas',
                    'permissoes': {
                        'dashboard': ['read', 'write'],
                        'vendas': ['read', 'write', 'delete'],
                        'produtos': ['read', 'write', 'delete'],
                        'clientes': ['read', 'write', 'delete'],
                        'funcionarios': ['read', 'write'],
                        'relatorios': ['read', 'write'],
                        'configuracoes': ['read', 'write'],
                        'estoque': ['read', 'write']
                    }
                },
                {
                    'nome': 'Caixa',
                    'descricao': 'Responsável pelas operações financeiras',
                    'permissoes': {
                        'dashboard': ['read'],
                        'vendas': ['read', 'write'],
                        'produtos': ['read'],
                        'clientes': ['read'],
                        'relatorios': ['read']
                    }
                },
                {
                    'nome': 'Visual Merchandising',
                    'descricao': 'Responsável pela organização visual e vitrines',
                    'permissoes': {
                        'dashboard': ['read'],
                        'produtos': ['read', 'write'],
                        'estoque': ['read']
                    }
                }
            ],
            'supermercado': [
                {
                    'nome': 'Operador de Caixa',
                    'descricao': 'Responsável pelas operações de checkout',
                    'permissoes': {
                        'dashboard': ['read'],
                        'vendas': ['read', 'write'],
                        'produtos': ['read'],
                        'clientes': ['read'],
                        'relatorios': ['read']
                    }
                },
                {
                    'nome': 'Repositor',
                    'descricao': 'Responsável pela reposição e organização de produtos',
                    'permissoes': {
                        'dashboard': ['read'],
                        'produtos': ['read', 'write'],
                        'estoque': ['read', 'write']
                    }
                },
                {
                    'nome': 'Açougueiro',
                    'descricao': 'Responsável pela seção de carnes e atendimento especializado',
                    'permissoes': {
                        'dashboard': ['read'],
                        'produtos': ['read', 'write'],
                        'vendas': ['read', 'write'],
                        'clientes': ['read'],
                        'estoque': ['read', 'write']
                    }
                },
                {
                    'nome': 'Padeiro',
                    'descricao': 'Responsável pela seção de panificação',
                    'permissoes': {
                        'dashboard': ['read'],
                        'produtos': ['read', 'write'],
                        'vendas': ['read', 'write'],
                        'estoque': ['read', 'write']
                    }
                },
                {
                    'nome': 'Gerente',
                    'descricao': 'Responsável pela gestão geral do supermercado',
                    'permissoes': {
                        'dashboard': ['read', 'write'],
                        'vendas': ['read', 'write', 'delete'],
                        'produtos': ['read', 'write', 'delete'],
                        'clientes': ['read', 'write', 'delete'],
                        'funcionarios': ['read', 'write'],
                        'relatorios': ['read', 'write'],
                        'configuracoes': ['read', 'write'],
                        'estoque': ['read', 'write']
                    }
                },
                {
                    'nome': 'Segurança',
                    'descricao': 'Responsável pelo monitoramento e prevenção de perdas',
                    'permissoes': {
                        'dashboard': ['read'],
                        'relatorios': ['read']
                    }
                }
            ],
            'tintas': [
                {
                    'nome': 'Vendedor Técnico',
                    'descricao': 'Responsável pela consultoria técnica e vendas especializadas',
                    'permissoes': {
                        'dashboard': ['read'],
                        'vendas': ['read', 'write'],
                        'produtos': ['read'],
                        'clientes': ['read', 'write']
                    }
                },
                {
                    'nome': 'Colorista',
                    'descricao': 'Responsável pela preparação de cores e mistura de tintas',
                    'permissoes': {
                        'dashboard': ['read'],
                        'produtos': ['read', 'write'],
                        'estoque': ['read', 'write']
                    }
                },
                {
                    'nome': 'Gerente',
                    'descricao': 'Responsável pela gestão completa e compras técnicas',
                    'permissoes': {
                        'dashboard': ['read', 'write'],
                        'vendas': ['read', 'write', 'delete'],
                        'produtos': ['read', 'write', 'delete'],
                        'clientes': ['read', 'write', 'delete'],
                        'funcionarios': ['read', 'write'],
                        'relatorios': ['read', 'write'],
                        'configuracoes': ['read', 'write'],
                        'estoque': ['read', 'write']
                    }
                },
                {
                    'nome': 'Caixa',
                    'descricao': 'Responsável pelas operações financeiras',
                    'permissoes': {
                        'dashboard': ['read'],
                        'vendas': ['read', 'write'],
                        'produtos': ['read'],
                        'clientes': ['read'],
                        'relatorios': ['read']
                    }
                },
                {
                    'nome': 'Estoquista',
                    'descricao': 'Responsável pelo controle de estoque especializado',
                    'permissoes': {
                        'dashboard': ['read'],
                        'produtos': ['read', 'write'],
                        'estoque': ['read', 'write']
                    }
                }
            ],
            'eletronicos': [
                {
                    'nome': 'Vendedor Técnico',
                    'descricao': 'Responsável pelas vendas especializadas e consultoria',
                    'permissoes': {
                        'dashboard': ['read'],
                        'vendas': ['read', 'write'],
                        'produtos': ['read'],
                        'clientes': ['read', 'write']
                    }
                },
                {
                    'nome': 'Técnico em Eletrônicos',
                    'descricao': 'Responsável pela assistência técnica e reparos',
                    'permissoes': {
                        'dashboard': ['read'],
                        'produtos': ['read', 'write'],
                        'clientes': ['read', 'write'],
                        'servicos': ['read', 'write']
                    }
                },
                {
                    'nome': 'Gerente',
                    'descricao': 'Responsável pela gestão completa e relacionamento com fornecedores',
                    'permissoes': {
                        'dashboard': ['read', 'write'],
                        'vendas': ['read', 'write', 'delete'],
                        'produtos': ['read', 'write', 'delete'],
                        'clientes': ['read', 'write', 'delete'],
                        'funcionarios': ['read', 'write'],
                        'relatorios': ['read', 'write'],
                        'configuracoes': ['read', 'write'],
                        'estoque': ['read', 'write'],
                        'servicos': ['read', 'write']
                    }
                },
                {
                    'nome': 'Caixa',
                    'descricao': 'Responsável pelas operações financeiras',
                    'permissoes': {
                        'dashboard': ['read'],
                        'vendas': ['read', 'write'],
                        'produtos': ['read'],
                        'clientes': ['read'],
                        'relatorios': ['read']
                    }
                },
                {
                    'nome': 'Estoquista',
                    'descricao': 'Responsável pelo controle de estoque e logística',
                    'permissoes': {
                        'dashboard': ['read'],
                        'produtos': ['read', 'write'],
                        'estoque': ['read', 'write']
                    }
                }
            ]
        }

        with transaction.atomic():
            created_count = 0
            
            for tipo_loja_nome, funcionarios in tipos_funcionarios.items():
                try:
                    tipo_loja = TipoLoja.objects.get(nome=tipo_loja_nome)
                    self.stdout.write(f'Processando tipo de loja: {tipo_loja.get_nome_display()}')
                    
                    for funcionario_data in funcionarios:
                        tipo_funcionario, created = TipoFuncionario.objects.get_or_create(
                            nome=funcionario_data['nome'],
                            tipo_loja=tipo_loja,
                            defaults={
                                'descricao': funcionario_data['descricao'],
                                'permissoes': funcionario_data['permissoes']
                            }
                        )
                        
                        if created:
                            created_count += 1
                            self.stdout.write(
                                f'  ✓ Criado: {funcionario_data["nome"]}'
                            )
                        else:
                            self.stdout.write(
                                f'  - Já existe: {funcionario_data["nome"]}'
                            )
                            
                except TipoLoja.DoesNotExist:
                    self.stdout.write(
                        self.style.WARNING(f'Tipo de loja "{tipo_loja_nome}" não encontrado')
                    )
                    continue

        self.stdout.write(
            self.style.SUCCESS(
                f'População concluída! {created_count} tipos de funcionários criados.'
            )
        )