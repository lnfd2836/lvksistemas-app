# Generated migration for login personalizado models

from django.db import migrations, models
import django.db.models.deletion
import uuid
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('lojas', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='LoginPersonalizado',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('titulo', models.CharField(default='Login', max_length=200, verbose_name='Título da Página')),
                ('subtitulo', models.CharField(blank=True, max_length=300, verbose_name='Subtítulo')),
                ('logo', models.ImageField(blank=True, null=True, upload_to='login_personalizado/logos/', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'svg'])], verbose_name='Logo da Loja')),
                ('imagem_fundo', models.ImageField(blank=True, null=True, upload_to='login_personalizado/fundos/', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])], verbose_name='Imagem de Fundo')),
                ('cor_primaria', models.CharField(default='#007bff', help_text='Formato hexadecimal (#000000)', max_length=7, verbose_name='Cor Primária')),
                ('cor_secundaria', models.CharField(default='#6c757d', help_text='Formato hexadecimal (#000000)', max_length=7, verbose_name='Cor Secundária')),
                ('cor_fundo', models.CharField(default='#ffffff', help_text='Formato hexadecimal (#000000)', max_length=7, verbose_name='Cor de Fundo')),
                ('cor_texto', models.CharField(default='#333333', help_text='Formato hexadecimal (#000000)', max_length=7, verbose_name='Cor do Texto')),
                ('tema', models.CharField(choices=[('padrao', 'Padrão'), ('moderno', 'Moderno'), ('minimalista', 'Minimalista'), ('corporativo', 'Corporativo'), ('personalizado', 'Personalizado')], default='padrao', max_length=20, verbose_name='Tema')),
                ('css_personalizado', models.TextField(blank=True, help_text='CSS adicional para personalização avançada', verbose_name='CSS Personalizado')),
                ('mostrar_logo', models.BooleanField(default=True, verbose_name='Mostrar Logo')),
                ('mostrar_nome_loja', models.BooleanField(default=True, verbose_name='Mostrar Nome da Loja')),
                ('permitir_lembrar_senha', models.BooleanField(default=True, verbose_name='Permitir "Lembrar de Mim"')),
                ('mostrar_link_recuperar_senha', models.BooleanField(default=True, verbose_name='Mostrar Link "Esqueci Minha Senha"')),
                ('mensagem_boas_vindas', models.TextField(blank=True, help_text='Mensagem exibida na tela de login', verbose_name='Mensagem de Boas-vindas')),
                ('mensagem_rodape', models.TextField(blank=True, help_text='Mensagem exibida no rodapé da página', verbose_name='Mensagem do Rodapé')),
                ('url_personalizada', models.CharField(blank=True, help_text='Ex: minha-loja (acessível via /login/minha-loja/)', max_length=100, unique=True, verbose_name='URL Personalizada')),
                ('ativo', models.BooleanField(default=True, verbose_name='Login Personalizado Ativo')),
                ('data_criacao', models.DateTimeField(auto_now_add=True, verbose_name='Data de Criação')),
                ('data_atualizacao', models.DateTimeField(auto_now=True, verbose_name='Última Atualização')),
                ('loja', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='login_personalizado', to='lojas.loja', verbose_name='Loja')),
            ],
            options={
                'verbose_name': 'Login Personalizado',
                'verbose_name_plural': 'Logins Personalizados',
                'ordering': ['loja__nome'],
            },
        ),
        migrations.CreateModel(
            name='HistoricoLoginLoja',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('usuario', models.CharField(max_length=150, verbose_name='Usuário')),
                ('ip_address', models.GenericIPAddressField(verbose_name='Endereço IP')),
                ('user_agent', models.TextField(blank=True, verbose_name='User Agent')),
                ('sucesso', models.BooleanField(default=True, verbose_name='Login Bem-sucedido')),
                ('data_tentativa', models.DateTimeField(auto_now_add=True, verbose_name='Data da Tentativa')),
                ('metodo_login', models.CharField(default='personalizado', max_length=50, verbose_name='Método de Login')),
                ('dispositivo', models.CharField(blank=True, max_length=100, verbose_name='Dispositivo')),
                ('navegador', models.CharField(blank=True, max_length=100, verbose_name='Navegador')),
                ('loja', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='historico_logins', to='lojas.loja', verbose_name='Loja')),
            ],
            options={
                'verbose_name': 'Histórico de Login da Loja',
                'verbose_name_plural': 'Histórico de Logins das Lojas',
                'ordering': ['-data_tentativa'],
            },
        ),
    ]