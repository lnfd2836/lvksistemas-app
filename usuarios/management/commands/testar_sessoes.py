from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from usuarios.models import SessaoAtiva


class Command(BaseCommand):
    help = 'Testa o sistema de sessão única'

    def handle(self, *args, **options):
        """Testa o sistema de sessão única"""
        try:
            # Lista todas as sessões ativas
            sessoes_ativas = SessaoAtiva.objects.filter(ativa=True)
            
            self.stdout.write(f'Sessões ativas encontradas: {sessoes_ativas.count()}')
            
            for sessao in sessoes_ativas:
                tipo_sessao = "Super Admin (Múltiplas)" if sessao.is_super_admin else "Admin Loja (Única)"
                self.stdout.write(
                    f'  - {sessao.user.username} ({sessao.ip_address}) - '
                    f'Tipo: {tipo_sessao} - '
                    f'Login: {sessao.data_login} - '
                    f'Última atividade: {sessao.ultima_atividade}'
                )
            
            # Testa a limpeza de sessões expiradas
            self.stdout.write('\nTestando limpeza de sessões expiradas...')
            SessaoAtiva.limpar_sessoes_expiradas()
            
            sessoes_apos_limpeza = SessaoAtiva.objects.filter(ativa=True).count()
            self.stdout.write(f'Sessões ativas após limpeza: {sessoes_apos_limpeza}')
            
            self.stdout.write(
                self.style.SUCCESS('Teste de sessões concluído com sucesso!')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Erro ao testar sessões: {str(e)}')
            )
