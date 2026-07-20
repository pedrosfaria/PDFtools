"""
Funções utilitárias para manipulação de PDFs
"""

import pdfplumber
import re
from typing import List, Dict, Optional, Tuple
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


def extract_text_from_pdf(pdf_path: str, use_ocr: bool = False) -> str:
    """
    Extrair texto de um ficheiro PDF.
    
    Args:
        pdf_path: Caminho para o ficheiro PDF
        use_ocr: Se True, usa OCR para extrair texto de imagens (requer pytesseract)
        
    Returns:
        Texto extraído do PDF
    """
    pdf_path = Path(pdf_path)
    
    if not pdf_path.exists():
        raise FileNotFoundError(f"Ficheiro não encontrado: {pdf_path}")
    
    text_parts = []
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                # Extrair texto diretamente
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
                
                # Se usar OCR, extrair texto de imagens
                if use_ocr:
                    try:
                        from .ocr_utils import extract_text_from_images
                        ocr_text = extract_text_from_images(page)
                        if ocr_text:
                            text_parts.append(ocr_text)
                    except ImportError:
                        logger.warning("pytesseract não está instalado. OCR não disponível.")
                        
    except Exception as e:
        logger.error(f"Erro a ler PDF {pdf_path}: {e}")
        raise
    
    return "\n".join(text_parts)


def extract_text_with_layout(pdf_path: str) -> List[Dict]:
    """
    Extrair texto com informação de layout (posição, tamanho, etc.)
    
    Args:
        pdf_path: Caminho para o ficheiro PDF
        
    Returns:
        Lista de dicionários com texto e informação de layout
    """
    pdf_path = Path(pdf_path)
    
    if not pdf_path.exists():
        raise FileNotFoundError(f"Ficheiro não encontrado: {pdf_path}")
    
    elements = []
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages):
                # Extrair palavras com posição
                words = page.extract_words()
                if words:
                    for word in words:
                        elements.append({
                            "text": word["text"],
                            "x0": word["x0"],
                            "y0": word["top"],
                            "x1": word["x1"],
                            "y1": word["bottom"],
                            "page": page_num + 1,
                            "size": word.get("size", 0),
                            "fontname": word.get("fontname", ""),
                        })
                        
    except Exception as e:
        logger.error(f"Erro a extrair layout do PDF {pdf_path}: {e}")
        raise
    
    return elements


def find_text_pattern(text: str, pattern: str, flags: int = re.IGNORECASE) -> Optional[str]:
    """
    Procurar um padrão de texto e devolver o primeiro match.
    
    Args:
        text: Texto a procurar
        pattern: Expressão regular
        flags: Flags da regex
        
    Returns:
        Primeiro match ou None
    """
    match = re.search(pattern, text, flags)
    if match:
        return match.group(1) if match.groups() else match.group(0)
    return None


def find_all_text_patterns(text: str, pattern: str, flags: int = re.IGNORECASE) -> List[str]:
    """
    Procurar todos os padrões de texto.
    
    Args:
        text: Texto a procurar
        pattern: Expressão regular
        flags: Flags da regex
        
    Returns:
        Lista de todos os matches
    """
    matches = re.findall(pattern, text, flags)
    return matches


def normalize_text(text: str) -> str:
    """
    Normalizar texto: remover espaços extra, normalizar quebras de linha, etc.
    
    Args:
        text: Texto a normalizar
        
    Returns:
        Texto normalizado
    """
    if not text:
        return ""
    
    # Substituir múltiplos espaços por um só
    text = re.sub(r'\s+', ' ', text)
    
    # Remover caracteres de controlo
    text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
    
    return text.strip()


def extract_amount(text: str) -> Optional[float]:
    """
    Extrair um valor monetário de texto.
    
    Args:
        text: Texto contendo o valor
        
    Returns:
        Valor como float ou None
    """
    # Padrão para valores como: 123,45 € ou € 123,45 ou 123.45
    pattern = r"\b\d{1,3}(?:\.\d{3})*(?:,\d{2})?\s*€\b|\b€\s*\d{1,3}(?:\.\d{3})*(?:,\d{2})?\b|\b\d{1,3}(?:\.\d{3})*(?:\.\d{2})?\b"
    match = re.search(pattern, text, re.IGNORECASE)
    
    if match:
        amount_str = match.group(0)
        # Remover símbolo de euro e espaços
        amount_str = amount_str.replace("€", "").replace(",", ".").strip()
        try:
            return float(amount_str)
        except ValueError:
            return None
    
    return None


def extract_date(text: str, date_format: str = "dd-mm-yyyy") -> Optional[str]:
    """
    Extrair uma data de texto.
    
    Args:
        text: Texto contendo a data
        date_format: Formato esperado (dd-mm-yyyy, dd/mm/yyyy, yyyy-mm-dd)
        
    Returns:
        Data como string ou None
    """
    date_patterns = [
        r"\b\d{2}[/-]\d{2}[/-]\d{4}\b",  # dd-mm-yyyy ou dd/mm/yyyy
        r"\b\d{4}[/-]\d{2}[/-]\d{2}\b",  # yyyy-mm-dd ou yyyy/mm/dd
        r"\b\d{2}\.\d{2}\.\d{4}\b",      # dd.mm.yyyy
    ]
    
    for pattern in date_patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(0)
    
    return None


def extract_number(text: str) -> Optional[float]:
    """
    Extrair um número de texto.
    
    Args:
        text: Texto contendo o número
        
    Returns:
        Número como float ou None
    """
    # Padrão para números com ou sem casas decimais
    pattern = r"\b\d{1,3}(?:\.\d{3})*(?:,\d+)?\b|\b\d+\.\d+\b"
    match = re.search(pattern, text)
    
    if match:
        num_str = match.group(0).replace(",", ".")
        try:
            return float(num_str)
        except ValueError:
            return None
    
    return None
