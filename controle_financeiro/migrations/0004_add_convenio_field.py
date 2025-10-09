# Generated manually for adding convenio field

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('controle_financeiro', '0003_configuracaoboleto_codigo_cedente'),
    ]

    operations = [
        migrations.AddField(
            model_name='configuracaoboleto',
            name='convenio',
            field=models.CharField(blank=True, help_text='Número do convênio com a Caixa', max_length=20, null=True, verbose_name='Número do Convênio'),
        ),
    ]