from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Loja
from .models_login import LoginPersonalizado
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Loja)
def criar_login_personalizado(sender, instance, created, **kwargs):
    """
    Cria automaticamente uma configuração de login personalizado
    quando uma nova loja é criada, baseada no tipo de loja
    """
    if created:
        try:
            # Verificar se já existe (por segurança)
            if not hasattr(instance, 'login_personalizado'):
                # Configurações baseadas no tipo de loja
                config = obter_configuracao_por_tipo_loja(instance)
                
                LoginPersonalizado.objects.create(
                    loja=instance,
                    titulo=config['titulo'],
                    subtitulo=config['subtitulo'],
                    tema=config['tema'],
                    cor_primaria=config['cor_primaria'],
                    cor_secundaria=config['cor_secundaria'],
                    cor_fundo=config['cor_fundo'],
                    cor_texto=config['cor_texto'],
                    mensagem_boas_vindas=config['mensagem_boas_vindas'],
                    mensagem_rodape=config['mensagem_rodape'],
                    css_personalizado=config['css_personalizado'],
                    mostrar_logo=config['mostrar_logo'],
                    mostrar_nome_loja=config['mostrar_nome_loja'],
                    permitir_lembrar_senha=config['permitir_lembrar_senha'],
                    mostrar_link_recuperar_senha=config['mostrar_link_recuperar_senha'],
                    ativo=True
                )
                logger.info(f"Login personalizado criado automaticamente para loja: {instance.nome} (Tipo: {instance.tipo_loja})")
        except Exception as e:
            logger.error(f"Erro ao criar login personalizado para loja {instance.nome}: {str(e)}")


def obter_configuracao_por_tipo_loja(loja):
    """
    Retorna configuração de login personalizada baseada no tipo de loja
    """
    # Configuração padrão
    config_padrao = {
        'titulo': f"Acesso - {loja.nome}",
        'subtitulo': f"Entre com suas credenciais",
        'tema': 'padrao',
        'cor_primaria': '#007bff',
        'cor_secundaria': '#6c757d',
        'cor_fundo': '#ffffff',
        'cor_texto': '#333333',
        'mensagem_boas_vindas': f"Bem-vindo(a) à {loja.nome}!",
        'mensagem_rodape': f"© 2024 {loja.nome} - Todos os direitos reservados",
        'css_personalizado': '',
        'mostrar_logo': True,
        'mostrar_nome_loja': True,
        'permitir_lembrar_senha': True,
        'mostrar_link_recuperar_senha': True,
    }
    
    # Se não tem tipo de loja, usar padrão
    if not loja.tipo_loja:
        return config_padrao
    
    # Configurações específicas por tipo de loja
    configuracoes_tipos = {
        'controle_qualidade': {
            'titulo': f"Portal FATESA - {loja.nome}",
            'subtitulo': "Sistema de Controle de Qualidade Educacional",
            'tema': 'corporativo',
            'cor_primaria': '#2c3e50',
            'cor_secundaria': '#34495e',
            'cor_fundo': '#ecf0f1',
            'cor_texto': '#2c3e50',
            'mensagem_boas_vindas': f"Bem-vindo ao Sistema de Controle de Qualidade da {loja.nome}",
            'mensagem_rodape': f"FATESA - {loja.nome} | Sistema Seguro de Avaliação",
            'css_personalizado': '''
                .login-card {
                    border-top: 4px solid #2c3e50;
                }
                .btn-login {
                    background: linear-gradient(135deg, #2c3e50, #34495e);
                }
            ''',
        },
        'clinica_estetica': {
            'titulo': f"Clínica {loja.nome}",
            'subtitulo': "Portal de Beleza e Bem-estar",
            'tema': 'moderno',
            'cor_primaria': '#e91e63',
            'cor_secundaria': '#f06292',
            'cor_fundo': '#fce4ec',
            'cor_texto': '#880e4f',
            'mensagem_boas_vindas': f"Bem-vinda à {loja.nome} - Sua beleza é nossa prioridade",
            'mensagem_rodape': f"{loja.nome} - Beleza, Saúde e Bem-estar",
            'css_personalizado': '''
                body {
                    background: linear-gradient(135deg, #fce4ec, #f8bbd9);
                }
                .login-card {
                    backdrop-filter: blur(15px);
                    background: rgba(255, 255, 255, 0.9);
                }
            ''',
        },
        'lanchonete': {
            'titulo': f"Lanchonete {loja.nome}",
            'subtitulo': "Sabor que você já conhece",
            'tema': 'moderno',
            'cor_primaria': '#ff9800',
            'cor_secundaria': '#f57c00',
            'cor_fundo': '#fff3e0',
            'cor_texto': '#e65100',
            'mensagem_boas_vindas': f"Bem-vindo à {loja.nome} - O melhor sabor da região!",
            'mensagem_rodape': f"{loja.nome} - Tradição em sabor desde sempre",
            'css_personalizado': '''
                .login-card {
                    box-shadow: 0 8px 32px rgba(255, 152, 0, 0.3);
                }
                .btn-login {
                    background: linear-gradient(135deg, #ff9800, #f57c00);
                }
            ''',
        },
        'farmacia': {
            'titulo': f"Farmácia {loja.nome}",
            'subtitulo': "Cuidando da sua saúde",
            'tema': 'minimalista',
            'cor_primaria': '#4caf50',
            'cor_secundaria': '#66bb6a',
            'cor_fundo': '#e8f5e8',
            'cor_texto': '#2e7d32',
            'mensagem_boas_vindas': f"Bem-vindo à {loja.nome} - Sua saúde em primeiro lugar",
            'mensagem_rodape': f"{loja.nome} - Farmácia de confiança",
            'css_personalizado': '''
                .login-card {
                    border-left: 5px solid #4caf50;
                }
            ''',
        },
        'roupas': {
            'titulo': f"Moda {loja.nome}",
            'subtitulo': "Estilo e elegância",
            'tema': 'moderno',
            'cor_primaria': '#9c27b0',
            'cor_secundaria': '#ba68c8',
            'cor_fundo': '#f3e5f5',
            'cor_texto': '#4a148c',
            'mensagem_boas_vindas': f"Bem-vindo à {loja.nome} - Moda que inspira",
            'mensagem_rodape': f"{loja.nome} - Vista-se com estilo",
            'css_personalizado': '''
                body {
                    background: linear-gradient(135deg, #f3e5f5, #e1bee7);
                }
            ''',
        },
        'conveniencia': {
            'titulo': f"{loja.nome}",
            'subtitulo': "Praticidade no seu dia a dia",
            'tema': 'padrao',
            'cor_primaria': '#2196f3',
            'cor_secundaria': '#64b5f6',
            'cor_fundo': '#e3f2fd',
            'cor_texto': '#0d47a1',
            'mensagem_boas_vindas': f"Bem-vindo à {loja.nome} - Tudo que você precisa",
            'mensagem_rodape': f"{loja.nome} - Conveniência 24 horas",
        },
    }
    
    # Buscar configuração específica ou usar padrão
    tipo_nome = loja.tipo_loja.nome if loja.tipo_loja else 'padrao'
    config_especifica = configuracoes_tipos.get(tipo_nome, {})
    
    # Mesclar configuração padrão com específica
    config_final = config_padrao.copy()
    config_final.update(config_especifica)
    
    return config_final


@receiver(post_save, sender=Loja)
def atualizar_login_personalizado(sender, instance, created, **kwargs):
    """
    Atualiza informações do login personalizado quando a loja é modificada
    """
    if not created:
        try:
            login_config = getattr(instance, 'login_personalizado', None)
            if login_config:
                # Atualizar apenas se os campos não foram personalizados
                if login_config.titulo == f"Login - {instance.nome}" or not login_config.titulo:
                    login_config.titulo = f"Login - {instance.nome}"
                
                if login_config.subtitulo == f"Acesse sua conta na {instance.nome}" or not login_config.subtitulo:
                    login_config.subtitulo = f"Acesse sua conta na {instance.nome}"
                
                if login_config.mensagem_boas_vindas == f"Bem-vindo(a) à {instance.nome}!" or not login_config.mensagem_boas_vindas:
                    login_config.mensagem_boas_vindas = f"Bem-vindo(a) à {instance.nome}!"
                
                # Desativar login personalizado se loja estiver inativa
                if instance.status != 'ativa':
                    login_config.ativo = False
                elif instance.status == 'ativa' and not login_config.ativo:
                    # Reativar se loja voltou a ficar ativa
                    login_config.ativo = True
                
                login_config.save()
                logger.info(f"Login personalizado atualizado para loja: {instance.nome}")
        except Exception as e:
            logger.error(f"Erro ao atualizar login personalizado para loja {instance.nome}: {str(e)}")