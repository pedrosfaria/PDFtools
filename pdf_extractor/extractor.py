"""
Motor principal de extraao de dados de faturas de eletricidade
"""

from typing import Dict, List, Optional, Union
from pathlib import Path
import logging
import json
import csv
import pandas as pd

from .config import SUPPORTED_PROVIDERS, STANDARD_FIELDS, EXPORT_FORMATS, DEFAULT_EXPORT_FORMAT, DEFAULT_OUTPUT_DIR
from .utils import pdf_utils
from .parsers import PARSERS, BaseInvoiceParser

logger = logging.getLogger(__name__)


class PDFExtractor:
    """
    Motor principal para extraao de dados de faturas de eletricidade em PDF.
    
    Esta classe coordena todo o processo:
    1. Leitura do PDF
    2. Deteao do fornecedor
    3. Parsing com o parser adequado
    4. Extracao com padroes aprendidos (PatternManager)
    5. Validaao dos dados
    6. Exportaao para o formato desejado
    """
    
    def __init__(self, use_ocr: bool = False, output_dir: str = None):
        """
        Inicializar o extrator.
        
        Args:
            use_ocr: Se True, usa OCR para extrair texto de imagens
            output_dir: Diretrio de sada (padro: data/output)
        """
        self.use_ocr = use_ocr
        self.output_dir = Path(output_dir) if output_dir else Path(DEFAULT_OUTPUT_DIR)
        self.parsers = {}
        self.pattern_manager = None
        
        # Inicializar parsers
        self._init_parsers()
        
        # Tentar carregar PatternManager
        self._init_pattern_manager()
        
    def _init_parsers(self):
        """Inicializar todos os parsers disponveis."""
        for provider, parser_class in PARSERS.items():
            self.parsers[provider] = parser_class()
        
    def _init_pattern_manager(self):
        """Inicializar PatternManager para usar padroes aprendidos."""
        try:
            from training.patterns import PatternManager
            self.pattern_manager = PatternManager()
            logger.info("PatternManager carregado com sucesso")
        except Exception as e:
            logger.warning(f"PatternManager nao disponivel: {e}")
            self.pattern_manager = None
    
    def extract_from_pdf(self, pdf_path: str, use_ocr: bool = None) -> Dict:
        """
        Extrair dados de um ficheiro PDF.
        
        Args:
            pdf_path: Caminho para o ficheiro PDF
            use_ocr: Usar OCR (sobrepe a configuraao global)
            
        Returns:
            Dicionrio com os dados extrados
        """
        pdf_path = Path(pdf_path)
        
        if not pdf_path.exists():
            raise FileNotFoundError(f"Ficheiro no encontrado: {pdf_path}")
        
        # Extrair texto do PDF
        ocr = use_ocr if use_ocr is not None else self.use_ocr
        text = pdf_utils.extract_text_from_pdf(str(pdf_path), use_ocr=ocr)
        
        if not text or not text.strip():
            raise ValueError(f"No foi possvel extrair texto do PDF: {pdf_path}")
        
        # Detetar fornecedor
        provider = self._detect_provider(text)
        
        # Tentar com parser especifico
        if provider:
            parser = self.parsers.get(provider)
            if parser:
                try:
                    data = parser.parse(text)
                    if data:
                        data["_source_file"] = str(pdf_path)
                        data["_provider"] = provider
                        return data
                except Exception as e:
                    logger.debug(f"Parser {provider} falhou: {e}")
        
        # Se parser falhou ou nao detetou fornecedor, tentar com todos os parsers
        for parser_name, parser in self.parsers.items():
            try:
                data = parser.parse(text)
                if data:
                    data["_source_file"] = str(pdf_path)
                    data["_provider"] = parser_name
                    return data
            except Exception as e:
                logger.debug(f"Parser {parser_name} falhou: {e}")
                continue
        
        # Se nenhum parser funcionou, tentar com PatternManager
        if self.pattern_manager:
            try:
                logger.info("A usar PatternManager para extracao")
                data = self.pattern_manager.extract_all_fields(text, provider or "coopernico")
                if data:
                    data["_source_file"] = str(pdf_path)
                    data["_provider"] = provider or "coopernico"
                    data["_method"] = "patterns"
                    return data
            except Exception as e:
                logger.error(f"PatternManager falhou: {e}")
        
        # Se nada funcionou
        raise ValueError(f"No foi possvel parsear a fatura: {pdf_path}")
    
    def extract_from_text(self, text: str) -> Dict:
        """
        Extrair dados de texto diretamente.
        
        Args:
            text: Texto da fatura
            
        Returns:
            Dicionrio com os dados extrados
        """
        if not text or not text.strip():
            raise ValueError("Texto vazio")
        
        # Detetar fornecedor
        provider = self._detect_provider(text)
        
        # Tentar com parser especifico
        if provider:
            parser = self.parsers.get(provider)
            if parser:
                try:
                    data = parser.parse(text)
                    if data:
                        return data
                except Exception as e:
                    logger.debug(f"Parser {provider} falhou: {e}")
        
        # Tentar com todos os parsers
        for parser_name, parser in self.parsers.items():
            try:
                data = parser.parse(text)
                if data:
                    return data
            except Exception as e:
                logger.debug(f"Parser {parser_name} falhou: {e}")
                continue
        
        # Tentar com PatternManager
        if self.pattern_manager:
            try:
                logger.info("A usar PatternManager para extracao")
                data = self.pattern_manager.extract_all_fields(text, provider or "coopernico")
                if data:
                    data["_method"] = "patterns"
                    return data
            except Exception as e:
                logger.error(f"PatternManager falhou: {e}")
        
        # Se nada funcionou
        raise ValueError("No foi possvel detetar o fornecedor")
    
    def _detect_provider(self, text: str) -> Optional[str]:
