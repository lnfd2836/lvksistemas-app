"""
Gerador de senhas seguras para o sistema de credenciais
"""
import secrets
import string
import re
from typing import Optional


class PasswordGenerator:
    """Utilitário para geração de senhas seguras"""
    
    # Caracteres permitidos para senhas
    LOWERCASE = string.ascii_lowercase
    UPPERCASE = string.ascii_uppercase
    DIGITS = string.digits
    SPECIAL_CHARS = "!@#$%&*"
    
    # Palavras comuns que devem ser evitadas
    COMMON_WORDS = [
        'password', 'senha', '123456', 'qwerty', 'admin', 'user',
        'login', 'sistema', 'loja', 'fatesa', 'lvk'
    ]
    
    @classmethod
    def generate_secure_password(cls, length: int = 12, include_special: bool = False) -> str:
        """
        Gera uma senha segura com critérios específicos
        
        Args:
            length: Comprimento da senha (mínimo 12)
            include_special: Se deve incluir caracteres especiais
            
        Returns:
            str: Senha gerada
            
        Raises:
            ValueError: Se o comprimento for menor que 12
        """
        if length < 12:
            raise ValueError("Senha deve ter pelo menos 12 caracteres")
        
        # Definir conjunto de caracteres
        chars = cls.LOWERCASE + cls.UPPERCASE + cls.DIGITS
        if include_special:
            chars += cls.SPECIAL_CHARS
        
        # Gerar senha até encontrar uma válida
        max_attempts = 100
        for _ in range(max_attempts):
            password = ''.join(secrets.choice(chars) for _ in range(length))
            
            if cls.is_password_strong(password, include_special):
                return password
        
        # Fallback: construir senha garantindo critérios
        return cls._build_guaranteed_password(length, include_special)
    
    @classmethod
    def is_password_strong(cls, password: str, require_special: bool = False) -> bool:
        """
        Valida se a senha atende aos critérios de segurança
        
        Args:
            password: Senha a ser validada
            require_special: Se caracteres especiais são obrigatórios
            
        Returns:
            bool: True se a senha é forte
        """
        if len(password) < 12:
            return False
        
        # Verificar presença de diferentes tipos de caracteres
        has_lower = any(c in cls.LOWERCASE for c in password)
        has_upper = any(c in cls.UPPERCASE for c in password)
        has_digit = any(c in cls.DIGITS for c in password)
        has_special = any(c in cls.SPECIAL_CHARS for c in password)
        
        # Critérios básicos
        if not (has_lower and has_upper and has_digit):
            return False
        
        # Caracteres especiais se requeridos
        if require_special and not has_special:
            return False
        
        # Verificar se não contém palavras comuns
        password_lower = password.lower()
        for word in cls.COMMON_WORDS:
            if word in password_lower:
                return False
        
        # Verificar se não tem sequências repetitivas
        if cls._has_repetitive_patterns(password):
            return False
        
        return True
    
    @classmethod
    def _build_guaranteed_password(cls, length: int, include_special: bool) -> str:
        """
        Constrói uma senha garantindo todos os critérios
        """
        password_parts = []
        
        # Garantir pelo menos um de cada tipo
        password_parts.append(secrets.choice(cls.LOWERCASE))
        password_parts.append(secrets.choice(cls.UPPERCASE))
        password_parts.append(secrets.choice(cls.DIGITS))
        
        if include_special:
            password_parts.append(secrets.choice(cls.SPECIAL_CHARS))
        
        # Preencher o restante
        remaining_length = length - len(password_parts)
        chars = cls.LOWERCASE + cls.UPPERCASE + cls.DIGITS
        if include_special:
            chars += cls.SPECIAL_CHARS
        
        for _ in range(remaining_length):
            password_parts.append(secrets.choice(chars))
        
        # Embaralhar para evitar padrões previsíveis
        secrets.SystemRandom().shuffle(password_parts)
        
        return ''.join(password_parts)
    
    @classmethod
    def _has_repetitive_patterns(cls, password: str) -> bool:
        """
        Verifica se a senha tem padrões repetitivos
        """
        # Verificar sequências de 3+ caracteres iguais
        if re.search(r'(.)\1{2,}', password):
            return True
        
        # Verificar sequências numéricas simples
        if re.search(r'(012|123|234|345|456|567|678|789|890)', password):
            return True
        
        # Verificar sequências alfabéticas simples
        if re.search(r'(abc|bcd|cde|def|efg|fgh|ghi|hij|ijk|jkl|klm|lmn|mno|nop|opq|pqr|qrs|rst|stu|tuv|uvw|vwx|wxy|xyz)', password.lower()):
            return True
        
        return False
    
    @classmethod
    def generate_multiple_passwords(cls, count: int = 5, length: int = 12) -> list[str]:
        """
        Gera múltiplas senhas para escolha
        
        Args:
            count: Número de senhas a gerar
            length: Comprimento das senhas
            
        Returns:
            list: Lista de senhas geradas
        """
        passwords = []
        for _ in range(count):
            password = cls.generate_secure_password(length)
            passwords.append(password)
        
        return passwords
    
    @classmethod
    def estimate_strength(cls, password: str) -> dict:
        """
        Estima a força da senha e retorna detalhes
        
        Args:
            password: Senha a ser analisada
            
        Returns:
            dict: Informações sobre a força da senha
        """
        result = {
            'length': len(password),
            'has_lowercase': any(c in cls.LOWERCASE for c in password),
            'has_uppercase': any(c in cls.UPPERCASE for c in password),
            'has_digits': any(c in cls.DIGITS for c in password),
            'has_special': any(c in cls.SPECIAL_CHARS for c in password),
            'has_common_words': any(word in password.lower() for word in cls.COMMON_WORDS),
            'has_repetitive': cls._has_repetitive_patterns(password),
            'score': 0,
            'strength': 'Muito Fraca'
        }
        
        # Calcular score
        if result['length'] >= 12:
            result['score'] += 2
        elif result['length'] >= 8:
            result['score'] += 1
        
        if result['has_lowercase']:
            result['score'] += 1
        if result['has_uppercase']:
            result['score'] += 1
        if result['has_digits']:
            result['score'] += 1
        if result['has_special']:
            result['score'] += 1
        
        if result['has_common_words']:
            result['score'] -= 2
        if result['has_repetitive']:
            result['score'] -= 1
        
        # Determinar força
        if result['score'] >= 6:
            result['strength'] = 'Muito Forte'
        elif result['score'] >= 5:
            result['strength'] = 'Forte'
        elif result['score'] >= 4:
            result['strength'] = 'Boa'
        elif result['score'] >= 3:
            result['strength'] = 'Regular'
        elif result['score'] >= 2:
            result['strength'] = 'Fraca'
        else:
            result['strength'] = 'Muito Fraca'
        
        return result