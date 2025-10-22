"""
Comando para listar lojas e controles financeiros
"""
from django.core.management.base import BaseCommand
from controle_financeiro.models import ControleFinanceiro
from lojas.models import Loja


class Command(BaseCommand):
    help = 'Lista lojas e controles financeiros disponíveis'

    def handle(self, *args, **options):
        try:
            self.stdout.write("📋 Listando lojas e controles financeiros...")
            
            # Listar lojas
            lojas = Loja.objects.all()
            self.stdout.write(f"\n🏪 Total de lojas: {lojas.count()}")
            
            for loja in lojas:
                self.stdout.write(f"  ID: {loja.id} | Nome: {loja.nome} | CNPJ: {loja.cnpj}")
                
                # Verificar controle financeiro
                try:
                    controle = ControleFinanceiro.objects.get(loja=loja)
                    self.stdout.write(f"    ✅ Controle: Status {controle.status} | Valor: R$ {controle.valor_mensal}")
                except ControleFinanceiro.DoesNotExist:
                    self.stdout.write(f"    ❌ Sem controle financeiro")
            
            # Listar controles sem loja (se houver)
            controles_sem_loja = ControleFinanceiro.objects.filter(loja__isnull=True)
            if controles_sem_loja.exists():
                self.stdout.write(f"\n⚠️ Controles sem loja: {controles_sem_loja.count()}")
            
            self.stdout.write("\n✅ Listagem concluída")
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Erro: {str(e)}"))
            import traceback
            self.stdout.write(traceback.format_exc())