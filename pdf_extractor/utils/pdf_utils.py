"""
PDF text extraction utilities
"""

import pdfplumber
from typing import Optional, List
from PIL import Image
import io


def extract_text_from_pdf(pdf_path: str) -> Optional[str]:
    """
    Extract text from a PDF file using pdfplumber.
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        Extracted text or None if extraction fails
    """
    try:
        text = ""
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text.strip() if text else None
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return None


def extract_images_from_pdf(pdf_path: str) -> List[Image.Image]:
    """
    Extract images from a PDF file.
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        List of PIL Image objects
    """
    images = []
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                for image in page.images:
                    img_data = image["stream"].get_data()
                    img = Image.open(io.BytesIO(img_data))
                    images.append(img)
        return images
    except Exception as e:
        print(f"Error extracting images from PDF: {e}")
        return []
