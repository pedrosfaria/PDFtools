"""
Funções utilitárias para processamento de texto
"""

import re
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import unicodedata


def clean_text(text: str) -> str:
    """
    Limpar texto: remover caracteres especiais, normalizar, etc.
    
    Args:
        text: Texto a limpar
        
    Returns:
        Texto limpo
    """
    if not text:
        return ""
    
    # Normalizar unicode
    text = unicodedata.normalize('NFKD', text)
    
    # Remover caracteres de controlo
    text = ''.join(char for char in text if unicodedata.category(char)[0] != 'C')
    
    # Substituir múltiplos espaços
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()


def normalize_nif(nif: str) -> Optional[str]:
    """
    Normalizar um NIF (9 dígitos).
    
    Args:
        nif: NIF a normalizar
        
    Returns:
        NIF normalizado (9 dígitos) ou None
    """
    if not nif:
        return None
    
    # Extrair apenas dígitos
    digits = re.sub(r'\D', '', nif)
    
    # Verificar se tem 9 dígitos
    if len(digits) == 9:
        return digits
    
    return None


def normalize_invoice_number(invoice_number: str) -> str:
    """
    Normalizar número de fatura.
    
    Args:
        invoice_number: Número de fatura a normalizar
        
    Returns:
        Número de fatura normalizado
    """
    if not invoice_number:
        return ""
    
    # Remover espaços e caracteres especiais
    invoice_number = re.sub(r'[\s\-\/]', '', invoice_number)
    
    return invoice_number.upper()


def parse_date(date_str: str, formats: List[str] = None) -> Optional[datetime]:
    """
    Converter string de data para objeto datetime.
    
    Args:
        date_str: String da data
        formats: Lista de formatos a tentar (opcional)
        
    Returns:
        Objeto datetime ou None
    """
    if not date_str:
        return None
    
    if formats is None:
        formats = [
            "%d-%m-%Y",
            "%d/%m/%Y",
            "%Y-%m-%d",
            "%Y/%m/%d",
            "%d.%m.%Y",
            "%d %m %Y",
        ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    
    return None


def format_date(date: datetime, fmt: str = "%Y-%m-%d") -> str:
    """
    Formatar data como string.
    
    Args:
        date: Objeto datetime
        fmt: Formato de saída
        
    Returns:
        String da data formatada
    """
    if not date:
        return ""
    
    return date.strftime(fmt)


def extract_email(text: str) -> Optional[str]:
    """
    Extrair endereço de email de texto.
    
    Args:
        text: Texto a procurar
        
    Returns:
        Email encontrado ou None
    """
    pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
    match = re.search(pattern, text)
    
    if match:
        return match.group(0)
    
    return None


def extract_phone(text: str) -> Optional[str]:
    """
    Extrair número de telefone de texto.
    
    Args:
        text: Texto a procurar
        
    Returns:
        Telefone encontrado ou None
    """
    # Padrão para telemóveis portugueses (9 dígitos)
    pattern = r"\b9[1236]\d{7}\b|\b\+351\s*9[1236]\d{7}\b"
    match = re.search(pattern, text)
    
    if match:
        return match.group(0)
    
    return None


def find_between(text: str, start: str, end: str) -> Optional[str]:
    """
    Extrair texto entre dois marcadores.
    
    Args:
        text: Texto a procurar
        start: Marcador de início
        end: Marcador de fim
        
    Returns:
        Texto entre os marcadores ou None
    """
    start_idx = text.find(start)
    if start_idx == -1:
        return None
    
    start_idx += len(start)
    end_idx = text.find(end, start_idx)
    
    if end_idx == -1:
        return None
    
    return text[start_idx:end_idx].strip()


def find_after(text: str, marker: str) -> Optional[str]:
    """
    Extrair texto após um marcador.
    
    Args:
        text: Texto a procurar
        marker: Marcador
        
    Returns:
        Texto após o marcador ou None
    """
    idx = text.find(marker)
    if idx == -1:
        return None
    
    return text[idx + len(marker):].strip()


def find_before(text: str, marker: str) -> Optional[str]:
    """
    Extrair texto antes de um marcador.
    
    Args:
        text: Texto a procurar
        marker: Marcador
        
    Returns:
        Texto antes do marcador ou None
    """
    idx = text.find(marker)
    if idx == -1:
        return None
    
    return text[:idx].strip()


def split_by_keywords(text: str, keywords: List[str]) -> List[str]:
    """
    Dividir texto por palavras-chave.
    
    Args:
        text: Texto a dividir
        keywords: Lista de palavras-chave
        
    Returns:
        Lista de secções
    """
    sections = []
    start = 0
    
    for keyword in keywords:
        idx = text.find(keyword, start)
        if idx != -1:
            sections.append(text[start:idx].strip())
            start = idx
    
    sections.append(text[start:].strip())
    
    return [s for s in sections if s]
