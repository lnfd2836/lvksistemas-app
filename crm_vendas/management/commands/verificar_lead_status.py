"""
Comando para verificar e corrigir status de leads
"""
from django.core.management.base import BaseCommand
from crm_vendas.models import Lead, Orcamento, Proposta, HistoricoContato
from django.utils import timezone


class Command(BaseCommand):
    help = 'Verifica e corrige status de leads baseado em orçamentos e propostas'

    def add_arguments(self, parser):
        parser.add_argument(
            '--lead-id',
            type=str,
            help='ID específico do lead para verificar',
        )
        parser.add_argument(
            '--fix',
            action='store_true',
            help='Corrigir automaticamente os status incorretos',
        )

    def handle(self, *args, **options):
        lead_id = options.get('lead_id')
        fix = options.get('fix', False)

        if lead_id:
            # Verificar lead específico
            try:
                lead = Lead.objects.get(id=lead_id)
                self.verificar_lead(lead, fix)
            except Lead.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'Lead com ID {lead_id} não encontrado')
                )
        else:
            # Verificar todos os leads com status 'proposta_enviada'
            leads = Lead.objects.filter(status='proposta_enviada')
            self.stdout.write(f'Verificando {leads.count()} leads com status "proposta_enviada"...')
            
            for lead in leads:
                self.verificar_lead(lead, fix)

    def verificar_lead(self, lead, fix=False):
        self.stdout.write(f'\n--- LEAD: {lead.nome} (ID: {lead.id}) ---')
        self.stdout.write(f'Status atual: {lead.get_status_display()}')
        
        # Verificar orçamentos
        orcamentos = lead.orcamentos.all()
        propostas = lead.propostas.all()
        historico = lead.historico_contatos.all().order_by('-data_contato')
        
        self.stdout.write(f'Orçamentos: {orcamentos.count()}')
        for orc in orcamentos:
            self.stdout.write(f'  - {orc.numero} ({orc.get_status_display()}) - {orc.data_criacao}')
        
        self.stdout.write(f'Propostas: {propostas.count()}')
        for prop in propostas:
            self.stdout.write(f'  - {prop.numero} ({prop.get_status_display()}) - {prop.data_criacao}')
        
        self.stdout.write(f'Histórico de contatos: {historico.count()}')
        for hist in historico[:5]:  # Mostrar apenas os 5 mais recentes
            self.stdout.write(f'  - {hist.data_contato} | {hist.get_tipo_display()} | {hist.assunto}')
        
        # Determinar status correto
        status_correto = self.determinar_status_correto(lead, orcamentos, propostas)
        
        if status_correto != lead.status:
            self.stdout.write(
                self.style.WARNING(f'Status incorreto! Deveria ser: {status_correto}')
            )
            
            if fix:
                lead.status = status_correto
                lead.save()
                
                # Registrar correção no histórico
                HistoricoContato.objects.create(
                    lead=lead,
                    tipo='outros',
                    assunto='Status Corrigido',
                    descricao=f'Status corrigido automaticamente para {lead.get_status_display()}',
                    resultado='Status ajustado conforme situação real',
                    data_contato=timezone.now()
                )
                
                self.stdout.write(
                    self.style.SUCCESS(f'Status corrigido para: {lead.get_status_display()}')
                )
        else:
            self.stdout.write(
                self.style.SUCCESS('Status está correto!')
            )

    def determinar_status_correto(self, lead, orcamentos, propostas):
        """Determina o status correto baseado nos orçamentos e propostas"""
        
        # Se tem propostas, verificar status
        if propostas.exists():
            proposta_mais_recente = propostas.order_by('-data_criacao').first()
            if proposta_mais_recente.status == 'aprovada':
                return 'fechado_ganho'
            elif proposta_mais_recente.status == 'rejeitada':
                return 'fechado_perdido'
            else:
                return 'proposta_enviada'
        
        # Se tem orçamentos enviados mas sem propostas
        if orcamentos.filter(status='enviado').exists():
            return 'qualificado'  # Orçamento enviado, mas ainda não virou proposta
        
        # Se tem orçamentos aprovados
        if orcamentos.filter(status='aprovado').exists():
            return 'fechado_ganho'
        
        # Se tem orçamentos rejeitados
        if orcamentos.filter(status='rejeitado').exists():
            return 'fechado_perdido'
        
        # Se tem orçamentos mas não foram enviados
        if orcamentos.exists():
            return 'qualificado'
        
        # Se não tem nada, manter status atual ou definir como qualificado
        if lead.status == 'proposta_enviada':
            return 'qualificado'  # Provavelmente foi alterado incorretamente
        
        return lead.status