#!/usr/bin/env python3
"""
Script para integrar os padrões aprendidos com o extrator principal.

Este script permite:
1. Carregar padrões aprendidos
2. Usar esses padrões para melhorar a extração
3. Criar um parser personalizado com base nos padrões
"""

import sys
from pathlib import Path

# Adicionar o diretório ao path
sys.path.insert(0, str(Path(__file__).parent))

from training.patterns import PatternManager
from pdf_extractor.parsers.base_parser import BaseInvoiceParser
from pdf_extractor.parsers.coopernico_parser import CoopernicoParser
from typing import Dict, Optional
import re
import logging

logger = logging.getLogger(__name__)


class TrainedCoopernicoParser(CoopernicoParser):
    """
    Parser para Coopérnico que usa padrões aprendidos.
    
    Esta classe estende o CoopernicoParser para usar
    os padrões aprendidos através do treino.
    """
    
    def __init__(self, patterns_file: Optional[str] = None):
        super().__init__()
        self.pattern_manager = PatternManager(patterns_file)
        self.use_learned_patterns = True
        
    def parse(self, text: str) -> Dict:
        """
        Parsear texto usando padrões aprendidos.
        
        Args:
            text: Texto extraído do PDF
            
        Returns:
            Dicionário com os dados extraídos
        """
        # Primeiro, tentar com o método padrão
        data = super().parse(text)
        
        if self.use_learned_patterns:
            # Depois, preencher campos em falta com padrões aprendidos
            learned_data = self.pattern_manager.extract_all_fields(text, "coopernico")
            
            # Atualizar dados com valores aprendidos
            for field_name, value in learned_data.items():
                if value is not None and (field_name not in data or not data[field_name]):
                    data[field_name] = value
        
        return data
    
    def detect(self, text: str) -> bool:
        """
        Detetar se o texto é de uma fatura Coopérnico.
        
        Args:
            text: Texto a analisar
            
        Returns:
            True se for da Coopérnico
        """
        # Usar deteção padrão
        if super().detect(text):
            return True
        
        # Verificar se há padrões aprendidos para Coopérnico
        coopernico_patterns = [
            p for field in self.pattern_manager.get_all_fields()
            for p in field.patterns
            if p.provider == "coopernico"
        ]
        
        if not coopernico_patterns:
            return False
        
        # Se houver padrões, assumir que é Coopérnico
        return True


class EnhancedPDFExtractor:
    """
    Extrator de PDF melhorado com padrões aprendidos.
    
    Esta classe estende o PDFExtractor para usar
    os padrões aprendidos durante o treino.
    """
    
    def __init__(self, use_ocr: bool = False, use_training: bool = True):
        from pdf_extractor.extractor import PDFExtractor
        
        super().__init__(use_ocr=use_ocr)
        self.use_training = use_training
        self.pattern_manager = PatternManager()
        
        if use_training:
            # Adicionar parser de Coopérnico com padrões aprendidos
            self.parsers["coopernico"] = TrainedCoopernicoParser()
            
    def extract_from_pdf(self, pdf_path: str, use_ocr: bool = None) -> Dict:
        """
        Extrair dados de um PDF, usando padrões aprendidos.
        
        Args:
            pdf_path: Caminho para o ficheiro PDF
            use_ocr: Usar OCR
            
        Returns:
            Dicionário com os dados extraídos
        """
        # Extrair texto
        ocr = use_ocr if use_ocr is not None else self.use_ocr
        text = self._extract_text(pdf_path, ocr)
        
        # Detetar fornecedor
        provider = self._detect_provider(text)
        
        if not provider:
            # Tentar com padrões aprendidos
            for field in self.pattern_manager.get_all_fields():
                for pattern in field.patterns:
                    if pattern.provider in self.parsers:
                        return self.parsers[pattern.provider].parse(text)
            
            raise ValueError(f"Não foi possível detetar o fornecedor para: {pdf_path}")
        
        # Parsear com o parser adequado
        parser = self.parsers.get(provider)
        if not parser:
            raise ValueError(f"Parser não disponível para fornecedor: {provider}")
        
        return parser.parse(text)
    
    def _extract_text(self, pdf_path: str, use_ocr: bool) -> str:
        """Extrair texto de um PDF."""
        from pdf_extractor.utils import pdf_utils
        return pdf_utils.extract_text_from_pdf(pdf_path, use_ocr=use_ocr)
    
    def _detect_provider(self, text: str) -> Optional[str]:
        """Detetar fornecedor."""
        # Primeiro, tentar com os parsers padrão
        for provider, parser in self.parsers.items():
            if parser.detect(text):
                return provider
        
        # Depois, verificar padrões aprendidos
        providers_with_patterns = set()
        for field in self.pattern_manager.get_all_fields():
            for pattern in field.patterns:
                providers_with_patterns.add(pattern.provider)
        
        # Se houver padrões para um fornecedor, assumir esse fornecedor
        if len(providers_with_patterns) == 1:
            return list(providers_with_patterns)[0]
        
        return None


def create_trained_parser(provider: str = "coopernico", patterns_file: Optional[str] = None) -> BaseInvoiceParser:
    """
    Criar um parser treinado para um fornecedor.
    
    Args:
        provider: Nome do fornecedor
        patterns_file: Caminho para o ficheiro de padrões
        
    Returns:
        Parser treinado
    """
    if provider == "coopernico":
        return TrainedCoopernicoParser(patterns_file)
    else:
        # Para outros fornecedores, usar o parser padrão
        from pdf_extractor.parsers import PARSERS
        parser_class = PARSERS.get(provider)
        if parser_class:
            return parser_class()
        else:
            raise ValueError(f"Parser não disponível para fornecedor: {provider}")


def train_from_examples(examples_dir: str, provider: str = "coopernico") -> PatternManager:
    """
    Treinar a partir de exemplos em um diretório.
    
    Args:
        examples_dir: Diretório com ficheiros de exemplo
        provider: Fornecedor
        
    Returns:
        PatternManager com os padrões aprendidos
    """
    from training.trainer import InvoiceTrainer
    
    trainer = InvoiceTrainer()
    examples_dir = Path(examples_dir)
    
    if not examples_dir.exists():
        raise FileNotFoundError(f"Diretório não encontrado: {examples_dir}")
    
    # Processar todos os PDFs no diretório
    pdf_files = list(examples_dir.glob("*.pdf")) + list(examples_dir.glob("*.PDF"))
    
    for pdf_file in pdf_files:
        try:
            text, filename = trainer.load_pdf(str(pdf_file))
            logger.info(f"Processando: {filename}")
            
            # Aqui poderia adicionar lógica para anotar automaticamente
            # com base em padrões conhecidos
            
        except Exception as e:
            logger.error(f"Erro a processar {pdf_file}: {e}")
            continue
    
    return trainer.pattern_manager


def main():
    """Função principal para teste."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Integrar padrões aprendidos com o extrator')
    parser.add_argument('--test', action='store_true', help='Testar com uma fatura de exemplo')
    parser.add_argument('--train-dir', help='Diretório com faturas para treinar')
    parser.add_argument('--pdf', help='Ficheiro PDF para testar')
    
    args = parser.parse_args()
    
    if args.test:
        # Testar com uma fatura de exemplo
        extractor = EnhancedPDFExtractor(use_training=True)
        
        # Texto de exemplo
        text = """
        Coopérnico - Cooperativa de Energia
        Fatura nº: COOP-2024-001234
        Data Emissão: 15-01-2024
        Data Vencimento: 30-01-2024
        
        Sócio: João Silva
        NIF: 123456789
        
        Consumo: 350,50 kWh
        Total a Pagar: 73,41 €
        """
        
        # Extrair dados
        data = extractor.extract_from_text(text)
        
        print("Dados extraídos:")
        for key, value in data.items():
            if not key.startswith("_"):
                print(f"  {key}: {value}")
    
    elif args.train_dir:
        # Treinar a partir de um diretório
        patterns = train_from_examples(args.train_dir)
        print(f"Padrões aprendidos de {args.train_dir}")
        print(f"Número de campos: {len(patterns.get_all_fields())}")
    
    elif args.pdf:
        # Testar com um PDF
        extractor = EnhancedPDFExtractor(use_training=True)
        data = extractor.extract_from_pdf(args.pdf)
        
        print(f"Dados extraídos de {args.pdf}:")
        for key, value in data.items():
            if not key.startswith("_"):
                print(f"  {key}: {value}")
    
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
