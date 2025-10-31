"""
Managers personalizados para garantir isolamento de dados por loja
"""
import logging
import threading
from django.db import models
from django.core.exceptions import PermissionDenied

logger = logging.getLogger(__name__)


class LojaIsoladaManager(models.Manager):
    """
    Manager que garante isolamento automático por loja
    """
    
    def get_queryset(self):
        """
        Retorna QuerySet filtrado pela loja atual do contexto
        """
        queryset = super().get_queryset()
        
        try:
            # Verificar se está em contexto de super admin
            if self._is_super_admin_context():
                logger.debug(f"Super admin context - retornando todos os dados para {self.model.__name__}")
                return queryset
            
            # Obter loja atual do contexto
            current_loja = self._get_current_loja()
            
            if current_loja:
                # Filtrar pela loja atual
                filtered_queryset = queryset.filter(loja=current_loja)
                logger.debug(f"Dados filtrados por loja {current_loja.nome} para {self.model.__name__}")
                return filtered_queryset
            else:
                # Se não há loja no contexto, não retornar nenhum dado
                logger.warning(f"Nenhuma loja no contexto - retornando QuerySet vazio para {self.model.__name__}")
                return queryset.none()
                
        except Exception as e:
            logger.error(f"Erro no manager isolado para {self.model.__name__}: {str(e)}")
            # Em caso de erro, retornar QuerySet vazio por segurança
            return queryset.none()
    
    def _get_current_loja(self):
        """Obtém a loja atual do contexto da thread"""
        
        try:
            thread = threading.current_thread()
            
            # Tentar diferentes formas de obter a loja do contexto
            
            # Método 1: isolation_context
            if hasattr(thread, 'isolation_context') and hasattr(thread.isolation_context, 'loja'):
                loja = thread.isolation_context.loja
                if loja:
                    return loja
            
            # Método 2: loja_atual
            if hasattr(thread, 'loja_atual'):
                return thread.loja_atual
            
            # Método 3: loja_context
            if hasattr(thread, 'loja_context') and hasattr(thread.loja_context, 'loja_id'):
                loja_id = thread.loja_context.loja_id
                if loja_id:
                    from lojas.models import Loja
                    return Loja.objects.get(id=loja_id)
            
            # Método 4: loja_id direto
            if hasattr(thread, 'loja_id'):
                loja_id = thread.loja_id
                if loja_id:
                    from lojas.models import Loja
                    return Loja.objects.get(id=loja_id)
            
            return None
            
        except Exception as e:
            logger.error(f"Erro ao obter loja atual do contexto: {str(e)}")
            return None
    
    def _is_super_admin_context(self):
        """Verifica se está em contexto de super admin"""
        
        try:
            thread = threading.current_thread()
            
            # Verificar isolation_context
            if hasattr(thread, 'isolation_context'):
                return getattr(thread.isolation_context, 'is_super_admin', False)
            
            return False
            
        except Exception:
            return False
    
    def create(self, **kwargs):
        """
        Cria um novo objeto garantindo que seja associado à loja atual
        """
        try:
            # Se não está em contexto de super admin, definir loja automaticamente
            if not self._is_super_admin_context():
                current_loja = self._get_current_loja()
                
                if current_loja and 'loja' not in kwargs:
                    kwargs['loja'] = current_loja
                    logger.debug(f"Loja {current_loja.nome} definida automaticamente para novo {self.model.__name__}")
                elif not current_loja and 'loja' not in kwargs:
                    raise PermissionDenied("Não é possível criar objeto sem contexto de loja")
            
            return super().create(**kwargs)
            
        except Exception as e:
            logger.error(f"Erro ao criar {self.model.__name__}: {str(e)}")
            raise
    
    def bulk_create(self, objs, **kwargs):
        """
        Cria múltiplos objetos garantindo isolamento por loja
        """
        try:
            # Se não está em contexto de super admin, definir loja para todos os objetos
            if not self._is_super_admin_context():
                current_loja = self._get_current_loja()
                
                if current_loja:
                    for obj in objs:
                        if not hasattr(obj, 'loja') or obj.loja is None:
                            obj.loja = current_loja
                    logger.debug(f"Loja {current_loja.nome} definida para {len(objs)} objetos {self.model.__name__}")
                elif not current_loja:
                    raise PermissionDenied("Não é possível criar objetos sem contexto de loja")
            
            return super().bulk_create(objs, **kwargs)
            
        except Exception as e:
            logger.error(f"Erro ao criar múltiplos {self.model.__name__}: {str(e)}")
            raise


class LojaIsoladaRelacionadaManager(models.Manager):
    """
    Manager para modelos que se relacionam com outros modelos isolados por loja
    (ex: HistoricoContato que se relaciona com Lead)
    """
    
    def get_queryset(self):
        """
        Retorna QuerySet filtrado pela loja através de relacionamento
        """
        queryset = super().get_queryset()
        
        try:
            # Verificar se está em contexto de super admin
            if self._is_super_admin_context():
                return queryset
            
            # Obter loja atual do contexto
            current_loja = self._get_current_loja()
            
            if current_loja:
                # Filtrar através do relacionamento (deve ser customizado por modelo)
                return self._filter_by_loja_relationship(queryset, current_loja)
            else:
                # Se não há loja no contexto, não retornar nenhum dado
                return queryset.none()
                
        except Exception as e:
            logger.error(f"Erro no manager relacionado para {self.model.__name__}: {str(e)}")
            return queryset.none()
    
    def _filter_by_loja_relationship(self, queryset, loja):
        """
        Filtra QuerySet pela loja através de relacionamento
        Deve ser sobrescrito em subclasses
        """
        # Implementação padrão - assumir que há campo 'loja'
        if hasattr(self.model, 'loja'):
            return queryset.filter(loja=loja)
        
        # Se não há campo loja direto, retornar todos (deve ser customizado)
        logger.warning(f"Modelo {self.model.__name__} não tem campo loja - implementar _filter_by_loja_relationship")
        return queryset
    
    def _get_current_loja(self):
        """Obtém a loja atual do contexto da thread"""
        
        try:
            thread = threading.current_thread()
            
            if hasattr(thread, 'isolation_context') and hasattr(thread.isolation_context, 'loja'):
                return thread.isolation_context.loja
            
            if hasattr(thread, 'loja_atual'):
                return thread.loja_atual
            
            return None
            
        except Exception as e:
            logger.error(f"Erro ao obter loja atual: {str(e)}")
            return None
    
    def _is_super_admin_context(self):
        """Verifica se está em contexto de super admin"""
        
        try:
            thread = threading.current_thread()
            
            if hasattr(thread, 'isolation_context'):
                return getattr(thread.isolation_context, 'is_super_admin', False)
            
            return False
            
        except Exception:
            return False


class HistoricoContatoManager(LojaIsoladaRelacionadaManager):
    """
    Manager específico para HistoricoContato
    """
    
    def _filter_by_loja_relationship(self, queryset, loja):
        """
        Filtra HistoricoContato pela loja do Lead relacionado
        """
        return queryset.filter(lead__loja=loja)


class ItemOrcamentoManager(LojaIsoladaRelacionadaManager):
    """
    Manager específico para ItemOrcamento
    """
    
    def _filter_by_loja_relationship(self, queryset, loja):
        """
        Filtra ItemOrcamento pela loja do Orcamento relacionado
        """
        return queryset.filter(orcamento__loja=loja)


class AssinaturaDigitalManager(LojaIsoladaRelacionadaManager):
    """
    Manager específico para AssinaturaDigital
    """
    
    def _filter_by_loja_relationship(self, queryset, loja):
        """
        Filtra AssinaturaDigital pela loja através dos relacionamentos
        """
        # AssinaturaDigital pode estar relacionada a Proposta ou Contrato
        from django.db.models import Q
        
        return queryset.filter(
            Q(proposta__loja=loja) | Q(contrato__loja=loja)
        )