"""
Utilitários para gerenciamento de bancos de dados das lojas
"""
import os
import subprocess
from django.conf import settings
from django.db import connection
from django.core.management import execute_from_command_line
from django.utils import timezone


def criar_banco_loja(loja):
    """
    Cria um banco de dados individual para uma loja
    """
    try:
        # Conecta ao PostgreSQL e cria o banco
        with connection.cursor() as cursor:
            cursor.execute(f"CREATE DATABASE {loja.db_name};")
        
        # Configura o banco de dados da loja
        config_banco = {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': loja.db_name,
            'USER': settings.DATABASES['default']['USER'],
            'PASSWORD': settings.DATABASES['default']['PASSWORD'],
            'HOST': settings.DATABASES['default']['HOST'],
            'PORT': settings.DATABASES['default']['PORT'],
        }
        
        # Salva a configuração (você pode implementar um sistema de configuração dinâmica)
        # Por enquanto, apenas retorna True
        return True
        
    except Exception as e:
        print(f"Erro ao criar banco de dados: {e}")
        return False


def executar_migracoes_loja(loja):
    """
    Executa as migrações no banco de dados da loja
    """
    try:
        # Aqui você implementaria a lógica para executar migrações
        # no banco específico da loja
        return True
    except Exception as e:
        print(f"Erro ao executar migrações: {e}")
        return False


def criar_backup_loja(loja):
    """
    Cria backup do banco de dados da loja
    """
    try:
        # Comando pg_dump para criar backup
        cmd = [
            'pg_dump',
            '-h', settings.DATABASES['default']['HOST'],
            '-U', settings.DATABASES['default']['USER'],
            '-d', loja.db_name,
            '-f', f'/tmp/backup_{loja.db_name}_{timezone.now().strftime("%Y%m%d_%H%M%S")}.sql'
        ]
        
        # Executa o comando
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            return True, result.stdout
        else:
            return False, result.stderr
            
    except Exception as e:
        return False, str(e)


def restaurar_backup_loja(loja, arquivo_backup):
    """
    Restaura backup do banco de dados da loja
    """
    try:
        # Comando psql para restaurar backup
        cmd = [
            'psql',
            '-h', settings.DATABASES['default']['HOST'],
            '-U', settings.DATABASES['default']['USER'],
            '-d', loja.db_name,
            '-f', arquivo_backup
        ]
        
        # Executa o comando
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            return True, result.stdout
        else:
            return False, result.stderr
            
    except Exception as e:
        return False, str(e)


def otimizar_banco_loja(loja):
    """
    Otimiza o banco de dados da loja
    """
    try:
        with connection.cursor() as cursor:
            # Executa VACUUM ANALYZE para otimizar
            cursor.execute(f"VACUUM ANALYZE;")
            return True
    except Exception as e:
        print(f"Erro ao otimizar banco: {e}")
        return False
