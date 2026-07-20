"""
OCR utilities for image text extraction
"""

import pytesseract
from PIL import Image
from typing import Optional


def preprocess_image(image: Image.Image) -> Image.Image:
    """
    Preprocess image for better OCR results.
    Simple version without OpenCV dependency.
    
    Args:
        image: PIL Image to preprocess
        
    Returns:
        Preprocessed PIL Image
    """
    # Convert to grayscale
    return image.convert('L')


def perform_ocr(image: Image.Image, language: str = "eng") -> Optional[str]:
    """
    Perform OCR on an image.
    
    Args:
        image: PIL Image to process
        language: OCR language
        
    Returns:
        Extracted text or None if OCR fails
    """
    try:
        # Preprocess image
        processed_img = preprocess_image(image)
        
        # Perform OCR
        text = pytesseract.image_to_string(processed_img, lang=language)
        return text.strip() if text else None
    except Exception as e:
        print(f"OCR Error: {e}")
        return None


def perform_ocr_on_pdf(pdf_path: str, language: str = "eng") -> Optional[str]:
    """
    Perform OCR on all pages of a PDF.
    
    Args:
        pdf_path: Path to PDF file
        language: OCR language
        
    Returns:
        Combined text from all pages or None
    """
    from .pdf_utils import extract_images_from_pdf
    
    images = extract_images_from_pdf(pdf_path)
    if not images:
        # If no images found, try direct text extraction first
        from .pdf_utils import extract_text_from_pdf
        text = extract_text_from_pdf(pdf_path)
        if text:
            return text
        return None
    
    all_text = ""
    for img in images:
        text = perform_ocr(img, language)
        if text:
            all_text += text + "\n"
    
    return all_text.strip() if all_text else None
