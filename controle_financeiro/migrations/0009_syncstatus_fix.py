# Generated manually to fix SyncStatus table

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('controle_financeiro', '0008_syncstatus'),
    ]

    operations = [
        migrations.CreateModel(
            name='SyncStatus',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(default='main', max_length=10, unique=True)),
                ('is_running', models.BooleanField(default=False)),
                ('sync_interval', models.IntegerField(default=300)),
                ('last_sync', models.DateTimeField(blank=True, null=True)),
                ('started_at', models.DateTimeField(blank=True, null=True)),
                ('stopped_at', models.DateTimeField(blank=True, null=True)),
                ('stats_json', models.TextField(default='{}')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Status de Sincronização',
                'verbose_name_plural': 'Status de Sincronização',
            },
        ),
    ]