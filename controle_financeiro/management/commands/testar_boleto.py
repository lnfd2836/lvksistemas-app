from django.core.management.base import BaseCommand
import requests

class Command(BaseCommand):
    help = 'Testa se o link do boleto está funcionando'

    def add_arguments(self, parser):
        parser.add_argument('url', type=str, help='URL do boleto para testar')

    def handle(self, *args, **options):
        url = options['url']
        
        self.stdout.write(f"Testando URL: {url}")
        
        try:
            response = requests.get(url, timeout=30)
            self.stdout.write(f"Status Code: {response.status_code}")
            self.stdout.write(f"Content-Type: {response.headers.get('Content-Type', 'N/A')}")
            self.stdout.write(f"Content-Length: {response.headers.get('Content-Length', 'N/A')}")
            
            if response.status_code == 200:
                if 'application/pdf' in response.headers.get('Content-Type', ''):
                    self.stdout.write("✅ PDF válido encontrado!")
                else:
                    self.stdout.write("⚠️ Resposta não é um PDF")
                    self.stdout.write(f"Primeiros 200 caracteres: {response.text[:200]}")
            else:
                self.stdout.write("❌ Erro na requisição")
                self.stdout.write(f"Resposta: {response.text[:500]}")
                
        except Exception as e:
            self.stdout.write(f"❌ Erro: {str(e)}")