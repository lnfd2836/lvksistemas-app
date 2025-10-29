"""
Comando para excluir uma loja específica pelo nome
"""
from django.core.management.base import BaseCommand
from django.db import transaction, DatabaseError, ProgrammingError
from lojas.models import Loja, Cliente, Produto, Venda, Funcionario
from lojas.models import ItemVenda
from dashboard.models import Notificacao
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Exclui uma loja específica pelo nome'

    def add_arguments(self, parser):
        parser.add_argument('nome_loja', type=str, help='Nome da loja a ser excluída')
        parser.add_argument('--confirmar', action='store_true', help='Confirma a exclusão')

    def handle(self, *args, **options):
        nome_loja = options['nome_loja']
        confirmar = options['confirmar']

        try:
            # Buscar a loja
            loja = Loja.objects.filter(nome__icontains=nome_loja).first()
            
            if not loja:
                self.stdout.write(
                    self.style.ERROR(f'Loja "{nome_loja}" não encontrada!')
                )
                # Listar lojas similares
                lojas_similares = Loja.objects.filter(nome__icontains=nome_loja.split()[0])[:10]
                if lojas_similares:
                    self.stdout.write('\nLojas similares encontradas:')
                    for l in lojas_similares:
                        self.stdout.write(f'  - {l.nome} (ID: {l.id})')
                return

            # Mostrar informações da loja
            self.stdout.write('\n' + '='*60)
            self.stdout.write(f'LOJA ENCONTRADA:')
            self.stdout.write(f'  Nome: {loja.nome}')
            self.stdout.write(f'  CNPJ: {loja.cnpj}')
            self.stdout.write(f'  Cidade: {loja.cidade}/{loja.estado}')
            self.stdout.write(f'  Tipo: {loja.tipo_loja.nome if loja.tipo_loja else "N/A"}')
            self.stdout.write(f'  ID: {loja.id}')
            self.stdout.write('='*60)

            # Coletar estatísticas
            stats = {
                'clientes': Cliente.objects.filter(loja=loja).count(),
                'produtos': Produto.objects.filter(loja=loja).count(),
                'vendas': Venda.objects.filter(loja=loja).count(),
                'funcionarios': Funcionario.objects.filter(loja=loja).count(),
                'notificacoes': Notificacao.objects.filter(loja=loja).count(),
            }

            self.stdout.write('\nDADOS A SEREM EXCLUÍDOS:')
            for key, value in stats.items():
                self.stdout.write(f'  {key.capitalize()}: {value}')

            if not confirmar:
                self.stdout.write(
                    self.style.WARNING(
                        '\n⚠️  Use --confirmar para executar a exclusão'
                    )
                )
                return

            # Confirmar exclusão
            self.stdout.write(
                self.style.WARNING('\n⚠️  EXCLUINDO LOJA E TODOS OS DADOS RELACIONADOS...')
            )

            loja_id = str(loja.id)
            nome_loja_final = loja.nome

            try:
                # Tenta excluir usando QuerySet diretamente (mais seguro quando tabela não existe)
                # Como já verificamos que não há dados relacionados, podemos fazer exclusão simples
                # Excluir dados relacionados primeiro
                Notificacao.objects.filter(loja=loja).delete()
                ItemVenda.objects.filter(venda__loja=loja).delete()
                Venda.objects.filter(loja=loja).delete()
                Funcionario.objects.filter(loja=loja).delete()
                Produto.objects.filter(loja=loja).delete()
                Cliente.objects.filter(loja=loja).delete()
                
                # Configurações específicas da loja
                try:
                    from modulos.models import ConfiguracaoLoja
                    ConfiguracaoLoja.objects.filter(loja=loja).delete()
                except (DatabaseError, ProgrammingError) as e:
                    error_msg = str(e)
                    if 'does not exist' in error_msg or 'relation' in error_msg.lower():
                        self.stdout.write(
                            self.style.WARNING('  Tabela modulos_configuracaoloja não existe. Pulando...')
                        )
                    else:
                        logger.warning(f"Erro ao excluir configurações: {e}")
                except Exception as e:
                    logger.warning(f"Erro ao excluir configurações: {e}")
                
                # Excluir a loja usando SQL direto (evita problemas com CASCADE quando tabela não existe)
                from django.db import connection
                with connection.cursor() as cursor:
                    cursor.execute("DELETE FROM lojas_loja WHERE id = %s", [loja_id])
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'\n✅ Loja "{nome_loja_final}" excluída com sucesso!'
                    )
                )
                self.stdout.write(f'  - {stats["clientes"]} clientes removidos')
                self.stdout.write(f'  - {stats["produtos"]} produtos removidos')
                self.stdout.write(f'  - {stats["vendas"]} vendas removidas')
                self.stdout.write(f'  - {stats["funcionarios"]} funcionários removidos')
                self.stdout.write(f'  - {stats["notificacoes"]} notificações removidas')
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'\n❌ Erro ao excluir loja: {e}')
                )
                logger.error(f"Erro ao excluir loja {nome_loja_final}: {e}", exc_info=True)
        
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'\n❌ Erro geral ao processar comando: {e}')
            )
            logger.error(f"Erro geral: {e}", exc_info=True)

