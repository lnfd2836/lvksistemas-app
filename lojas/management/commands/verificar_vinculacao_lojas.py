"""
Comando para verificar e corrigir problemas de vinculação entre lojas e administradores
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from lojas.utils.admin_vinculacao import (
    listar_lojas_com_problemas,
    corrigir_vinculacao_automatica,
    verificar_isolamento_loja
)
from lojas.models import Loja


class Command(BaseCommand):
    help = 'Verifica e corrige problemas de vinculação entre lojas e administradores'

    def add_arguments(self, parser):
        parser.add_argument(
            '--corrigir',
            action='store_true',
            help='Corrige automaticamente os problemas encontrados'
        )
        parser.add_argument(
            '--loja-id',
            type=str,
            help='Verifica apenas uma loja específica (UUID)'
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Mostra informações detalhadas'
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS(
                f'\n🔍 Verificação de Vinculação de Lojas - {timezone.now().strftime("%d/%m/%Y %H:%M:%S")}\n'
            )
        )

        # Verificar loja específica
        if options['loja_id']:
            self.verificar_loja_especifica(options['loja_id'], options['corrigir'], options['verbose'])
            return

        # Verificar todas as lojas
        self.verificar_todas_lojas(options['corrigir'], options['verbose'])

    def verificar_loja_especifica(self, loja_id, corrigir, verbose):
        """Verifica uma loja específica"""
        try:
            loja = Loja.objects.get(id=loja_id)
            self.stdout.write(f"📋 Verificando loja: {loja.nome}")
            
            verificacao = verificar_isolamento_loja(loja)
            
            if verificacao['success']:
                self.stdout.write(
                    self.style.SUCCESS(f"✅ Loja {loja.nome} está corretamente configurada")
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f"⚠️  Problemas encontrados na loja {loja.nome}:")
                )
                for problema in verificacao['problemas']:
                    self.stdout.write(f"   - {problema}")
                
                if corrigir:
                    self.stdout.write("\n🔧 Aplicando correções...")
                    resultado = corrigir_vinculacao_automatica(loja_id)
                    
                    if resultado['success']:
                        self.stdout.write(
                            self.style.SUCCESS(f"✅ {resultado['message']}")
                        )
                    else:
                        self.stdout.write(
                            self.style.ERROR(f"❌ {resultado['message']}")
                        )
                    
                    if verbose and resultado['acoes_realizadas']:
                        self.stdout.write("\n📝 Ações realizadas:")
                        for acao in resultado['acoes_realizadas']:
                            self.stdout.write(f"   - {acao}")
                    
                    if resultado.get('problemas_restantes'):
                        self.stdout.write(
                            self.style.WARNING("\n⚠️  Problemas que ainda precisam de atenção:")
                        )
                        for problema in resultado['problemas_restantes']:
                            self.stdout.write(f"   - {problema}")
            
        except Loja.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f"❌ Loja com ID {loja_id} não encontrada")
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ Erro ao verificar loja: {str(e)}")
            )

    def verificar_todas_lojas(self, corrigir, verbose):
        """Verifica todas as lojas"""
        self.stdout.write("📋 Verificando todas as lojas...\n")
        
        # Listar lojas com problemas
        lojas_com_problemas = listar_lojas_com_problemas()
        
        if not lojas_com_problemas:
            self.stdout.write(
                self.style.SUCCESS("✅ Todas as lojas estão corretamente configuradas!")
            )
            return
        
        self.stdout.write(
            self.style.WARNING(f"⚠️  Encontradas {len(lojas_com_problemas)} lojas com problemas:\n")
        )
        
        for loja_info in lojas_com_problemas:
            self.stdout.write(f"🏪 Loja: {loja_info['loja_nome']}")
            self.stdout.write(f"   ID: {loja_info['loja_id']}")
            
            if verbose:
                self.stdout.write("   Problemas:")
                for problema in loja_info['problemas']:
                    self.stdout.write(f"   - {problema}")
            
            if corrigir:
                self.stdout.write("   🔧 Aplicando correções...")
                resultado = corrigir_vinculacao_automatica(loja_info['loja_id'])
                
                if resultado['success']:
                    self.stdout.write(
                        self.style.SUCCESS(f"   ✅ {resultado['message']}")
                    )
                else:
                    self.stdout.write(
                        self.style.ERROR(f"   ❌ {resultado['message']}")
                    )
            
            self.stdout.write("")  # Linha em branco
        
        if not corrigir:
            self.stdout.write(
                self.style.WARNING(
                    "💡 Para corrigir automaticamente, execute: "
                    "python manage.py verificar_vinculacao_lojas --corrigir"
                )
            )
        
        # Estatísticas finais
        total_lojas = Loja.objects.count()
        lojas_ok = total_lojas - len(lojas_com_problemas)
        
        self.stdout.write(f"\n📊 Resumo:")
        self.stdout.write(f"   Total de lojas: {total_lojas}")
        self.stdout.write(f"   Lojas OK: {lojas_ok}")
        self.stdout.write(f"   Lojas com problemas: {len(lojas_com_problemas)}")
        
        if corrigir:
            # Verificar novamente após correções
            lojas_com_problemas_pos = listar_lojas_com_problemas()
            if len(lojas_com_problemas_pos) < len(lojas_com_problemas):
                corrigidas = len(lojas_com_problemas) - len(lojas_com_problemas_pos)
                self.stdout.write(
                    self.style.SUCCESS(f"   ✅ Lojas corrigidas: {corrigidas}")
                )
            
            if lojas_com_problemas_pos:
                self.stdout.write(
                    self.style.WARNING(f"   ⚠️  Lojas ainda com problemas: {len(lojas_com_problemas_pos)}")
                )