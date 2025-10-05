#!/usr/bin/env python3
"""
Script para verificação rápida do status dos domínios
Pode ser executado independentemente do Django
"""

import subprocess
import socket
import sys
from datetime import datetime


def run_command(cmd, timeout=10):
    """Executa um comando e retorna o resultado"""
    try:
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            timeout=timeout,
            shell=isinstance(cmd, str)
        )
        return result.stdout.strip(), result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return "", False


def check_dns_record(domain, record_type='CNAME'):
    """Verifica registro DNS"""
    if record_type == 'CNAME':
        output, success = run_command(f'dig {domain} CNAME +short')
        if success and output:
            return output.rstrip('.')
    else:  # A record
        output, success = run_command(f'dig {domain} A +short')
        if success and output:
            return output
    
    # Fallback com nslookup
    try:
        if record_type == 'CNAME':
            output, success = run_command(f'nslookup -type=CNAME {domain}')
            if 'canonical name' in output:
                for line in output.split('\n'):
                    if 'canonical name' in line:
                        return line.split('=')[-1].strip().rstrip('.')
        else:
            ip = socket.gethostbyname(domain)
            return ip
    except:
        pass
    
    return None


def check_connectivity(domain):
    """Verifica conectividade básica"""
    try:
        socket.gethostbyname(domain)
        return True
    except socket.gaierror:
        return False


def main():
    print(f"=== Verificação Rápida de Domínios - {datetime.now().strftime('%d/%m/%Y %H:%M:%S')} ===\n")
    
    domains_config = [
        {
            'name': 'www.lvksistemas.com.br',
            'type': 'CNAME',
            'expected': 'octagonal-brook-oqbuqqt97582c9psm8wscgs8.herokudns.com'
        },
        {
            'name': 'lvksistemas.com.br',
            'type': 'A',
            'expected': 'tetrahedral-goose-lm4se1i5s96qkuaqu2fz67jz.herokudns.com'
        }
    ]
    
    all_ok = True
    
    for domain_info in domains_config:
        domain = domain_info['name']
        record_type = domain_info['type']
        expected = domain_info['expected']
        
        print(f"--- {domain} ---")
        
        # Verificar DNS
        actual = check_dns_record(domain, record_type)
        if actual:
            if expected in actual or actual in expected:
                print(f"✅ DNS {record_type}: OK")
                print(f"   Target: {actual}")
            else:
                print(f"❌ DNS {record_type}: INCORRETO")
                print(f"   Esperado: {expected}")
                print(f"   Atual: {actual}")
                all_ok = False
        else:
            print(f"❌ DNS {record_type}: NÃO ENCONTRADO")
            all_ok = False
        
        # Verificar conectividade
        if check_connectivity(domain):
            print(f"✅ Conectividade: OK")
        else:
            print(f"❌ Conectividade: FALHA")
            all_ok = False
        
        print()
    
    # Verificar status Heroku se disponível
    print("--- Status Heroku ---")
    heroku_output, heroku_ok = run_command('heroku domains --app lvksistemas-app')
    if heroku_ok:
        print("✅ Heroku CLI disponível")
        if 'www.lvksistemas.com.br' in heroku_output and 'lvksistemas.com.br' in heroku_output:
            print("✅ Domínios configurados no Heroku")
        else:
            print("⚠️ Verificar configuração de domínios no Heroku")
    else:
        print("⚠️ Heroku CLI não disponível ou não logado")
    
    print("\n" + "="*50)
    if all_ok:
        print("✅ TODOS OS DOMÍNIOS ESTÃO FUNCIONANDO!")
        sys.exit(0)
    else:
        print("❌ ALGUNS DOMÍNIOS PRECISAM DE CORREÇÃO")
        print("\nPara corrigir:")
        print("1. Acesse o painel do seu provedor de DNS")
        print("2. Corrija os registros conforme mostrado acima")
        print("3. Aguarde até 24h para propagação")
        sys.exit(1)


if __name__ == '__main__':
    main()