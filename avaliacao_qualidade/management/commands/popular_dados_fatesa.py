from django.core.management.base import BaseCommand
from django.db import transaction
from avaliacao_qualidade.models import Curso, Coordenador, Professor


class Command(BaseCommand):
    help = 'Popula dados iniciais da FATESA (cursos, coordenadores e professores)'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Iniciando população de dados da FATESA...'))
        
        with transaction.atomic():
            # === COORDENADORES ===
            coordenadores_data = [
                'Dr. Mauad',
                'Dr. Fernando', 
                'Dr. Procópio',
                'Dr. Jorge',
                'Dra. Daniela',
                'Dr. Renato',
                'Dr. Marcus Ferez',
                'Dr. Joel',
                'Dr. Guilherme Luna',
                'Dr. Augusto',
                'Dr. Carlos César',
                'Dr. Victor Campos'
            ]
            
            coordenadores_criados = 0
            for nome in coordenadores_data:
                coordenador, created = Coordenador.objects.get_or_create(
                    nome=nome,
                    defaults={'ativo': True}
                )
                if created:
                    coordenadores_criados += 1
            
            self.stdout.write(f'Coordenadores criados: {coordenadores_criados}')
            
            # === PROFESSORES ===
            professores_data = [
                'Dr. Mauad',
                'Dr. Fernando',
                'Dr. Procópio', 
                'Dr. Jorge',
                'Dr. Amaury',
                'Dr. Otávio',
                'Dra. Eliane',
                'Dra. Camila',
                'Dra. Rafaela',
                'Dra. Daniela',
                'Dr. Danilo',
                'Dr. Vinicius',
                'Dr. Guilherme',
                'Dr. Renato',
                'Dr. Marcus Ferez',
                'Dra. Fernanda',
                'Dr. Joel',
                'Dr. Guilherme Luna',
                'Dr. Augusto',
                'Dr. Chufalo',
                'Dr. Carlos César',
                'Dr. Victor Campos',
                'Dra. Flávia',
                'Dra. Tatiana'
            ]
            
            professores_criados = 0
            for nome in professores_data:
                professor, created = Professor.objects.get_or_create(
                    nome=nome,
                    defaults={'ativo': True}
                )
                if created:
                    professores_criados += 1
            
            self.stdout.write(f'Professores criados: {professores_criados}')
            
            # === CURSOS ===
            cursos_data = [
                ('AV001', 'Acesso Vascular Guiado por Ultrassonografia (acesso periférico, arterial e venoso central)'),
                ('AA001', 'Aparelhos Auditivos Módulo Avançado'),
                ('AH001', 'Atualização em Hipertensão Arterial'),
                ('AE001', 'Avançada em Endovaginal - Endometriose In Company'),
                ('AI001', 'Avançado de Imersão em Procedimentos Minimamente Invasivos Guiados por Ultrassom - Membros Superiores'),
                ('AO001', 'Avançado de Intervenções Osteoarticulares Guiadas por Ultrassonografia com ênfase em Membros Inferiores'),
                ('BG001', 'Básico de Ultrassonografia em Ginecologia e Obstetrícia'),
                ('BM001', 'Básico de Ultrassonografia em Medicina Interna'),
                ('BU001', 'Básico em Ultrassonografia Geral'),
                ('BM002', 'Básico Ultrassonografia do Sistema Musculoesquelético'),
                ('CG001', 'Cosmetoginecologia e Energias – Ninfoplastia, Laser, FRAXX e US Microfocado'),
                ('DP001', 'Dermatologia Pediátrica'),
                ('DE001', 'Dermatoscopia'),
                ('DI001', 'DIU e Saúde da Mulher'),
                ('EB001', 'Ecocardiografia Básica I'),
                ('EC001', 'Ecocardiografia em Cardiopatia Congênita'),
                ('EF001', 'Ecocardiografia Fetal'),
                ('ED001', 'Eco-Doppler Vascular'),
                ('IE001', 'Intensivo de Estética Íntima Feminina'),
                ('IF001', 'Intensivo de Fleboestética - Hands ON'),
                ('IR001', 'Intensivo de Rinomodelação'),
                ('IT001', 'Intensivo de Toxina Botulínica'),
                ('IN001', 'Intradermoterapia Facial (Skinbooster, Lipo de Papada e Intradermoterapia)'),
                ('JI001', 'JIU - Jornada Internacional de Ultrassonografia'),
                ('LE001', 'Laudos e Equipamentos'),
                ('MC001', 'Mamografia Convencional e Digital'),
                ('NE001', 'Noções Básicas de Ecocardiografia Transesofágica com Simulador'),
                ('NP001', 'Noções Básicas de Ultrassom de Pele'),
                ('PT001', 'Patologia do Trato Genital Inferior (Colposcopia, Laser, Crioterapia, Anuscopia) -Teoria gravada e presencial'),
                ('PC001', 'Point of Care para Intensivista e Medicina de Urgência (USIMUR)'),
                ('PR001', 'Prática em Transplante Masculino; Feminino; Barba; Sobrancelhas'),
                ('P1001', 'Prática I - Ultrassonografia Prática (Endovaginal/Doppler)'),
                ('P2001', 'Prática II - Ultrassonografia Prática (Endovaginal Avançado/Morfológico/Gestação/Laudos)'),
                ('P3001', 'Prática III - Ultrassonografia Prática (Ecocardiografia/Morfo de 1º /Mama)'),
                ('PI001', 'Prática Intensiva em Ecocardiografia'),
                ('PE001', 'Prática Intensiva na Endoscopia Digestiva Alta'),
                ('P4001', 'Prática IV - Ultrassonografia Prática Final'),
                ('PP001', 'Preparatório Prova de Título em Dermatologia - TED'),
                ('PM001', 'Procedimento Estético Injetável para Microvasos'),
                ('PQ001', 'Procedimentos Minimamente Invasivos Guiados por Ultrassom: Quadril'),
                ('RT001', 'Reciclagem e Preparatório para o Título de Especialista em Ginecologia e Obstetrícia - TEGO'),
                ('RU001', 'Reciclagem e Preparatório para o Título de Especialista em Ultrassonografia Geral (TEUS)'),
                ('RP001', 'Reciclagem e Preparatório para o Título de Especialista em Ultrassonografia Geral (TEUS) - Prático'),
                ('RG001', 'Reciclagem e Preparatório para o Título de Especialista em Ultrassonografia na Ginecologia e Obstetrícia (TEUS-GO)'),
                ('RO001', 'Reciclagem e Preparatório para Título de Especialista em Ginecologia e Obstetrícia/TEGO'),
                ('RV001', 'Reciclagem para o Título de Especialista em Ultrassonografia Vascular'),
                ('TC001', 'Tomografia Computadorizada Cabeça e Pescoço'),
                ('TC002', 'Tomografia Computadorizada Coluna'),
                ('TC003', 'Tomografia Computadorizada Sistema Nervoso Central'),
                ('TE001', 'Tópicos Especiais em Ecocardiografia'),
                ('TB001', 'Transplante Capilar - Body Hair Transplant'),
                ('TC004', 'Transplante Capilar em regiões com cicatrizes'),
                ('TF001', 'Transplante Capilar Feminino'),
                ('TM001', 'Transplante Capilar Masculino - Técnica FUE- Follicular Unit Extraction'),
                ('TA001', 'Transplante Capilar Masculino Avançado - Tecnica Fue Long - Hair'),
                ('TB002', 'Transplante de Barba - Tecnica FUE - Follicular Unit Extraction'),
                ('TB003', 'Transplante De Barba Avançado - Técnica FUE Long Hair'),
                ('TS001', 'Transplante de Sobrancelhas - Tecnica FUE - Follcular Unit Extraction'),
                ('TS002', 'Transplante sobrancelha Avançado - Técnica FUE Long Hair'),
                ('TR001', 'Tricologia Aplicada – Diagnóstico e Tratamento das Alopécias'),
                ('UP001', 'Ultrassom Point of Care Pediátrico'),
                ('UA001', 'Ultrassonografia Abdominal de Pequenos Animais'),
                ('UC001', 'Ultrassonografia Avançada de Carótidas e Vertebrais'),
                ('UA002', 'Ultrassonografia Avançada do Sistema Arterial dos Membros Inferiores In Company'),
                ('UA003', 'Ultrassonografia Avançada do Sistema Arterial nos Membros Inferiores'),
                ('UV001', 'Ultrassonografia Avançada do Sistema Venoso dos Membros Inferiores - In Company'),
                ('UV002', 'Ultrassonografia Avançada do Sistema Venoso nos Membros Inferiores'),
                ('UM001', 'Ultrassonografia Avançada dos Membros Superiores com e sem Fístula (FAV) Arteriovenosa Terapêutica In Company'),
                ('UM002', 'Ultrassonografia Avançada dos Membros Superiores com e sem Fístula (FAVT) Arteriovenosa Terapêutica'),
                ('UB001', 'Ultrassonografia Avançada em Bolsa Testicular e Pênis'),
                ('UE001', 'Ultrassonografia Avançada em Endovaginal – Assoalho Pélvico e Uroginecologia'),
                ('UE002', 'Ultrassonografia Avançada em Endovaginal - Endometriose'),
                ('UE003', 'Ultrassonografia Avançada Em Endovaginal - Histerossonografia e Disturbios Menstruais'),
                ('UE004', 'Ultrassonografia Avançada em Endovaginal I - Endometriose e Uroginecologia'),
                ('UG001', 'Ultrassonografia Avançada em Ginecologia e Obstetrícia - ISUOG'),
                ('UH001', 'Ultrassonografia Avançada Endovaginal- Histerossonossalpingografia (HyFoSy)'),
                ('UH002', 'Ultrassonografia Avançada Endovaginal II - Distúrbios Menstruais e Histerossonografia'),
                ('UB002', 'Ultrassonografia Básica Aplicada em Anestesia Regional'),
                ('UB003', 'Ultrassonografia Básica do Sistema Musculoesquelético'),
                ('UB004', 'Ultrassonografia Básica Em Ginecologia E Obstetrícia'),
                ('UB005', 'Ultrassonografia Básica em Medicina Interna'),
                ('UC002', 'Ultrassonografia Cervical'),
                ('UP002', 'Ultrassonografia da Parede Abdominal e Hérnia Inguinal'),
                ('UP003', 'Ultrassonografia da Parede Abdominal e Hérnia Inguinal - In Company'),
                ('UA004', 'Ultrassonografia das Artérias Oftálmicas para Pré-Eclâmpsia'),
                ('UC003', 'Ultrassonografia de Carótidas e Vertebrais - In Company'),
                ('UT001', 'Ultrassonografia de Tireoide com Doppler'),
                ('UC004', 'Ultrassonografia do Couro Cabeludo'),
                ('UP004', 'Ultrassonografia do Pênis – Estudo da Disfunção Erétil'),
                ('UQ001', 'Ultrassonografia do Quadril no Recém-Nascido'),
                ('US001', 'Ultrassonografia do Sistema Musculoesquelético e Tópicos avançados do Membro Inferiror'),
                ('US002', 'Ultrassonografia do Sistema Musculoesquelético e Tópicos Avançados do Membro Superior'),
                ('UD001', 'Ultrassonografia Doppler em Ginecologia'),
                ('UD002', 'Ultrassonografia Doppler em Ginecologia - In Company'),
                ('UD003', 'Ultrassonografia Doppler em Medicina Interna: Módulo Aorto Renal'),
                ('UD004', 'Ultrassonografia Doppler em Medicina Interna: Módulo Hepático'),
                ('UD005', 'Ultrassonografia Doppler em Medicina Interna: Módulo Hepático In Company'),
                ('UD006', 'Ultrassonografia Doppler em Obstetrícia'),
                ('UD007', 'Ultrassonografia Doppler em Obstetrícia - In Company'),
                ('UD008', 'Ultrassonografia Doppler Transcraniano'),
                ('UN001', 'Ultrassonografia dos Nervos Periféricos'),
                ('UB006', 'Ultrassonografia em Biópsia da Tireoide'),
                ('UB007', 'Ultrassonografia em Biópsia de Mama'),
                ('UB008', 'Ultrassonografia em Biópsia Endorretal'),
                ('UE005', 'Ultrassonografia em Elastografia Geral'),
                ('UE006', 'Ultrassonografia em Elastografia Hepática'),
                ('UE007', 'Ultrassonografia em Emergências (FAST) Traumáticas e Não Traumáticas'),
                ('UO001', 'Ultrassonografia em Oftalmologia'),
                ('UP005', 'Ultrassonografia em Partes Moles, Parede Abdominal e Hérnia Inguinal'),
                ('UP006', 'Ultrassonografia em Pediatria'),
                ('UR001', 'Ultrassonografia em Reumatologia'),
                ('UE008', 'Ultrassonografia Endovaginal'),
                ('UI001', 'Ultrassonografia Intervencionista'),
                ('UM003', 'Ultrassonografia Mamária'),
                ('UM004', 'Ultrassonografia Mamária In company'),
                ('UM005', 'Ultrassonografia Morfológica de Primeiro Trimestre'),
                ('UM006', 'Ultrassonografia Morfológica do Primeiro Trimestre In Company'),
                ('UM007', 'Ultrassonografia Morfológica do Segundo Trimestre'),
                ('UM008', 'Ultrassonografia Morfológica do Segundo Trimestre In Company'),
                ('UG002', 'Ultrassonografia na Gestação de Alto Risco'),
                ('UP007', 'Ultrassonografia na Prática Intensiva do Sistema Musculoesquelético e Reumatologia'),
                ('UP008', 'Ultrassonografia na Prática Intensiva do Sistema Musculoesquelético e Tópicos Avançados do Membro Inferior'),
                ('UP009', 'Ultrassonografia na Prática Intensiva do Sistema Musculoesquelético e Tópicos Avançados do Membro Inferior - In Company'),
                ('UP010', 'Ultrassonografia na Prática Intensiva do Sistema Musculoesquelético e Tópicos Avançados do Membro Superior'),
                ('UP011', 'Ultrassonografia na Prática Intensiva do Sistema Musculoesquelético e Tópicos Avançados do Membro Superior - In Company'),
                ('UP012', 'Ultrassonografia na Prática Intensiva do Sistema Urinário e Tópicos Avançados'),
                ('UP013', 'Ultrassonografia na Prática Intensiva em Medicina Interna'),
                ('UP014', 'Ultrassonografia na Prática Intensiva Mamária e Tópicos Avançados'),
                ('UP015', 'Ultrassonografia na Prática Intensiva Vascular'),
                ('UV003', 'Ultrassonografia na Varredura Abdominal'),
                ('UE009', 'Ultrassonografia nas Emergências em Ginecologia e Obstetrícia'),
                ('UO002', 'Ultrassonografia Ocular'),
                ('UP016', 'Ultrassonografia Point of Care na Obstetrícia'),
                ('UP017', 'Ultrassonografia Prática em Ginecologia e Obstetrícia'),
                ('UP018', 'Ultrassonografia Prostática'),
                ('UT002', 'Ultrassonografia Transfontanelar e de Medula Espinhal do Recém-Nascido'),
                ('UT003', 'Ultrassonografia Tridimensional 3D/4D'),
                ('UR002', 'Urgências Dermatológicas no Plantão Generalista'),
                ('V3001', 'VIP - 3D/4D e Ecocardiografia Fetal'),
                ('VB001', 'VIP - Biópsia de Mama'),
                ('VB002', 'VIP - Biópsia de Mama e de Tireoide'),
                ('VB003', 'VIP - Biópsia de Tireoide'),
                ('VE001', 'VIP - Ecocardiografia Fetal'),
                ('VE002', 'VIP - Eco-doppler Venoso de Membros Inferiores'),
                ('VE003', 'VIP - Ecografia de Tornozelo e Pé'),
                ('VE004', 'VIP - Elastografia Hepática'),
                ('VE005', 'VIP - Elastografia Hepática, Ultrassonografia Mamária e Tireoide com Doppler'),
                ('VE006', 'VIP - Endovaginal'),
                ('VF001', 'VIP - FAST'),
                ('VT001', 'VIP - Teus Prático'),
                ('VU001', 'VIP - Ultrassonografia Abdominal e Cervical'),
                ('VU002', 'VIP - Ultrassonografia da Tireoide'),
                ('VU003', 'VIP - Ultrassonografia do Sistema Musculoesquelético'),
                ('VU004', 'VIP - Ultrassonografia Doppler em Medicina Interna: Módulo Aorto Renal'),
                ('VU005', 'VIP - Ultrassonografia Doppler em Medicina Interna: Módulo Hepático'),
                ('VU006', 'VIP - Ultrassonografia em Pediatria'),
                ('VU007', 'VIP - Ultrassonografia Morfológica de 2º Trimestre'),
                ('VU008', 'VIP - Ultrassonografia na Prática Intensiva em Medicina Interna'),
                ('VU009', 'VIP - Ultrassonografia Prostática'),
                ('VU010', 'VIP - Ultrassonografia Transfontanelar'),
                ('VU011', 'VIP- Membro Superior sem Fístula Rim Normal'),
                ('VM001', 'VIP Morfológico de 1º Trimestre'),
                ('VM002', 'VIP Ultrassonografia Mamária')
            ]
            
            cursos_criados = 0
            for codigo, nome in cursos_data:
                curso, created = Curso.objects.get_or_create(
                    codigo=codigo,
                    defaults={
                        'nome': nome,
                        'ativo': True
                    }
                )
                if created:
                    cursos_criados += 1
            
            self.stdout.write(f'Cursos criados: {cursos_criados}')
            
            # Resumo
            total_coordenadores = Coordenador.objects.count()
            total_professores = Professor.objects.count()
            total_cursos = Curso.objects.count()
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'\n=== RESUMO ===\n'
                    f'Total de Coordenadores: {total_coordenadores}\n'
                    f'Total de Professores: {total_professores}\n'
                    f'Total de Cursos: {total_cursos}\n'
                    f'População de dados concluída com sucesso!'
                )
            )