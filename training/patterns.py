"""
Gestor de padrões aprendidos para extração de faturas.

Este módulo guarda e gere os padrões que o programa aprende
através do treino com faturas reais.
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class Pattern:
    """Representa um padrão aprendido para extrair um campo."""
    field_name: str  # Nome do campo (ex: "invoice_number")
    pattern: str  # Expressão regular ou texto a procurar
    pattern_type: str = "regex"  # "regex", "contains", "starts_with", "ends_with", "between"
    context_before: Optional[str] = None  # Texto que aparece antes
    context_after: Optional[str] = None  # Texto que aparece depois
    provider: str = "coopernico"  # Fornecedor (ex: "coopernico")
    confidence: float = 1.0  # Confiança (0-1)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    examples: List[str] = field(default_factory=list)  # Exemplos de texto que matcham
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Pattern':
        return cls(**data)


@dataclass
class FieldConfig:
    """Configuração de um campo (que padrões usar, prioridade, etc.)."""
    field_name: str
    display_name: str  # Nome para mostrar ao utilizador
    data_type: str = "string"  # "string", "number", "date", "amount"
    required: bool = False
    patterns: List[Pattern] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            "field_name": self.field_name,
            "display_name": self.display_name,
            "data_type": self.data_type,
            "required": self.required,
            "patterns": [p.to_dict() for p in self.patterns]
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'FieldConfig':
        return cls(
            field_name=data["field_name"],
            display_name=data["display_name"],
            data_type=data.get("data_type", "string"),
            required=data.get("required", False),
            patterns=[Pattern.from_dict(p) for p in data.get("patterns", [])]
        )


class PatternManager:
    """
    Gestor de padrões aprendidos.
    
    Guarda e gere todos os padrões que o programa aprende
    através do treino com faturas reais.
    """
    
    DEFAULT_PATTERNS_FILE = Path("training/patterns.json")
    
    # Campos padrão para faturas de eletricidade
    STANDARD_FIELDS = [
        {"field_name": "invoice_number", "display_name": "Nº Fatura", "data_type": "string", "required": True},
        {"field_name": "issue_date", "display_name": "Data Emissão", "data_type": "date", "required": True},
        {"field_name": "due_date", "display_name": "Data Vencimento", "data_type": "date", "required": True},
        {"field_name": "consumption_period_start", "display_name": "Início Período", "data_type": "date"},
        {"field_name": "consumption_period_end", "display_name": "Fim Período", "data_type": "date"},
        {"field_name": "consumption_kwh", "display_name": "Consumo (kWh)", "data_type": "number", "required": True},
        {"field_name": "power_contracted_kva", "display_name": "Potência (kVA)", "data_type": "number"},
        {"field_name": "price_per_kwh", "display_name": "Preço/kWh (€)", "data_type": "amount"},
        {"field_name": "energy_cost", "display_name": "Custo Energia (€)", "data_type": "amount"},
        {"field_name": "network_cost", "display_name": "Custo Rede (€)", "data_type": "amount"},
        {"field_name": "iva_rate", "display_name": "Taxa IVA (%)", "data_type": "number"},
        {"field_name": "iva_value", "display_name": "Valor IVA (€)", "data_type": "amount"},
        {"field_name": "total_amount", "display_name": "Total a Pagar (€)", "data_type": "amount", "required": True},
        {"field_name": "client_number", "display_name": "Nº Cliente", "data_type": "string"},
        {"field_name": "nif", "display_name": "NIF", "data_type": "string", "required": True},
        {"field_name": "client_name", "display_name": "Nome Cliente", "data_type": "string", "required": True},
        {"field_name": "address", "display_name": "Morada", "data_type": "string"},
        {"field_name": "postal_code", "display_name": "Código Postal", "data_type": "string"},
        {"field_name": "city", "display_name": "Localidade", "data_type": "string"},
        {"field_name": "payment_method", "display_name": "Método Pagamento", "data_type": "string"},
        {"field_name": "payment_reference", "display_name": "Referência Pagamento", "data_type": "string"},
        {"field_name": "meter_number", "display_name": "Nº Contador", "data_type": "string"},
        {"field_name": "current_reading", "display_name": "Leitura Atual", "data_type": "number"},
        {"field_name": "previous_reading", "display_name": "Leitura Anterior", "data_type": "number"},
        {"field_name": "reading_date", "display_name": "Data Leitura", "data_type": "date"},
    ]
    
    def __init__(self, patterns_file: Optional[str] = None):
        """
        Inicializar o gestor de padrões.
        
        Args:
            patterns_file: Caminho para o ficheiro JSON com os padrões
        """
        self.patterns_file = Path(patterns_file) if patterns_file else self.DEFAULT_PATTERNS_FILE
        self.fields: Dict[str, FieldConfig] = {}
        self._load_default_fields()
        self._load_patterns()
        
    def _load_default_fields(self):
        """Carregar os campos padrão."""
        for field_data in self.STANDARD_FIELDS:
            field = FieldConfig.from_dict(field_data)
            self.fields[field.field_name] = field
            
    def _load_patterns(self):
        """Carregar padrões do ficheiro JSON."""
        if self.patterns_file.exists():
            try:
                with open(self.patterns_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for field_name, field_data in data.get("fields", {}).items():
                        if field_name in self.fields:
                            self.fields[field_name] = FieldConfig.from_dict(field_data)
                        else:
                            self.fields[field_name] = FieldConfig.from_dict(field_data)
                logger.info(f"Carregados {len(data.get('fields', {}))} campos do ficheiro {self.patterns_file}")
            except Exception as e:
                logger.error(f"Erro a carregar padrões: {e}")
        else:
            logger.info(f"Ficheiro de padrões não encontrado: {self.patterns_file}")
            self._save_patterns()  # Criar ficheiro com campos padrão
            
    def _save_patterns(self):
        """Guardar padrões no ficheiro JSON."""
        try:
            self.patterns_file.parent.mkdir(parents=True, exist_ok=True)
            data = {
                "version": "1.0",
                "last_updated": datetime.now().isoformat(),
                "fields": {field_name: field.to_dict() for field_name, field in self.fields.items()}
            }
            with open(self.patterns_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.info(f"Padrões guardados em {self.patterns_file}")
        except Exception as e:
            logger.error(f"Erro a guardar padrões: {e}")
            
    def get_field(self, field_name: str) -> Optional[FieldConfig]:
        """Obter configuração de um campo."""
        return self.fields.get(field_name)
    
    def get_all_fields(self) -> List[FieldConfig]:
        """Obter todos os campos."""
        return list(self.fields.values())
    
    def get_required_fields(self) -> List[FieldConfig]:
        """Obter campos obrigatórios."""
        return [field for field in self.fields.values() if field.required]
    
    def add_pattern(self, field_name: str, pattern: Pattern) -> bool:
        """
        Adicionar um padrão a um campo.
        
        Args:
            field_name: Nome do campo
            pattern: Padrão a adicionar
            
        Returns:
            True se adicionado com sucesso
        """
        if field_name not in self.fields:
            # Criar campo se não existir
            self.fields[field_name] = FieldConfig(
                field_name=field_name,
                display_name=field_name.replace("_", " ").title(),
                data_type="string"
            )
        
        # Adicionar padrão
        self.fields[field_name].patterns.append(pattern)
        self._save_patterns()
        return True
    
    def remove_pattern(self, field_name: str, pattern_index: int) -> bool:
        """Remover um padrão de um campo."""
        if field_name in self.fields and 0 <= pattern_index < len(self.fields[field_name].patterns):
            del self.fields[field_name].patterns[pattern_index]
            self._save_patterns()
            return True
        return False
    
    def extract_field(self, text: str, field_name: str) -> Optional[Any]:
        """
        Extrair um campo usando os padrões aprendidos.
        
        Args:
            text: Texto a analisar
            field_name: Nome do campo
            
        Returns:
            Valor extraído ou None
        """
        field = self.get_field(field_name)
        if not field or not field.patterns:
            return None
        
        for pattern in field.patterns:
            try:
                result = self._apply_pattern(text, pattern)
                if result is not None:
                    # Processar segundo o tipo de dados
                    return self._process_value(result, field.data_type)
            except Exception as e:
                logger.debug(f"Erro a aplicar padrão para {field_name}: {e}")
                continue
        
        return None
    
    def _apply_pattern(self, text: str, pattern: Pattern) -> Optional[str]:
        """Aplicar um padrão ao texto."""
        if pattern.pattern_type == "regex":
            match = re.search(pattern.pattern, text, re.IGNORECASE)
            if match:
                return match.group(1) if match.groups() else match.group(0)
        elif pattern.pattern_type == "contains":
            # Procurar o padrao no texto
            if pattern.pattern in text:
                # Devolver o padrao completo que foi encontrado
                return pattern.pattern
        elif pattern.pattern_type == "starts_with":
            if text.startswith(pattern.pattern):
                return text[len(pattern.pattern):].strip()
        elif pattern.pattern_type == "ends_with":
            if text.endswith(pattern.pattern):
                return text[:-len(pattern.pattern)].strip()
        elif pattern.pattern_type == "between":
            if pattern.context_before and pattern.context_after:
                start = text.find(pattern.context_before)
                if start != -1:
                    start += len(pattern.context_before)
                    end = text.find(pattern.context_after, start)
                    if end != -1:
                        return text[start:end].strip()
        
        return None
    
    def _process_value(self, value: str, data_type: str) -> Any:
        """Processar valor segundo o tipo de dados."""
        if value is None:
            return None
        
        value = value.strip()
        
        if data_type == "number":
            # Remover vírgulas e converter para float
            value = value.replace(",", ".")
            try:
                return float(value)
            except ValueError:
                return None
        elif data_type == "amount":
            # Remover símbolo de euro e converter
            value = value.replace("€", "").replace(",", ".").strip()
            try:
                return float(value)
            except ValueError:
                return None
        elif data_type == "date":
            # Tentar vários formatos de data
            from ..utils.text_utils import parse_date
            return parse_date(value)
        else:
            return value
    
    def extract_all_fields(self, text: str, provider: str = "coopernico") -> Dict[str, Any]:
        """
        Extrair todos os campos do texto.
        
        Args:
            text: Texto a analisar
            provider: Fornecedor (para filtrar padrões)
            
        Returns:
            Dicionário com todos os campos extraídos
        """
        result = {}
        
        for field_name, field in self.fields.items():
            # Filtrar por fornecedor se especificado
            provider_patterns = [p for p in field.patterns if p.provider == provider]
            if not provider_patterns:
                provider_patterns = field.patterns
            
            # Ordenar padrões por comprimento (maiores primeiro) para matchar os mais específicos
            provider_patterns = sorted(provider_patterns, key=lambda p: len(p.pattern), reverse=True)
            
            # Extrair usando apenas os padrões do fornecedor
            for pattern in provider_patterns:
                try:
                    result_value = self._apply_pattern(text, pattern)
                    if result_value is not None:
                        # Processar segundo o tipo de dados do campo
                        processed_value = self._process_value(result_value, field.data_type)
                        if processed_value is not None:
                            result[field_name] = processed_value
                            break  # Parar no primeiro match
                except Exception as e:
                    logger.debug(f"Erro a aplicar padrão para {field_name}: {e}")
                    continue
        
        return result
    
    def learn_from_example(self, text: str, field_name: str, selected_text: str, 
                         provider: str = "coopernico") -> Pattern:
        """
        Aprender um padrão a partir de um exemplo.
        
        Args:
            text: Texto completo
            field_name: Nome do campo
            selected_text: Texto selecionado pelo utilizador
            provider: Fornecedor
            
        Returns:
            Padrão criado
        """
        # Criar padrão com base no texto selecionado
        # Tentar criar uma regex simples
        pattern_str = re.escape(selected_text)
        
        # Verificar se o texto selecionado tem um padrão claro
        # Ex: "Nº Fatura: FA2024001" -> "Nº Fatura:\\s*([A-Z0-9\\-]+)"
        if ":" in selected_text:
            parts = selected_text.split(":", 1)
            if len(parts) == 2:
                label = parts[0].strip()
                value = parts[1].strip()
                # Criar padrão para capturar o valor
                pattern_str = f"{re.escape(label)}\\s*:?\\s*([A-Za-z0-9\\-\\/\\s]+)"
        
        # Criar padrão
        pattern = Pattern(
            field_name=field_name,
            pattern=pattern_str,
            pattern_type="regex",
            provider=provider,
            examples=[selected_text]
        )
        
        # Adicionar ao campo
        self.add_pattern(field_name, pattern)
        
        return pattern
    
    def learn_from_position(self, text: str, field_name: str, start: int, end: int,
                          provider: str = "coopernico") -> Pattern:
        """
        Aprender um padrão com base na posição do texto.
        
        Args:
            text: Texto completo
            field_name: Nome do campo
            start: Índice de início da seleção
            end: Índice de fim da seleção
            provider: Fornecedor
            
        Returns:
            Padrão criado
        """
        selected_text = text[start:end].strip()
        
        # Tentar encontrar contexto antes e depois
        context_before = text[max(0, start-50):start].strip()
        context_after = text[end:end+50].strip()
        
        # Criar padrão com contexto
        pattern = Pattern(
            field_name=field_name,
            pattern=re.escape(selected_text),
            pattern_type="between",
            context_before=context_before,
            context_after=context_after,
            provider=provider,
            examples=[selected_text]
        )
        
        # Adicionar ao campo
        self.add_pattern(field_name, pattern)
        
        return pattern
