#!/usr/bin/env python3
"""
Script para integrar middlewares exclusivos ao sistema
"""

import os
import sys
import django

# Configurar Django
sys.path.append('/home/luiz/Documentos/lvksistemas-app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lojad.settings')
django.setup()

def atualizar_settings_middlewares():
    """Atualiza settings.py com os novos middlewares"""
    
    print("🔧 Atualizando settings.py com middlewares exclusivos...")
    
    try:
        settings_path = 'lojad/settings.py'
        
        with open(settings_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Encontrar seção MIDDLEWARE
        lines = content.split('\n')
        new_lines = []
        in_middleware_section = False
        middleware_updated = False
        
        for line in lines:
            if 'MIDDLEWARE = [' in line:
                in_middleware_section = True
                new_lines.append(line)
                # Adicionar comentário
                new_lines.append('    # === MIDDLEWARES EXCLUSIVOS POR GRUPO ===')
                new_lines.append('    # Grupo 1: Super Admin Exclusivo')
                new_lines.append("    'dashboard.middleware.super_admin_exclusivo.SuperAdminExclusivoMiddleware',")
                new_lines.append('    # Grupo 2: Asaas Exclusivo')
                new_lines.append("    'controle_financeiro.middleware.asaas_exclusivo.AsaasExclusivoMiddleware',")
                new_lines.append('    # === MIDDLEWARES ORIGINAIS ===')
                middleware_updated = True
            elif in_middleware_section and line.strip() == ']':
                # Adicionar comentário de fim
                new_lines.append('    # === MIDDLEWARES DINÂMICOS POR LOJA ===')
                new_lines.append('    # Middlewares de loja são adicionados dinamicamente')
                new_lines.append(line)
                in_middleware_section = False
            else:
                new_lines.append(line)
        
        if middleware_updated:
            # Escrever arquivo atualizado
            with open(settings_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(new_lines))
            
            print("✅ Settings.py atualizado com middlewares exclusivos!")
            return True
        else:
            print("❌ Não foi possível encontrar seção MIDDLEWARE")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao atualizar settings: {e}")
        return False


def gerar_middlewares_lojas_existentes():
    """Gera middlewares para todas as lojas existentes"""
    
    print("🏭 Gerando middlewares para lojas existentes...")
    
    try:
        from lojas.models import Loja
        from lojas.middleware.gerador_middleware_loja import MiddlewareLojaGenerator
        
        generator = MiddlewareLojaGenerator()
        lojas = Loja.objects.filter(status='ativa')
        
        success_count = 0
        middlewares_criados = []
        
        for loja in lojas:
            print(f"  🔧 Gerando middleware para: {loja.nome}")
            
            resultado = generator.gerar_middleware_loja(loja)
            
            if resultado['success']:
                success_count += 1
                middlewares_criados.append({
                    'loja': loja.nome,
                    'path': resultado['middleware_path'],
                    'class': resultado['middleware_class']
                })
                print(f"    ✅ {resultado['middleware_class']} criado!")
            else:
                print(f"    ❌ Erro: {resultado['error']}")
        
        print(f"\n📊 Resultado: {success_count}/{len(lojas)} middlewares criados")
        
        # Salvar lista de middlewares criados
        if middlewares_criados:
            lista_path = 'lojas/middleware/middlewares_criados.py'
            lista_content = f'''"""
Lista de middlewares criados automaticamente para lojas
Gerado em: {__import__('datetime').datetime.now()}
"""

MIDDLEWARES_LOJAS = {middlewares_criados}

def get_middleware_classes():
    """Retorna lista de classes de middleware para adicionar ao settings"""
    classes = []
    for mw in MIDDLEWARES_LOJAS:
        module_path = mw['path'].replace('/', '.').replace('.py', '')
        class_name = mw['class']
        classes.append(f"{{module_path}}.{{class_name}}")
    return classes
'''
            
            with open(lista_path, 'w', encoding='utf-8') as f:
                f.write(lista_content)
            
            print(f"✅ Lista de middlewares salva em: {lista_path}")
        
        return success_count > 0
        
    except Exception as e:
        print(f"❌ Erro ao gerar middlewares das lojas: {e}")
        return False


def criar_signal_auto_middleware():
    """Cria signal para gerar middleware automaticamente quando loja é criada"""
    
    signal_content = '''"""
Signal para criar middleware automaticamente quando loja é criada
"""
import logging
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from lojas.models import Loja
from lojas.middleware.gerador_middleware_loja import MiddlewareLojaGenerator

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Loja)
def criar_middleware_loja(sender, instance, created, **kwargs):
    """
    Cria middleware exclusivo automaticamente quando loja é criada
    """
    if created:
        try:
            generator = MiddlewareLojaGenerator()
            resultado = generator.gerar_middleware_loja(instance)
            
            if resultado['success']:
                logger.info(f"Middleware criado automaticamente para loja: {instance.nome}")
                logger.info(f"Classe: {resultado['middleware_class']}")
                logger.info(f"Arquivo: {resultado['middleware_path']}")
                
                # Aqui você poderia adicionar lógica para:
                # 1. Atualizar settings.py dinamicamente
                # 2. Reiniciar servidor (em desenvolvimento)
                # 3. Notificar administradores
                
            else:
                logger.error(f"Falha ao criar middleware para loja {instance.nome}: {resultado['error']}")
                
        except Exception as e:
            logger.error(f"Erro no signal de criação de middleware: {str(e)}")


@receiver(post_delete, sender=Loja)
def remover_middleware_loja(sender, instance, **kwargs):
    """
    Remove middleware quando loja é deletada
    """
    try:
        generator = MiddlewareLojaGenerator()
        if generator.remover_middleware_loja(instance):
            logger.info(f"Middleware removido para loja deletada: {instance.nome}")
        
    except Exception as e:
        logger.error(f"Erro ao remover middleware da loja {instance.nome}: {str(e)}")
'''
    
    signal_path = 'lojas/signals_middleware.py'
    
    try:
        with open(signal_path, 'w', encoding='utf-8') as f:
            f.write(signal_content)
        
        print("✅ Signal de auto-criação de middleware criado!")
        
        # Atualizar apps.py para carregar signals
        apps_path = 'lojas/apps.py'
        
        try:
            with open(apps_path, 'r', encoding='utf-8') as f:
                apps_content = f.read()
            
            if 'signals_middleware' not in apps_content:
                # Adicionar import do signal
                apps_content = apps_content.replace(
                    'class LojasConfig(AppConfig):',
                    '''class LojasConfig(AppConfig):
    
    def ready(self):
        """Carrega signals quando app está pronto"""
        try:
            import lojas.signals_middleware
        except ImportError:
            pass'''
                )
                
                with open(apps_path, 'w', encoding='utf-8') as f:
                    f.write(apps_content)
                
                print("✅ Apps.py atualizado para carregar signals!")
        
        except Exception as e:
            print(f"⚠️  Aviso: Não foi possível atualizar apps.py: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao criar signal: {e}")
        return False


def criar_comando_gerenciamento():
    """Cria comando Django para gerenciar middlewares"""
    
    comando_content = '''"""
Comando Django para gerenciar middlewares de lojas
"""
from django.core.management.base import BaseCommand
from django.core.management import CommandError
from lojas.models import Loja
from lojas.middleware.gerador_middleware_loja import MiddlewareLojaGenerator


class Command(BaseCommand):
    help = 'Gerencia middlewares exclusivos de lojas'
    
    def add_arguments(self, parser):
        parser.add_argument(
            'action',
            choices=['criar', 'remover', 'listar', 'recriar'],
            help='Ação a ser executada'
        )
        parser.add_argument(
            '--loja-id',
            type=str,
            help='ID da loja específica'
        )
        parser.add_argument(
            '--todas',
            action='store_true',
            help='Aplicar ação a todas as lojas'
        )
    
    def handle(self, *args, **options):
        action = options['action']
        loja_id = options.get('loja_id')
        todas = options.get('todas', False)
        
        generator = MiddlewareLojaGenerator()
        
        if action == 'criar':
            self._criar_middlewares(generator, loja_id, todas)
        elif action == 'remover':
            self._remover_middlewares(generator, loja_id, todas)
        elif action == 'listar':
            self._listar_middlewares()
        elif action == 'recriar':
            self._recriar_middlewares(generator, loja_id, todas)
    
    def _criar_middlewares(self, generator, loja_id, todas):
        """Cria middlewares"""
        if todas:
            lojas = Loja.objects.filter(status='ativa')
            self.stdout.write(f"Criando middlewares para {len(lojas)} lojas...")
            
            for loja in lojas:
                resultado = generator.gerar_middleware_loja(loja)
                if resultado['success']:
                    self.stdout.write(
                        self.style.SUCCESS(f"✅ {loja.nome}: {resultado['middleware_class']}")
                    )
                else:
                    self.stdout.write(
                        self.style.ERROR(f"❌ {loja.nome}: {resultado['error']}")
                    )
        
        elif loja_id:
            try:
                loja = Loja.objects.get(id=loja_id)
                resultado = generator.gerar_middleware_loja(loja)
                
                if resultado['success']:
                    self.stdout.write(
                        self.style.SUCCESS(f"✅ Middleware criado: {resultado['middleware_class']}")
                    )
                else:
                    self.stdout.write(
                        self.style.ERROR(f"❌ Erro: {resultado['error']}")
                    )
            except Loja.DoesNotExist:
                raise CommandError(f"Loja com ID {loja_id} não encontrada")
        
        else:
            raise CommandError("Especifique --loja-id ou --todas")
    
    def _remover_middlewares(self, generator, loja_id, todas):
        """Remove middlewares"""
        if todas:
            lojas = Loja.objects.all()
            self.stdout.write(f"Removendo middlewares de {len(lojas)} lojas...")
            
            for loja in lojas:
                if generator.remover_middleware_loja(loja):
                    self.stdout.write(
                        self.style.SUCCESS(f"✅ {loja.nome}: Middleware removido")
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(f"⚠️  {loja.nome}: Middleware não encontrado")
                    )
        
        elif loja_id:
            try:
                loja = Loja.objects.get(id=loja_id)
                if generator.remover_middleware_loja(loja):
                    self.stdout.write(
                        self.style.SUCCESS("✅ Middleware removido")
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING("⚠️  Middleware não encontrado")
                    )
            except Loja.DoesNotExist:
                raise CommandError(f"Loja com ID {loja_id} não encontrada")
        
        else:
            raise CommandError("Especifique --loja-id ou --todas")
    
    def _listar_middlewares(self):
        """Lista middlewares existentes"""
        import os
        import glob
        
        middleware_files = glob.glob('lojas/middleware/loja_*_middleware.py')
        
        if middleware_files:
            self.stdout.write("📋 Middlewares de lojas encontrados:")
            for file in middleware_files:
                self.stdout.write(f"  • {os.path.basename(file)}")
        else:
            self.stdout.write("❌ Nenhum middleware de loja encontrado")
    
    def _recriar_middlewares(self, generator, loja_id, todas):
        """Recria middlewares (remove e cria novamente)"""
        self.stdout.write("🔄 Recriando middlewares...")
        self._remover_middlewares(generator, loja_id, todas)
        self._criar_middlewares(generator, loja_id, todas)
'''
    
    # Criar diretório de comandos se não existir
    comando_dir = 'lojas/management/commands'
    os.makedirs(comando_dir, exist_ok=True)
    
    # Criar __init__.py se não existir
    init_files = [
        'lojas/management/__init__.py',
        'lojas/management/commands/__init__.py'
    ]
    
    for init_file in init_files:
        if not os.path.exists(init_file):
            with open(init_file, 'w') as f:
                f.write('# Django management module\n')
    
    # Criar comando
    comando_path = f'{comando_dir}/gerenciar_middlewares.py'
    
    try:
        with open(comando_path, 'w', encoding='utf-8') as f:
            f.write(comando_content)
        
        print("✅ Comando de gerenciamento criado!")
        print("   Uso: python manage.py gerenciar_middlewares criar --todas")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao criar comando: {e}")
        return False


def main():
    """Função principal"""
    print("=" * 80)
    print("🔗 INTEGRAÇÃO DOS MIDDLEWARES EXCLUSIVOS")
    print("=" * 80)
    print()
    
    success_count = 0
    
    # 1. Atualizar settings.py
    print("1️⃣  Atualizando settings.py...")
    if atualizar_settings_middlewares():
        success_count += 1
    print()
    
    # 2. Gerar middlewares para lojas existentes
    print("2️⃣  Gerando middlewares para lojas existentes...")
    if gerar_middlewares_lojas_existentes():
        success_count += 1
    print()
    
    # 3. Criar signal de auto-criação
    print("3️⃣  Criando signal de auto-criação...")
    if criar_signal_auto_middleware():
        success_count += 1
    print()
    
    # 4. Criar comando de gerenciamento
    print("4️⃣  Criando comando de gerenciamento...")
    if criar_comando_gerenciamento():
        success_count += 1
    print()
    
    print("=" * 80)
    print("📋 RESUMO DA INTEGRAÇÃO")
    print("=" * 80)
    
    if success_count >= 4:
        print("✅ INTEGRAÇÃO CONCLUÍDA COM SUCESSO!")
        print()
        print("🎯 Funcionalidades ativas:")
        print("  1. ✅ Middlewares exclusivos configurados no settings")
        print("  2. ✅ Middlewares gerados para lojas existentes")
        print("  3. ✅ Auto-criação de middleware para novas lojas")
        print("  4. ✅ Comando de gerenciamento disponível")
        print()
        print("🔧 Comandos disponíveis:")
        print("  • python manage.py gerenciar_middlewares criar --todas")
        print("  • python manage.py gerenciar_middlewares listar")
        print("  • python manage.py gerenciar_middlewares remover --loja-id <ID>")
        
    else:
        print("⚠️  INTEGRAÇÃO PARCIAL - Alguns passos podem ter falhado")
    
    print()
    print("=" * 80)


if __name__ == '__main__':
    main()