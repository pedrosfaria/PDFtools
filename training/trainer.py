"""
Motor de treino para ensinar o programa a reconhecer faturas.

Este modulo fornece uma interface para treinar o programa
com faturas reais, permitindo que o utilizador selecione
manualmente onde estao os dados.
"""

import re
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
import logging

# Adicionar o diretorio pai ao path para imports relativos
sys.path.insert(0, str(Path(__file__).parent.parent))

from training.patterns import PatternManager, Pattern
from pdf_extractor.utils import pdf_utils, text_utils

logger = logging.getLogger(__name__)


@dataclass
class TrainingExample:
    """Exemplo de treino com uma fatura."""
    filename: str
    text: str
    provider: str
    field_annotations: Dict[str, List[Tuple[int, int, str]]]  # {field_name: [(start, end, text), ...]}
    created_at: str = field(default_factory=lambda: text_utils.format_date(text_utils.parse_date("")))
    
    def to_dict(self) -> Dict:
        return {
            "filename": self.filename,
            "provider": self.provider,
            "field_annotations": {
                field: [{"start": s, "end": e, "text": t} for s, e, t in annotations]
                for field, annotations in self.field_annotations.items()
            },
            "created_at": self.created_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'TrainingExample':
        field_annotations = {}
        for field, annotations in data.get("field_annotations", {}).items():
            field_annotations[field] = [
                (ann["start"], ann["end"], ann["text"]) for ann in annotations
            ]
        return cls(
            filename=data["filename"],
            text=data.get("text", ""),
            provider=data["provider"],
            field_annotations=field_annotations,
            created_at=data.get("created_at", "")
        )


class InvoiceTrainer:
    """
    Motor de treino para faturas.
    
    Permite:
    - Carregar faturas PDF
    - Selecionar texto manualmente
    - Associar texto a campos
    - Guardar padroes aprendidos
    - Usar padroes para extrair dados automaticamente
    """
    
    def __init__(self, patterns_file: Optional[str] = None, training_data_dir: Optional[str] = None):
        """
        Inicializar o treinador.
        
        Args:
            patterns_file: Caminho para o ficheiro de padroes
            training_data_dir: Diretorio para guardar dados de treino
        """
        self.pattern_manager = PatternManager(patterns_file)
        self.training_data_dir = Path(training_data_dir) if training_data_dir else Path("training/training_data")
        self.training_data_dir.mkdir(parents=True, exist_ok=True)
        self.current_text = ""
        self.current_filename = ""
        self.current_provider = "coopernico"
        self.current_annotations: Dict[str, List[Tuple[int, int, str]]] = {}
        
    def load_pdf(self, pdf_path: str) -> Tuple[str, str]:
        """
        Carregar um ficheiro PDF e extrair texto.
        
        Args:
            pdf_path: Caminho para o ficheiro PDF
            
        Returns:
            (texto, nome do ficheiro)
        """
        pdf_path = Path(pdf_path)
        if not pdf_path.exists():
            raise FileNotFoundError(f"Ficheiro nao encontrado: {pdf_path}")
        
        text = pdf_utils.extract_text_from_pdf(str(pdf_path))
        self.current_text = text
        self.current_filename = pdf_path.name
        
        # Tentar detetar fornecedor
        self.current_provider = self._detect_provider(text)
        
        return text, pdf_path.name
    
    def _detect_provider(self, text: str) -> str:
        """Detetar fornecedor do texto."""
        from pdf_extractor.parsers import PARSERS
        
        for provider, parser in PARSERS.items():
            if parser.detect(text):
                return provider
        
        return "coopernico"  # Default para Coopernico
    
    def get_fields(self) -> List:
        """Obter todos os campos configurados."""
        return self.pattern_manager.get_all_fields()
    
    def get_required_fields(self) -> List:
        """Obter campos obrigatorios."""
        return self.pattern_manager.get_required_fields()
    
    def add_annotation(self, field_name: str, start: int, end: int, text: str) -> bool:
        """
        Adicionar uma anotacao (selecao de texto para um campo).
        
        Args:
            field_name: Nome do campo
            start: Indice de inicio
            end: Indice de fim
            text: Texto selecionado
            
        Returns:
            True se adicionado com sucesso
        """
        if field_name not in self.current_annotations:
            self.current_annotations[field_name] = []
        
        self.current_annotations[field_name].append((start, end, text))
        return True
    
    def remove_annotation(self, field_name: str, index: int) -> bool:
        """Remover uma anotacao."""
        if field_name in self.current_annotations and 0 <= index < len(self.current_annotations[field_name]):
            del self.current_annotations[field_name][index]
            if not self.current_annotations[field_name]:
                del self.current_annotations[field_name]
            return True
        return False
    
    def clear_annotations(self):
        """Limpar todas as anotacoes."""
        self.current_annotations = {}
    
    def learn_from_annotations(self) -> Dict[str, Pattern]:
        """
        Aprender padroes a partir das anotacoes atuais.
        
        Returns:
            Dicionario com os padroes criados {field_name: pattern}
        """
        learned_patterns = {}
        
        for field_name, annotations in self.current_annotations.items():
            for start, end, text in annotations:
                pattern = self.pattern_manager.learn_from_position(
                    self.current_text, field_name, start, end, self.current_provider
                )
                learned_patterns[field_name] = pattern
        
        # Guardar padroes
        self.pattern_manager._save_patterns()
        
        return learned_patterns
    
    def save_training_example(self) -> TrainingExample:
        """
        Guardar o exemplo de treino atual.
        
        Returns:
            Exemplo de treino guardado
        """
        example = TrainingExample(
            filename=self.current_filename,
            text=self.current_text,
            provider=self.current_provider,
            field_annotations=self.current_annotations
        )
        
        # Guardar em ficheiro
        example_path = self.training_data_dir / f"{self.current_filename}.json"
        with open(example_path, 'w', encoding='utf-8') as f:
            json.dump(example.to_dict(), f, indent=2, ensure_ascii=False)
        
        logger.info(f"Exemplo de treino guardado: {example_path}")
        
        return example
    
    def load_training_example(self, filename: str) -> Optional[TrainingExample]:
        """
        Carregar um exemplo de treino.
        
        Args:
            filename: Nome do ficheiro do exemplo
            
        Returns:
            Exemplo de treino ou None
        """
        example_path = self.training_data_dir / f"{filename}.json"
        
        if not example_path.exists():
            return None
        
        with open(example_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        example = TrainingExample.from_dict(data)
        self.current_text = example.text
        self.current_filename = example.filename
        self.current_provider = example.provider
        self.current_annotations = example.field_annotations
        
        return example
    
    def get_training_examples(self) -> List[TrainingExample]:
        """Obter todos os exemplos de treino guardados."""
        examples = []
        
        for json_file in self.training_data_dir.glob("*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                example = TrainingExample.from_dict(data)
                examples.append(example)
            except Exception as e:
                logger.error(f"Erro a carregar exemplo {json_file}: {e}")
        
        return examples
    
    def extract_with_learned_patterns(self, text: str, provider: str = None) -> Dict[str, Any]:
        """
        Extrair dados usando os padroes aprendidos.
        
        Args:
            text: Texto a analisar
            provider: Fornecedor (opcional)
            
        Returns:
            Dicionario com os dados extraidos
        """
        if provider is None:
            provider = self._detect_provider(text)
        
        return self.pattern_manager.extract_all_fields(text, provider)
    
    def train_from_text(self, text: str, field_values: Dict[str, str], provider: str = "coopernico") -> Dict[str, Pattern]:
        """
        Treinar a partir de texto e valores conhecidos.
        
        Args:
            text: Texto da fatura
            field_values: Dicionario com {field_name: value}
            provider: Fornecedor
            
        Returns:
            Dicionario com os padroes criados
        """
        self.current_text = text
        self.current_provider = provider
        self.current_annotations = {}
        
        learned_patterns = {}
        
        for field_name, value in field_values.items():
            if not value:
                continue
            
            # Encontrar a posicao do valor no texto
            start = text.find(value)
            if start != -1:
                end = start + len(value)
                self.current_annotations[field_name] = [(start, end, value)]
                
                pattern = self.pattern_manager.learn_from_position(
                    text, field_name, start, end, provider
                )
                learned_patterns[field_name] = pattern
        
        # Guardar padroes
        self.pattern_manager._save_patterns()
        
        return learned_patterns
    
    def get_text_with_highlights(self, field_name: str = None) -> str:
        """
        Obter texto com destaque das anotacoes.
        
        Args:
            field_name: Campo especifico a destacar (ou None para todos)
            
        Returns:
            HTML com texto e destaques
        """
        if not self.current_text:
            return "<p>Nenhum texto carregado</p>"
        
        # Dividir texto em linhas
        lines = self.current_text.split('\n')
        
        html_lines = []
        for line in lines:
            html_line = line
            
            # Aplicar destaques
            for ann_field, annotations in self.current_annotations.items():
                if field_name and ann_field != field_name:
                    continue
                
                for start, end, text in annotations:
                    # Encontrar a posicao na linha
                    line_start = 0
                    while True:
                        pos = self.current_text.find(line, line_start)
                        if pos == -1:
                            break
                        
                        # Verificar se a anotacao esta nesta linha
                        if start >= pos and end <= pos + len(line):
                            # Posicao relativa na linha
                            rel_start = start - pos
                            rel_end = end - pos
                            
                            # Aplicar destaque
                            before = line[:rel_start]
                            selected = line[rel_start:rel_end]
                            after = line[rel_end:]
                            
                            # Cor com base no campo
                            color = self._get_field_color(ann_field)
                            
                            # Criar o span com destaque
                            highlight_span = (f"<span class='highlight' style='background-color: {color}; "
                                           f"padding: 2px 4px; border-radius: 3px;' "
                                           f"data-field='{ann_field}' data-start='{start}' data-end='{end}'>"
                                           f"{selected}</span>")
                            
                            line = f"{before}{highlight_span}{after}"
                        
                        line_start = pos + 1
            
            html_lines.append(f"<div style='white-space: pre-wrap; margin-bottom: 5px;'>{line}</div>")
        
        return '\n'.join(html_lines)
    
    def _get_field_color(self, field_name: str) -> str:
        """Obter cor para um campo."""
        colors = {
            "invoice_number": "#FFD700",  # Amarelo
            "issue_date": "#87CEFA",      # Azul claro
            "due_date": "#87CEFA",        # Azul claro
            "consumption_kwh": "#98FB98", # Verde claro
            "total_amount": "#F08080",    # Vermelho claro
            "client_name": "#DDA0DD",     # Roxo claro
            "nif": "#FFA07A",            # Laranja claro
        }
        return colors.get(field_name, "#FFFF99")  # Amarelo claro
    
    def get_field_suggestions(self, text: str, field_name: str) -> List[Dict]:
        """
        Obter sugestoes de onde pode estar um campo no texto.
        
        Args:
            text: Texto a analisar
            field_name: Nome do campo
            
        Returns:
            Lista de sugestoes com posicao e confianca
        """
        suggestions = []
        field = self.pattern_manager.get_field(field_name)
        
        if not field or not field.patterns:
            return suggestions
        
        for i, pattern in enumerate(field.patterns):
            if pattern.provider != self.current_provider:
                continue
                
            try:
                if pattern.pattern_type == "regex":
                    for match in re.finditer(pattern.pattern, text, re.IGNORECASE):
                        start, end = match.span()
                        value = match.group(1) if match.groups() else match.group(0)
                        suggestions.append({
                            "start": start,
                            "end": end,
                            "text": value,
                            "pattern_index": i,
                            "confidence": pattern.confidence,
                            "pattern": pattern.pattern
                        })
                elif pattern.pattern_type == "between":
                    if pattern.context_before and pattern.context_after:
                        start = text.find(pattern.context_before)
                        if start != -1:
                            start += len(pattern.context_before)
                            end = text.find(pattern.context_after, start)
                            if end != -1:
                                value = text[start:end].strip()
                                suggestions.append({
                                    "start": start,
                                    "end": end,
                                    "text": value,
                                    "pattern_index": i,
                                    "confidence": pattern.confidence,
                                    "pattern": f"Entre '{pattern.context_before}' e '{pattern.context_after}'"
                                })
            except Exception as e:
                logger.debug(f"Erro a aplicar padrao: {e}")
                continue
        
        return suggestions
