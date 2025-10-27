"""
Service para gerenciar configurações com cache otimizado
"""
from django.core.cache import cache
from django.db import models
from typing import Dict, Any, Optional
import json
import logging

logger = logging.getLogger(__name__)


class ConfiguracaoService:
    """
    Service para gerenciar configurações de loja com cache inteligente
    """
    
    # Cache por 2 horas para configurações que mudam pouco
    CACHE_TIMEOUT = 7200
    
    @classmethod
    def get_all_configs(cls, loja_id: str) -> Dict[str, Any]:
        """
        Obtém todas as configurações de uma loja de uma vez
        Otimizado para reduzir consultas ao banco
        """
        cache_key = f"all_configs_{loja_id}"
        configs = cache.get(cache_key)
        
        if configs is None:
            configs = cls._load_all_configs(loja_id)
            cache.set(cache_key, configs, cls.CACHE_TIMEOUT)
            logger.info(f"Configurações carregadas do banco para loja {loja_id}")
        else:
            logger.info(f"Configurações carregadas do cache para loja {loja_id}")
        
        return configs
    
    @classmethod
    def _load_all_configs(cls, loja_id: str) -> Dict[str, Any]:
        """Carrega todas as configurações do banco de uma vez"""
        from ..models_configuracoes import (
            ConfiguracaoProduto, ConfiguracaoCliente,
            ConfiguracaoVenda, ConfiguracaoDashboard
        )
        from ..models import Loja
        
        try:
            loja = Loja.objects.get(id=loja_id)
            
            configs = {
                'produto': cls._get_or_create_config(ConfiguracaoProduto, loja),
                'cliente': cls._get_or_create_config(ConfiguracaoCliente, loja),
                'venda': cls._get_or_create_config(ConfiguracaoVenda, loja),
                'dashboard': cls._get_or_create_config(ConfiguracaoDashboard, loja),
                'loja_info': {
                    'id': str(loja.id),
                    'nome': loja.nome,
                    'tipo': loja.tipo_loja.nome if loja.tipo_loja else 'padrao'
                }
            }
            
            return configs
            
        except Exception as e:
            logger.error(f"Erro ao carregar configurações da loja {loja_id}: {e}")
            return {}
    
    @classmethod
    def _get_or_create_config(cls, model_class, loja):
        """Obtém ou cria configuração padrão"""
        try:
            config = model_class.objects.get(loja=loja)
            return cls._serialize_config(config)
        except model_class.DoesNotExist:
            config = model_class.objects.create(loja=loja)
            return cls._serialize_config(config)
    
    @classmethod
    def _serialize_config(cls, config) -> Dict[str, Any]:
        """Serializa configuração para cache"""
        data = {}
        for field in config._meta.fields:
            if field.name not in ['id', 'loja']:
                value = getattr(config, field.name)
                if isinstance(value, models.Model):
                    continue
                data[field.name] = value
        return data
    
    @classmethod
    def update_config(cls, loja_id: str, config_type: str, data: Dict[str, Any]) -> bool:
        """
        Atualiza configuração específica e limpa cache
        """
        try:
            model_map = {
                'produto': 'ConfiguracaoProduto',
                'cliente': 'ConfiguracaoCliente', 
                'venda': 'ConfiguracaoVenda',
                'dashboard': 'ConfiguracaoDashboard'
            }
            
            if config_type not in model_map:
                return False
            
            # Atualizar no banco
            cls._update_database_config(loja_id, config_type, data)
            
            # Limpar cache
            cls.clear_cache(loja_id)
            
            logger.info(f"Configuração {config_type} atualizada para loja {loja_id}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao atualizar configuração {config_type} da loja {loja_id}: {e}")
            return False
    
    @classmethod
    def _update_database_config(cls, loja_id: str, config_type: str, data: Dict[str, Any]):
        """Atualiza configuração no banco de dados"""
        from ..models_configuracoes import (
            ConfiguracaoProduto, ConfiguracaoCliente,
            ConfiguracaoVenda, ConfiguracaoDashboard
        )
        from ..models import Loja
        
        model_map = {
            'produto': ConfiguracaoProduto,
            'cliente': ConfiguracaoCliente,
            'venda': ConfiguracaoVenda,
            'dashboard': ConfiguracaoDashboard
        }
        
        loja = Loja.objects.get(id=loja_id)
        model_class = model_map[config_type]
        
        config, created = model_class.objects.get_or_create(loja=loja)
        
        # Atualizar campos
        for key, value in data.items():
            if hasattr(config, key):
                setattr(config, key, value)
        
        config.save()
    
    @classmethod
    def clear_cache(cls, loja_id: str):
        """Limpa cache de uma loja específica"""
        cache_keys = [
            f"all_configs_{loja_id}",
            f"configuracaoproduto_{loja_id}",
            f"configuracaocliente_{loja_id}",
            f"configuracaovenda_{loja_id}",
            f"configuracaodashboard_{loja_id}",
        ]
        
        cache.delete_many(cache_keys)
        logger.info(f"Cache limpo para loja {loja_id}")
    
    @classmethod
    def warm_cache(cls, loja_id: str):
        """Pré-carrega cache para uma loja"""
        cls.get_all_configs(loja_id)
        logger.info(f"Cache pré-carregado para loja {loja_id}")
    
    @classmethod
    def get_config_summary(cls, loja_id: str) -> Dict[str, Any]:
        """
        Obtém resumo das configurações (versão leve)
        """
        cache_key = f"config_summary_{loja_id}"
        summary = cache.get(cache_key)
        
        if summary is None:
            configs = cls.get_all_configs(loja_id)
            summary = {
                'loja_nome': configs.get('loja_info', {}).get('nome', ''),
                'loja_tipo': configs.get('loja_info', {}).get('tipo', 'padrao'),
                'tem_configuracoes': bool(configs.get('produto') or configs.get('cliente')),
                'ultima_atualizacao': configs.get('produto', {}).get('data_atualizacao'),
            }
            cache.set(cache_key, summary, cls.CACHE_TIMEOUT)
        
        return summary


class ConfiguracaoTipoLojaService:
    """
    Service para configurações específicas por tipo de loja
    """
    
    @classmethod
    def get_config_by_type(cls, loja_id: str, tipo_loja: str) -> Optional[Dict[str, Any]]:
        """
        Obtém configuração específica baseada no tipo da loja
        """
        cache_key = f"config_tipo_{tipo_loja}_{loja_id}"
        config = cache.get(cache_key)
        
        if config is None:
            config = cls._load_type_specific_config(loja_id, tipo_loja)
            if config:
                cache.set(cache_key, config, 3600)  # Cache por 1 hora
        
        return config
    
    @classmethod
    def _load_type_specific_config(cls, loja_id: str, tipo_loja: str) -> Optional[Dict[str, Any]]:
        """Carrega configuração específica do tipo de loja"""
        
        # Mapeamento de tipos para models (quando implementados)
        type_models = {
            'lanchonete': 'ConfiguracaoLanchonete',
            'clinica_estetica': 'ConfiguracaoClinicaEstetica', 
            'loja_roupas': 'ConfiguracaoLojaRoupas',
            'supermercado': 'ConfiguracaoSupermercado'
        }
        
        if tipo_loja not in type_models:
            return None
        
        # Por enquanto retorna configuração padrão
        # Quando os models específicos forem implementados, 
        # esta função carregará do banco
        return cls._get_default_config_by_type(tipo_loja)
    
    @classmethod
    def _get_default_config_by_type(cls, tipo_loja: str) -> Dict[str, Any]:
        """Retorna configuração padrão por tipo de loja"""
        
        defaults = {
            'lanchonete': {
                'categorias_cardapio': ['Lanches', 'Bebidas', 'Sobremesas'],
                'usa_comandas': True,
                'faz_delivery': True,
                'tempo_preparo_medio': 30
            },
            'clinica_estetica': {
                'tipos_procedimentos': ['Limpeza de Pele', 'Massagem'],
                'intervalo_agendamento': 30,
                'usa_anamnese': True,
                'faz_followup': True
            },
            'loja_roupas': {
                'grades_tamanho': {'feminino': ['PP', 'P', 'M', 'G', 'GG']},
                'usa_colecoes': True,
                'prazo_troca': 30,
                'numero_provadores': 3
            },
            'supermercado': {
                'secoes_loja': ['Açougue', 'Padaria', 'Hortifruti'],
                'controla_validade': True,
                'produtos_por_peso': True,
                'cobra_sacola': True
            }
        }
        
        return defaults.get(tipo_loja, {})
