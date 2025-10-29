"""
Comando para sincronizar lojas do banco local para o Heroku
Exporta e importa todas as lojas com seus dados relacionados
"""
import json
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.db import transaction
from django.contrib.auth.models import User
from lojas.models import Loja
from modulos.models import TipoLoja
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Sincroniza lojas do banco local para o Heroku via dumpdata/loaddata'

    def add_arguments(self, parser):
        parser.add_argument(
            '--app',
            type=str,
            default='lvk',
            help='Nome do app Heroku (padrão: lvk)'
        )
        parser.add_argument(
            '--export-only',
            action='store_true',
            help='Apenas exporta os dados sem enviar para Heroku'
        )
        parser.add_argument(
            '--import-only',
            action='store_true',
            help='Apenas importa dados de um arquivo JSON existente'
        )
        parser.add_argument(
            '--arquivo',
            type=str,
            help='Arquivo JSON para importar (usado com --import-only)'
        )
        parser.add_argument(
            '--limpar',
            action='store_true',
            help='Limpa as lojas existentes no Heroku antes de importar'
        )

    def handle(self, *args, **options):
        app_name = options['app']
        
        if options['import_only']:
            if not options.get('arquivo'):
                self.stdout.write(
                    self.style.ERROR('Especifique --arquivo ao usar --import-only')
                )
                return
            self.importar_lojas_heroku(app_name, options['arquivo'], options.get('limpar', False))
        elif options['export_only']:
            arquivo = self.exportar_lojas_local()
            self.stdout.write(
                self.style.SUCCESS(f'Lojas exportadas para {arquivo}')
            )
        else:
            # Exporta localmente, depois importa no Heroku
            arquivo = self.exportar_lojas_local()
            self.stdout.write(
                self.style.SUCCESS(f'Lojas exportadas para {arquivo}')
            )
            self.importar_lojas_heroku(app_name, arquivo, options.get('limpar', False))

    def exportar_lojas_local(self):
        """Exporta lojas do banco local para arquivo JSON"""
        from django.core import serializers
        from io import StringIO
        import os
        from datetime import datetime
        
        arquivo = f'lojas_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        
        self.stdout.write(self.style.WARNING('Exportando lojas do banco local...'))
        
        # Exportar lojas
        lojas = Loja.objects.all()
        
        # Criar arquivo JSON com os dados
        data = []
        
        for loja in lojas:
            self.stdout.write(f'Exportando loja: {loja.nome}')
            
            loja_data = {
                'model': 'lojas.loja',
                'pk': str(loja.id),
                'fields': {
                    'nome': loja.nome,
                    'cnpj': loja.cnpj,
                    'email': loja.email,
                    'telefone': loja.telefone,
                    'endereco': loja.endereco,
                    'cidade': loja.cidade,
                    'estado': loja.estado,
                    'cep': loja.cep,
                    'db_name': loja.db_name,
                    'db_host': loja.db_host,
                    'db_port': loja.db_port,
                    'status': loja.status,
                    'data_criacao': loja.data_criacao.isoformat(),
                    'data_atualizacao': loja.data_atualizacao.isoformat(),
                    'senha_provisoria': loja.senha_provisoria,
                    'senha_provisoria_expirada': loja.senha_provisoria_expirada,
                    'admin_user': loja.admin_user.id if loja.admin_user else None,
                    'tipo_loja': str(loja.tipo_loja.id) if loja.tipo_loja else None,
                    'plano_comercial': str(loja.plano_comercial.id) if loja.plano_comercial else None,
                }
            }
            data.append(loja_data)
        
        # Exportar usuários admin das lojas
        for loja in lojas:
            if loja.admin_user:
                try:
                    user = loja.admin_user
                    user_data = {
                        'model': 'auth.user',
                        'pk': user.id,
                        'fields': {
                            'username': user.username,
                            'first_name': user.first_name,
                            'last_name': user.last_name,
                            'email': user.email,
                            'is_staff': user.is_staff,
                            'is_active': user.is_active,
                            'is_superuser': user.is_superuser,
                            'date_joined': user.date_joined.isoformat(),
                            'last_login': user.last_login.isoformat() if user.last_login else None,
                        }
                    }
                    # Adicionar apenas se não existir (evitar duplicatas)
                    if not any(d.get('pk') == user.id and d.get('model') == 'auth.user' for d in data):
                        data.append(user_data)
                except Exception as e:
                    self.stdout.write(
                        self.style.WARNING(f'Erro ao exportar usuário admin da loja {loja.nome}: {e}')
                    )
        
        # Salvar em arquivo JSON
        with open(arquivo, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        self.stdout.write(
            self.style.SUCCESS(f'Total de {len([d for d in data if d["model"] == "lojas.loja"])} lojas exportadas')
        )
        
        return arquivo

    def importar_lojas_heroku(self, app_name, arquivo, limpar=False):
        """Importa lojas para o Heroku"""
        import subprocess
        import os
        
        if not os.path.exists(arquivo):
            self.stdout.write(
                self.style.ERROR(f'Arquivo {arquivo} não encontrado')
            )
            return
        
        self.stdout.write(self.style.WARNING(f'Importando lojas para Heroku app: {app_name}'))
        
        # Limpar lojas existentes se solicitado
        if limpar:
            self.stdout.write(self.style.WARNING('Limpando lojas existentes no Heroku...'))
            try:
                # Criar comando para limpar lojas (exceto superuser)
                cmd = f"python -c \"import os, django; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lojad.settings'); django.setup(); from lojas.models import Loja; from django.contrib.auth.models import User; Loja.objects.all().delete(); print('Lojas removidas')\""
                result = subprocess.run(
                    ['heroku', 'run', f'--app', app_name, cmd],
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    self.stdout.write(self.style.SUCCESS('Lojas limpas no Heroku'))
                else:
                    self.stdout.write(self.style.WARNING(f'Aviso ao limpar: {result.stderr}'))
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'Erro ao limpar lojas (continuando): {e}'))
        
        # Enviar arquivo para o Heroku
        self.stdout.write(self.style.WARNING('Enviando arquivo para Heroku...'))
        
        # Copiar arquivo para um diretório temporário no Heroku
        try:
            # Upload do arquivo via heroku run
            with open(arquivo, 'rb') as f:
                # Ler conteúdo do arquivo
                arquivo_content = f.read().decode('utf-8')
                
                # Criar comando para escrever arquivo no Heroku
                cmd = f"python -c \"import sys; f=open('/tmp/lojas_backup.json', 'w'); f.write('''{arquivo_content.replace(chr(39), chr(92)+chr(39))}'''); f.close()\""
                
                self.stdout.write(self.style.WARNING('Escrevendo arquivo no Heroku...'))
                result = subprocess.run(
                    ['heroku', 'run', '--app', app_name, '--no-tty', cmd],
                    capture_output=True,
                    text=True,
                    timeout=300
                )
                
                if result.returncode != 0:
                    self.stdout.write(self.style.ERROR(f'Erro ao enviar arquivo: {result.stderr}'))
                    return
                
                self.stdout.write(self.style.SUCCESS('Arquivo enviado para Heroku'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Erro ao enviar arquivo: {e}'))
            # Fallback: usar loaddata diretamente
            self.stdout.write(self.style.WARNING('Tentando método alternativo...'))
            self._importar_direto_heroku(app_name, arquivo)
            return
        
        # Executar loaddata no Heroku
        self.stdout.write(self.style.WARNING('Executando loaddata no Heroku...'))
        
        cmd = f"python manage.py loaddata /tmp/lojas_backup.json"
        result = subprocess.run(
            ['heroku', 'run', '--app', app_name, '--no-tty', cmd],
            capture_output=True,
            text=True,
            timeout=600
        )
        
        if result.returncode == 0:
            self.stdout.write(self.style.SUCCESS('Lojas importadas com sucesso no Heroku!'))
            self.stdout.write(result.stdout)
        else:
            self.stdout.write(self.style.ERROR(f'Erro ao importar lojas: {result.stderr}'))
            self.stdout.write(self.style.WARNING('Tentando método alternativo...'))
            self._importar_direto_heroku(app_name, arquivo)

    def _importar_direto_heroku(self, app_name, arquivo):
        """Método alternativo: cria um script temporário e executa no Heroku"""
        import subprocess
        import tempfile
        import os
        
        self.stdout.write(self.style.WARNING('Usando método de importação direto...'))
        
        # Ler arquivo JSON
        with open(arquivo, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Criar script Python para importar
        script_content = f'''import os, django, json
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lojad.settings')
django.setup()

from lojas.models import Loja
from django.contrib.auth.models import User
from modulos.models import TipoLoja
from planos.models import PlanoComercial

data = {repr(data)}

for item in data:
    if item['model'] == 'auth.user':
        try:
            user, created = User.objects.get_or_create(
                id=item['pk'],
                defaults={{
                    'username': item['fields']['username'],
                    'email': item['fields']['email'],
                    'first_name': item['fields'].get('first_name', ''),
                    'last_name': item['fields'].get('last_name', ''),
                    'is_staff': item['fields'].get('is_staff', False),
                    'is_active': item['fields'].get('is_active', True),
                    'is_superuser': item['fields'].get('is_superuser', False),
                }}
            )
            if created:
                user.set_password('senha_temporaria_123')
                user.save()
                print(f'Usuário {{user.username}} criado')
        except Exception as e:
            print(f'Erro ao criar usuário: {{e}}')
    elif item['model'] == 'lojas.loja':
        try:
            fields = item['fields']
            admin_user = None
            if fields.get('admin_user'):
                try:
                    admin_user = User.objects.get(id=fields['admin_user'])
                except User.DoesNotExist:
                    print(f"Usuário admin {{fields['admin_user']}} não encontrado")

            tipo_loja = None
            if fields.get('tipo_loja'):
                try:
                    tipo_loja = TipoLoja.objects.get(id=fields['tipo_loja'])
                except TipoLoja.DoesNotExist:
                    print(f"TipoLoja {{fields['tipo_loja']}} não encontrado")

            plano = None
            if fields.get('plano_comercial'):
                try:
                    plano = PlanoComercial.objects.get(id=fields['plano_comercial'])
                except PlanoComercial.DoesNotExist:
                    print(f"Plano {{fields['plano_comercial']}} não encontrado")

            loja, created = Loja.objects.get_or_create(
                id=item['pk'],
                defaults={{
                    'nome': fields['nome'],
                    'cnpj': fields['cnpj'],
                    'email': fields['email'],
                    'telefone': fields.get('telefone', ''),
                    'endereco': fields.get('endereco', ''),
                    'cidade': fields.get('cidade', ''),
                    'estado': fields.get('estado', ''),
                    'cep': fields.get('cep', ''),
                    'db_name': fields.get('db_name', ''),
                    'db_host': fields.get('db_host', 'localhost'),
                    'db_port': fields.get('db_port', 5432),
                    'status': fields.get('status', 'ativa'),
                    'senha_provisoria': fields.get('senha_provisoria', ''),
                    'senha_provisoria_expirada': fields.get('senha_provisoria_expirada', False),
                    'admin_user': admin_user,
                    'tipo_loja': tipo_loja,
                    'plano_comercial': plano,
                }}
            )
            if created:
                print(f'Loja {{loja.nome}} criada')
            else:
                print(f'Loja {{loja.nome}} já existe')
        except Exception as e:
            print(f'Erro ao criar loja: {{e}}')
            import traceback
            traceback.print_exc()
'''
        
        # Salvar script em arquivo temporário
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(script_content)
            script_file = f.name
        
        try:
            # Enviar script para Heroku e executar
            with open(script_file, 'rb') as f:
                # Ler conteúdo
                script_content_bytes = f.read()
                
                # Criar comando para escrever e executar no Heroku
                # Usar base64 para enviar o script
                import base64
                script_b64 = base64.b64encode(script_content_bytes).decode('utf-8')
                
                cmd = f"python -c \"import base64; script = base64.b64decode('{script_b64}').decode('utf-8'); exec(script)\""
                
                result = subprocess.run(
                    ['heroku', 'run', '--app', app_name, '--no-tty', cmd],
                    capture_output=True,
                    text=True,
                    timeout=600
                )
                
                if result.returncode == 0:
                    self.stdout.write(self.style.SUCCESS('Lojas importadas com sucesso!'))
                    if result.stdout:
                        self.stdout.write(result.stdout)
                else:
                    self.stdout.write(self.style.ERROR(f'Erro ao importar: {result.stderr}'))
                    if result.stdout:
                        self.stdout.write(result.stdout)
        finally:
            # Limpar arquivo temporário
            if os.path.exists(script_file):
                os.unlink(script_file)

