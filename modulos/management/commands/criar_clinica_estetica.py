from django.core.management.base import BaseCommand
from modulos.models import (
    TipoLoja, ModuloLoja, CampoPersonalizado,
    ServicoEstetica, ProtocoloEmagrecimento, PacoteTratamento
)


class Command(BaseCommand):
    help = 'Cria o tipo de loja Clínica de Estética com todos os módulos e configurações'

    def handle(self, *args, **options):
        self.stdout.write('Criando tipo de loja Clínica de Estética...')
        
        # 1. Criar tipo de loja Clínica de Estética
        clinica_estetica, created = TipoLoja.objects.get_or_create(
            nome='clinica_estetica',
            defaults={
                'descricao': 'Clínica de estética com sistema completo de agendamentos, tratamentos faciais e corporais, protocolos de emagrecimento e gestão de clientes',
                'icone': 'fas fa-spa',
                'cor_primaria': '#e91e63',
                'cor_secundaria': '#f8bbd9',
                
                # Configurações específicas para produtos (produtos de estética)
                'tem_categoria_produto': True,
                'tem_marca_produto': True,
                'tem_tamanho_produto': False,
                'tem_cor_produto': False,
                'tem_peso_produto': True,  # Para produtos como cremes, sérums
                'tem_volume_produto': True,  # Para produtos líquidos
                'tem_data_validade': True,  # Importante para produtos cosméticos
                'tem_codigo_barras': True,
                'tem_estoque_minimo': True,
                
                # Campos específicos para clientes (mais detalhados para estética)
                'tem_data_nascimento_cliente': True,
                'tem_sexo_cliente': True,
                'tem_cpf_cliente': True,
                'tem_rg_cliente': True,  # Importante para procedimentos
                'tem_cnpj_cliente': False,
                
                # Campos específicos para vendas
                'tem_desconto_venda': True,
                'tem_taxa_entrega': False,
                'tem_mesa_venda': False,
                'tem_garcom_venda': False,
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS('✅ Tipo de loja Clínica de Estética criado'))
        else:
            self.stdout.write(self.style.WARNING('⚠️  Tipo de loja Clínica de Estética já existe'))
        
        # 2. Criar módulos específicos para clínica de estética
        modulos_data = [
            {
                'nome': 'Agendamentos',
                'descricao': 'Sistema completo de agendamento de clientes com calendário, horários disponíveis e gestão de profissionais',
                'icone': 'fas fa-calendar-alt',
                'url': '/estetica/agendamentos/',
                'ordem': 1,
            },
            {
                'nome': 'Serviços',
                'descricao': 'Catálogo de serviços oferecidos: botox, limpeza de pele, aplicação de soro, tratamentos faciais e corporais',
                'icone': 'fas fa-concierge-bell',
                'url': '/estetica/servicos/',
                'ordem': 2,
            },
            {
                'nome': 'Protocolos de Emagrecimento',
                'descricao': 'Gestão de protocolos de emagrecimento com acompanhamento de evolução e resultados',
                'icone': 'fas fa-weight',
                'url': '/estetica/protocolos/',
                'ordem': 3,
            },
            {
                'nome': 'Clientes',
                'descricao': 'Gestão completa de clientes com ficha de anamnese, histórico de tratamentos e evolução',
                'icone': 'fas fa-users',
                'url': '/estetica/clientes/',
                'ordem': 4,
            },
            {
                'nome': 'Pacotes de Tratamento',
                'descricao': 'Criação e gestão de pacotes promocionais com múltiplos serviços',
                'icone': 'fas fa-gift',
                'url': '/estetica/pacotes/',
                'ordem': 5,
            },
            {
                'nome': 'Retornos',
                'descricao': 'Sistema de agendamento de retornos e acompanhamento pós-tratamento',
                'icone': 'fas fa-redo',
                'url': '/estetica/retornos/',
                'ordem': 6,
            },
            {
                'nome': 'Relatórios',
                'descricao': 'Relatórios de atendimentos, faturamento, clientes mais frequentes e evolução de tratamentos',
                'icone': 'fas fa-chart-bar',
                'url': '/estetica/relatorios/',
                'ordem': 7,
            },
        ]
        
        for modulo_data in modulos_data:
            modulo, created = ModuloLoja.objects.get_or_create(
                tipo_loja=clinica_estetica,
                nome=modulo_data['nome'],
                defaults=modulo_data
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'✅ Módulo "{modulo_data["nome"]}" criado'))
            else:
                self.stdout.write(self.style.WARNING(f'⚠️  Módulo "{modulo_data["nome"]}" já existe'))
        
        # 3. Criar campos personalizados específicos para produtos de estética
        campos_personalizados = [
            {
                'nome': 'Tipo de Pele',
                'slug': 'tipo_pele',
                'tipo_campo': 'escolha',
                'obrigatorio': True,
                'opcoes': 'Normal\nOleosa\nSeca\nMista\nSensível',
                'ordem': 1,
            },
            {
                'nome': 'Fator de Proteção Solar (FPS)',
                'slug': 'fps',
                'tipo_campo': 'numero',
                'obrigatorio': False,
                'ordem': 2,
            },
            {
                'nome': 'Princípio Ativo',
                'slug': 'principio_ativo',
                'tipo_campo': 'texto',
                'obrigatorio': False,
                'ordem': 3,
            },
            {
                'nome': 'Indicação de Uso',
                'slug': 'indicacao_uso',
                'tipo_campo': 'texto',
                'obrigatorio': False,
                'ordem': 4,
            },
            {
                'nome': 'Contraindicações',
                'slug': 'contraindicacoes',
                'tipo_campo': 'texto',
                'obrigatorio': False,
                'ordem': 5,
            },
            {
                'nome': 'Modo de Uso',
                'slug': 'modo_uso',
                'tipo_campo': 'texto',
                'obrigatorio': False,
                'ordem': 6,
            },
            {
                'nome': 'Requer Receita Médica',
                'slug': 'requer_receita',
                'tipo_campo': 'boolean',
                'obrigatorio': False,
                'ordem': 7,
            },
        ]
        
        for campo_data in campos_personalizados:
            campo, created = CampoPersonalizado.objects.get_or_create(
                tipo_loja=clinica_estetica,
                slug=campo_data['slug'],
                defaults=campo_data
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'✅ Campo personalizado "{campo_data["nome"]}" criado'))
            else:
                self.stdout.write(self.style.WARNING(f'⚠️  Campo personalizado "{campo_data["nome"]}" já existe'))
        
        # 4. Criar serviços padrão de estética
        servicos_padrao = [
            {
                'nome': 'Botox - Área dos Olhos',
                'descricao': 'Aplicação de toxina botulínica na região dos olhos para suavizar rugas e linhas de expressão',
                'categoria': 'injetavel',
                'duracao_minutos': 30,
                'preco': 800.00,
                'requer_consulta_medica': True,
                'idade_minima': 18,
                'contraindicacoes': 'Gravidez, amamentação, doenças neuromusculares, alergia ao produto',
                'cuidados_pos_procedimento': 'Evitar deitar por 4 horas, não massagear a região, evitar exercícios por 24h',
            },
            {
                'nome': 'Limpeza de Pele Profunda',
                'descricao': 'Limpeza completa com extração de comedões, esfoliação e hidratação profunda',
                'categoria': 'facial',
                'duracao_minutos': 60,
                'preco': 120.00,
                'requer_consulta_medica': False,
                'idade_minima': 16,
                'contraindicacoes': 'Pele com lesões ativas, rosácea em crise',
                'cuidados_pos_procedimento': 'Usar protetor solar, evitar exposição solar por 48h',
            },
            {
                'nome': 'Aplicação de Soro Vitamina C',
                'descricao': 'Aplicação de soro com vitamina C para clareamento e rejuvenescimento da pele',
                'categoria': 'facial',
                'duracao_minutos': 45,
                'preco': 80.00,
                'requer_consulta_medica': False,
                'idade_minima': 16,
                'contraindicacoes': 'Alergia à vitamina C, pele sensível',
                'cuidados_pos_procedimento': 'Usar protetor solar, evitar produtos com ácidos por 24h',
            },
            {
                'nome': 'Drenagem Linfática',
                'descricao': 'Massagem de drenagem linfática para redução de inchaço e melhora da circulação',
                'categoria': 'corporal',
                'duracao_minutos': 60,
                'preco': 100.00,
                'requer_consulta_medica': False,
                'idade_minima': 16,
                'contraindicacoes': 'Infecções ativas, trombose, câncer',
                'cuidados_pos_procedimento': 'Beber muita água, evitar álcool por 24h',
            },
            {
                'nome': 'Criolipólise - Abdômen',
                'descricao': 'Tratamento para redução de gordura localizada no abdômen através do frio',
                'categoria': 'corporal',
                'duracao_minutos': 60,
                'preco': 400.00,
                'requer_consulta_medica': True,
                'idade_minima': 18,
                'contraindicacoes': 'Gravidez, hérnia, problemas circulatórios',
                'cuidados_pos_procedimento': 'Massagear a região, beber muita água, exercícios leves',
            },
        ]
        
        for servico_data in servicos_padrao:
            servico, created = ServicoEstetica.objects.get_or_create(
                nome=servico_data['nome'],
                defaults=servico_data
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'✅ Serviço "{servico_data["nome"]}" criado'))
            else:
                self.stdout.write(self.style.WARNING(f'⚠️  Serviço "{servico_data["nome"]}" já existe'))
        
        # 5. Criar protocolos de emagrecimento padrão
        protocolos_padrao = [
            {
                'nome': 'Protocolo Drenagem + Massagem Modeladora',
                'descricao': 'Protocolo combinado de drenagem linfática e massagem modeladora para redução de medidas',
                'tipo_protocolo': 'combinado',
                'numero_sessoes': 10,
                'intervalo_dias': 3,
                'duracao_sessao_minutos': 90,
                'preco_total': 800.00,
                'preco_sessao': 80.00,
                'indicacoes': 'Redução de medidas, melhora da circulação, redução de inchaço',
                'contraindicacoes': 'Gravidez, problemas circulatórios graves, infecções ativas',
                'resultados_esperados': 'Redução de 2-4 cm de circunferência, melhora da textura da pele',
            },
            {
                'nome': 'Protocolo Criolipólise Completo',
                'descricao': 'Protocolo completo de criolipólise para redução de gordura localizada',
                'tipo_protocolo': 'criolipolise',
                'numero_sessoes': 3,
                'intervalo_dias': 30,
                'duracao_sessao_minutos': 60,
                'preco_total': 1000.00,
                'preco_sessao': 333.33,
                'indicacoes': 'Gordura localizada resistente à dieta e exercícios',
                'contraindicacoes': 'Gravidez, hérnia, problemas circulatórios, obesidade mórbida',
                'resultados_esperados': 'Redução de 20-30% da gordura localizada, melhora do contorno corporal',
            },
        ]
        
        for protocolo_data in protocolos_padrao:
            protocolo, created = ProtocoloEmagrecimento.objects.get_or_create(
                nome=protocolo_data['nome'],
                defaults=protocolo_data
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'✅ Protocolo "{protocolo_data["nome"]}" criado'))
            else:
                self.stdout.write(self.style.WARNING(f'⚠️  Protocolo "{protocolo_data["nome"]}" já existe'))
        
        # 6. Criar pacotes de tratamento padrão
        pacotes_padrao = [
            {
                'nome': 'Pacote Facial Completo',
                'descricao': 'Pacote com limpeza de pele, aplicação de soro e hidratação profunda',
                'numero_sessoes': 4,
                'validade_dias': 60,
                'preco_total': 300.00,
                'desconto_percentual': 20.00,
            },
            {
                'nome': 'Pacote Corporal Premium',
                'descricao': 'Pacote com drenagem linfática, massagem modeladora e criolipólise',
                'numero_sessoes': 8,
                'validade_dias': 90,
                'preco_total': 1200.00,
                'desconto_percentual': 25.00,
            },
        ]
        
        for pacote_data in pacotes_padrao:
            pacote, created = PacoteTratamento.objects.get_or_create(
                nome=pacote_data['nome'],
                defaults=pacote_data
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'✅ Pacote "{pacote_data["nome"]}" criado'))
            else:
                self.stdout.write(self.style.WARNING(f'⚠️  Pacote "{pacote_data["nome"]}" já existe'))
        
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('🎉 Clínica de Estética criada com sucesso!'))
        self.stdout.write('')
        self.stdout.write('📋 Funcionalidades incluídas:')
        self.stdout.write('   ✅ Sistema de agendamentos com calendário')
        self.stdout.write('   ✅ Catálogo de serviços (botox, limpeza, soro, etc.)')
        self.stdout.write('   ✅ Protocolos de emagrecimento')
        self.stdout.write('   ✅ Gestão completa de clientes')
        self.stdout.write('   ✅ Sistema de retornos')
        self.stdout.write('   ✅ Pacotes promocionais')
        self.stdout.write('   ✅ Relatórios e acompanhamento')
        self.stdout.write('   ✅ Campos personalizados para produtos de estética')
        self.stdout.write('')
        self.stdout.write('🚀 Próximos passos:')
        self.stdout.write('   1. Criar as views e templates para cada módulo')
        self.stdout.write('   2. Configurar URLs específicas')
        self.stdout.write('   3. Criar forms para agendamentos e fichas')
        self.stdout.write('   4. Implementar sistema de notificações')
        self.stdout.write('   5. Testar todas as funcionalidades')
