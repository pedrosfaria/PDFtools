"""
Funções utilitárias para OCR (Optical Character Recognition)
"""

import io
from typing import List, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


def extract_text_from_images(page) -> Optional[str]:
    """
    Extrair texto de imagens numa página PDF usando OCR.
    
    Args:
        page: Página do pdfplumber
        
    Returns:
        Texto extraído ou None
    """
    try:
        import pytesseract
        from PIL import Image
    except ImportError as e:
        logger.warning(f"Biblioteca OCR não disponível: {e}")
        return None
    
    text_parts = []
    
    try:
        # Extrair imagens da página
        images = page.images
        
        for img in images:
            try:
                # Obter a imagem
                img_data = img["image"]
                
                # Converter para PIL Image
                if isinstance(img_data, bytes):
                    img_pil = Image.open(io.BytesIO(img_data))
                else:
                    # Se for um objeto Image do pdfplumber
                    img_pil = img_data.original
                
                # Aplicar OCR
                text = pytesseract.image_to_string(img_pil, lang='por+eng')
                if text.strip():
                    text_parts.append(text)
                    
            except Exception as e:
                logger.warning(f"Erro a processar imagem: {e}")
                continue
                
    except Exception as e:
        logger.error(f"Erro a extrair imagens da página: {e}")
        return None
    
    return "\n".join(text_parts) if text_parts else None


def extract_text_from_pdf_with_ocr(pdf_path: str) -> str:
    """
    Extrair texto de um PDF usando OCR para todas as páginas.
    
    Args:
        pdf_path: Caminho para o ficheiro PDF
        
    Returns:
        Texto extraído
    """
    import pdfplumber
    
    pdf_path = Path(pdf_path)
    
    if not pdf_path.exists():
        raise FileNotFoundError(f"Ficheiro não encontrado: {pdf_path}")
    
    text_parts = []
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                # Tentar extrair texto diretamente
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
                
                # Extrair texto de imagens
                ocr_text = extract_text_from_images(page)
                if ocr_text:
                    text_parts.append(ocr_text)
                    
    except Exception as e:
        logger.error(f"Erro a processar PDF com OCR: {e}")
        raise
    
    return "\n".join(text_parts)
