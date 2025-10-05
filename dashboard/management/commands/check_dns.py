import subprocess
import socket
import ssl
import urllib.request
import urllib.error
from datetime import datetime
from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = 'Verifica a configuração DNS e conectividade dos domínios'

    def add_arguments(self, parser):
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Exibe informações detalhadas',
        )
        parser.add_argument(
            '--check-ssl',
            action='store_true',
            help='Verifica certificados SSL',
        )

    def handle(self, *args, **options):
        self.verbose = options['verbose']
        self.check_ssl = options['check_ssl']
        
        self.stdout.write(
            self.style.SUCCESS(f'=== Verificação DNS - {datetime.now().strftime("%d/%m/%Y %H:%M:%S")} ===')
        )
        
        # Domínios para verificar
        domains = [
            {
                'name': 'www.lvksistemas.com.br',
                'type': 'CNAME',
                'expected_target': 'octagonal-brook-oqbuqqt97582c9psm8wscgs8.herokudns.com'
            },
            {
                'name': 'lvksistemas.com.br',
                'type': 'ALIAS/ANAME',
                'expected_target': 'tetrahedral-goose-lm4se1i5s96qkuaqu2fz67jz.herokudns.com'
            }
        ]
        
        all_ok = True
        
        for domain in domains:
            self.stdout.write(f"\n--- Verificando {domain['name']} ---")
            domain_ok = self.check_domain(domain)
            all_ok = all_ok and domain_ok
            
            if self.check_ssl and domain_ok:
                self.check_ssl_certificate(domain['name'])
        
        # Resumo final
        if all_ok:
            self.stdout.write(
                self.style.SUCCESS('\n✅ Todos os domínios estão configurados corretamente!')
            )
        else:
            self.stdout.write(
                self.style.ERROR('\n❌ Alguns domínios precisam de correção.')
            )
            
        return all_ok

    def check_domain(self, domain_info):
        """Verifica a configuração DNS de um domínio"""
        domain_name = domain_info['name']
        expected_target = domain_info['expected_target']
        record_type = domain_info['type']
        
        try:
            # Verificar registro DNS
            if record_type == 'CNAME':
                actual_target = self.get_cname_record(domain_name)
            else:  # ALIAS/ANAME
                actual_target = self.get_a_record(domain_name)
            
            if actual_target:
                if expected_target in actual_target or actual_target in expected_target:
                    self.stdout.write(
                        self.style.SUCCESS(f'✅ DNS: {record_type} correto')
                    )
                    dns_ok = True
                else:
                    self.stdout.write(
                        self.style.ERROR(f'❌ DNS: {record_type} incorreto')
                    )
                    self.stdout.write(f'   Esperado: {expected_target}')
                    self.stdout.write(f'   Atual: {actual_target}')
                    dns_ok = False
            else:
                self.stdout.write(
                    self.style.ERROR(f'❌ DNS: Registro {record_type} não encontrado')
                )
                dns_ok = False
            
            # Verificar conectividade
            connectivity_ok = self.check_connectivity(domain_name)
            
            return dns_ok and connectivity_ok
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Erro ao verificar {domain_name}: {str(e)}')
            )
            return False

    def get_cname_record(self, domain):
        """Obtém o registro CNAME de um domínio"""
        try:
            result = subprocess.run(
                ['dig', domain, 'CNAME', '+short'],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip().rstrip('.')
            return None
        except (subprocess.TimeoutExpired, FileNotFoundError):
            # Fallback usando nslookup
            try:
                result = subprocess.run(
                    ['nslookup', '-type=CNAME', domain],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if 'canonical name' in result.stdout:
                    lines = result.stdout.split('\n')
                    for line in lines:
                        if 'canonical name' in line:
                            return line.split('=')[-1].strip().rstrip('.')
            except:
                pass
            return None

    def get_a_record(self, domain):
        """Obtém o registro A de um domínio"""
        try:
            result = subprocess.run(
                ['dig', domain, 'A', '+short'],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip()
            return None
        except (subprocess.TimeoutExpired, FileNotFoundError):
            # Fallback usando socket
            try:
                ip = socket.gethostbyname(domain)
                return ip
            except socket.gaierror:
                return None

    def check_connectivity(self, domain):
        """Verifica a conectividade HTTP/HTTPS"""
        protocols = ['https', 'http'] if self.check_ssl else ['http']
        
        for protocol in protocols:
            url = f'{protocol}://{domain}'
            try:
                req = urllib.request.Request(url, method='HEAD')
                with urllib.request.urlopen(req, timeout=10) as response:
                    status_code = response.getcode()
                    if status_code < 400:
                        self.stdout.write(
                            self.style.SUCCESS(f'✅ Conectividade: {protocol.upper()} OK ({status_code})')
                        )
                        return True
                    else:
                        self.stdout.write(
                            self.style.WARNING(f'⚠️ Conectividade: {protocol.upper()} retornou {status_code}')
                        )
            except urllib.error.URLError as e:
                if self.verbose:
                    self.stdout.write(
                        self.style.ERROR(f'❌ Conectividade: {protocol.upper()} falhou - {str(e)}')
                    )
            except Exception as e:
                if self.verbose:
                    self.stdout.write(
                        self.style.ERROR(f'❌ Conectividade: Erro inesperado - {str(e)}')
                    )
        
        self.stdout.write(
            self.style.ERROR('❌ Conectividade: Nenhum protocolo funcionando')
        )
        return False

    def check_ssl_certificate(self, domain):
        """Verifica o certificado SSL"""
        try:
            context = ssl.create_default_context()
            with socket.create_connection((domain, 443), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=domain) as ssock:
                    cert = ssock.getpeercert()
                    
                    # Verificar validade
                    not_after = datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
                    days_until_expiry = (not_after - datetime.now()).days
                    
                    if days_until_expiry > 30:
                        self.stdout.write(
                            self.style.SUCCESS(f'✅ SSL: Certificado válido (expira em {days_until_expiry} dias)')
                        )
                    elif days_until_expiry > 0:
                        self.stdout.write(
                            self.style.WARNING(f'⚠️ SSL: Certificado expira em {days_until_expiry} dias')
                        )
                    else:
                        self.stdout.write(
                            self.style.ERROR('❌ SSL: Certificado expirado')
                        )
                        
                    if self.verbose:
                        self.stdout.write(f'   Emissor: {cert.get("issuer", "N/A")}')
                        self.stdout.write(f'   Válido até: {cert.get("notAfter", "N/A")}')
                        
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ SSL: Não foi possível verificar certificado - {str(e)}')
            )