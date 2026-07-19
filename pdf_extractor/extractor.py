"""
Motor principal de extração de dados de faturas de eletricidade
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
    Motor principal para extração de dados de faturas de eletricidade em PDF.
    
    Esta classe coordena todo o processo:
    1. Leitura do PDF
    2. Deteção do fornecedor
    3. Parsing com o parser adequado
    4. Validação dos dados
    5. Exportação para o formato desejado
    """
    
    def __init__(self, use_ocr: bool = False, output_dir: str = None):
        """
        Inicializar o extrator.
        
        Args:
            use_ocr: Se True, usa OCR para extrair texto de imagens
            output_dir: Diretório de saída (padrão: data/output)
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
        """Inicializar todos os parsers disponíveis."""
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
            use_ocr: Usar OCR (sobrepõe a configuração global)
            
        Returns:
            Dicionário com os dados extraídos
        """
        pdf_path = Path(pdf_path)
        
        if not pdf_path.exists():
            raise FileNotFoundError(f"Ficheiro não encontrado: {pdf_path}")
        
        # Extrair texto do PDF
        ocr = use_ocr if use_ocr is not None else self.use_ocr
        text = pdf_utils.extract_text_from_pdf(str(pdf_path), use_ocr=ocr)
        
        if not text or not text.strip():
            raise ValueError(f"Não foi possível extrair texto do PDF: {pdf_path}")
        
        # Detetar fornecedor
        provider = self._detect_provider(text)
        
        if not provider:
            logger.warning(f"Não foi possível detetar o fornecedor para: {pdf_path}")
            # Tentar com todos os parsers
            for parser_name, parser in self.parsers.items():
                try:
                    data = parser.parse(text)
                    if data:
                        return data
                except Exception as e:
                    logger.debug(f"Parser {parser_name} falhou: {e}")
                    continue
            
            raise ValueError(f"Não foi possível parsear a fatura: {pdf_path}")
        
        # Parsear com o parser adequado
        parser = self.parsers.get(provider)
        if not parser:
            raise ValueError(f"Parser não disponível para fornecedor: {provider}")
        
        data = parser.parse(text)
        
        # Adicionar metadados
        data["_source_file"] = str(pdf_path)
        data["_provider"] = provider
        
        return data
    
    def extract_from_text(self, text: str) -> Dict:
        """
        Extrair dados de texto diretamente.
        
        Args:
            text: Texto da fatura
            
        Returns:
            Dicionário com os dados extraídos
        """
        if not text or not text.strip():
            raise ValueError("Texto vazio")
        
        # Detetar fornecedor
        provider = self._detect_provider(text)
        
        if not provider:
            # Tentar com todos os parsers
            for parser_name, parser in self.parsers.items():
                try:
                    data = parser.parse(text)
                    if data:
                        return data
                except Exception as e:
                    logger.debug(f"Parser {parser_name} falhou: {e}")
                    continue
            
            raise ValueError("Não foi possível detetar o fornecedor")
        
        # Parsear com o parser adequado
        parser = self.parsers.get(provider)
        if not parser:
            raise ValueError(f"Parser não disponível para fornecedor: {provider}")
        
        return parser.parse(text)
    
    def _detect_provider(self, text: str) -> Optional[str]:
        """
        Detetar o fornecedor do texto.
        
        Args:
            text: Texto a analisar
            
        Returns:
            Nome do fornecedor ou None
        """
        for provider, parser in self.parsers.items():
            if parser.detect(text):
                return provider
        
        return None
    
    def extract_multiple(self, pdf_paths: List[str], use_ocr: bool = None) -> List[Dict]:
        """
        Extrair dados de múltiplos PDFs.
        
        Args:
            pdf_paths: Lista de caminhos para ficheiros PDF
            use_ocr: Usar OCR
            
        Returns:
            Lista de dicionários com os dados extraídos
        """
        results = []
        
        for pdf_path in pdf_paths:
            try:
                data = self.extract_from_pdf(pdf_path, use_ocr=use_ocr)
                results.append(data)
                logger.info(f"Processado: {pdf_path}")
            except Exception as e:
                logger.error(f"Erro a processar {pdf_path}: {e}")
                results.append({
                    "_source_file": str(pdf_path),
                    "_error": str(e)
                })
        
        return results
    
    def export_to_csv(self, data: Union[Dict, List[Dict]], output_path: str = None) -> str:
        """
        Exportar dados para CSV.
        
        Args:
            data: Dados a exportar (dicionário ou lista de dicionários)
            output_path: Caminho de saída (opcional)
            
        Returns:
            Caminho do ficheiro criado
        """
        if isinstance(data, dict):
            data = [data]
        
        if not output_path:
            output_path = self.output_dir / "invoices.csv"
        else:
            output_path = Path(output_path)
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Obter todos os campos
        all_fields = set()
        for item in data:
            all_fields.update(item.keys())
        
        # Ordenar campos (campos padrão primeiro)
        sorted_fields = [f for f in STANDARD_FIELDS if f in all_fields]
        sorted_fields.extend([f for f in all_fields if f not in STANDARD_FIELDS and not f.startswith("_")])
        sorted_fields.extend([f for f in all_fields if f.startswith("_")])
        
        with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=sorted_fields, extrasaction='ignore')
            writer.writeheader()
            writer.writerows(data)
        
        logger.info(f"Dados exportados para: {output_path}")
        return str(output_path)
    
    def export_to_json(self, data: Union[Dict, List[Dict]], output_path: str = None) -> str:
        """
        Exportar dados para JSON.
        
        Args:
            data: Dados a exportar
            output_path: Caminho de saída (opcional)
            
        Returns:
            Caminho do ficheiro criado
        """
        if isinstance(data, dict):
            data = [data]
        
        if not output_path:
            output_path = self.output_dir / "invoices.json"
        else:
            output_path = Path(output_path)
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as jsonfile:
            json.dump(data, jsonfile, indent=2, ensure_ascii=False, default=str)
        
        logger.info(f"Dados exportados para: {output_path}")
        return str(output_path)
    
    def export_to_excel(self, data: Union[Dict, List[Dict]], output_path: str = None) -> str:
        """
        Exportar dados para Excel.
        
        Args:
            data: Dados a exportar
            output_path: Caminho de saída (opcional)
            
        Returns:
            Caminho do ficheiro criado
        """
        if isinstance(data, dict):
            data = [data]
        
        if not output_path:
            output_path = self.output_dir / "invoices.xlsx"
        else:
            output_path = Path(output_path)
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Criar DataFrame
        df = pd.DataFrame(data)
        
        # Reordenar colunas (campos padrão primeiro)
        all_columns = list(df.columns)
        sorted_columns = [c for c in STANDARD_FIELDS if c in all_columns]
        sorted_columns.extend([c for c in all_columns if c not in STANDARD_FIELDS and not c.startswith("_")])
        sorted_columns.extend([c for c in all_columns if c.startswith("_")])
        
        df = df[sorted_columns]
        
        # Guardar para Excel
        df.to_excel(output_path, index=False, engine='openpyxl')
        
        logger.info(f"Dados exportados para: {output_path}")
        return str(output_path)
    
    def export(self, data: Union[Dict, List[Dict]], format: str = None, output_path: str = None) -> str:
        """
        Exportar dados no formato especificado.
        
        Args:
            data: Dados a exportar
            format: Formato (csv, json, excel)
            output_path: Caminho de saída (opcional)
            
        Returns:
            Caminho do ficheiro criado
        """
        if format is None:
            format = DEFAULT_EXPORT_FORMAT
        
        format = format.lower()
        
        if format not in EXPORT_FORMATS:
            raise ValueError(f"Formato não suportado: {format}. Opções: {EXPORT_FORMATS}")
        
        if format == "csv":
            return self.export_to_csv(data, output_path)
        elif format == "json":
            return self.export_to_json(data, output_path)
        elif format == "excel":
            return self.export_to_excel(data, output_path)
        
        raise ValueError(f"Formato desconhecido: {format}")
    
    def process_directory(self, input_dir: str, output_format: str = None, use_ocr: bool = None) -> List[str]:
        """
        Processar todos os PDFs num diretório.
        
        Args:
            input_dir: Diretório com os PDFs
            output_format: Formato de saída
            use_ocr: Usar OCR
            
        Returns:
            Lista de caminhos dos ficheiros de saída criados
        """
        input_dir = Path(input_dir)
        
        if not input_dir.exists():
            raise FileNotFoundError(f"Diretório não encontrado: {input_dir}")
        
        # Encontrar todos os PDFs
        pdf_files = list(input_dir.glob("*.pdf")) + list(input_dir.glob("*.PDF"))
        
        if not pdf_files:
            logger.warning(f"Não foram encontrados ficheiros PDF em: {input_dir}")
            return []
        
        # Extrair dados de todos os PDFs
        all_data = self.extract_multiple([str(f) for f in pdf_files], use_ocr=use_ocr)
        
        # Exportar dados
        if output_format:
            output_path = self.export(all_data, format=output_format)
            return [output_path]
        else:
            # Exportar em todos os formatos
            results = []
            for fmt in EXPORT_FORMATS:
                output_path = self.export(all_data, format=fmt)
                results.append(output_path)
            return results
    
    def get_supported_providers(self) -> List[str]:
        """Obter lista de fornecedores suportados."""
        return list(self.parsers.keys())
    
    def add_custom_parser(self, provider: str, parser: BaseInvoiceParser):
        """
        Adicionar um parser personalizado.
        
        Args:
            provider: Nome do fornecedor
            parser: Instância do parser
        """
        self.parsers[provider.lower()] = parser
        logger.info(f"Parser personalizado adicionado para: {provider}")
