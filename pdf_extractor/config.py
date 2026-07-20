"""
Configuration for PDF Extractor
"""

import os
from dataclasses import dataclass
from typing import List, Dict, Optional


@dataclass
class Config:
    """Configuration settings for PDF extraction"""
    
    # OCR settings
    OCR_ENABLED: bool = True
    OCR_LANGUAGE: str = "eng"
    OCR_DPI: int = 300
    
    # PDF settings
    PDF_TEXT_EXTRACTION: str = "pdfplumber"  # or "pymupdf"
    
    # Extraction settings
    USE_PATTERNS: bool = True
    PATTERN_FILE: str = "training/patterns.json"
    
    # Debug settings
    DEBUG_MODE: bool = False
    SAVE_INTERMEDIATE: bool = False
    
    @classmethod
    def load(cls) -> 'Config':
        """Load configuration from environment or use defaults"""
        return cls(
            OCR_ENABLED=os.getenv("OCR_ENABLED", "true").lower() == "true",
            OCR_LANGUAGE=os.getenv("OCR_LANGUAGE", "eng"),
            OCR_DPI=int(os.getenv("OCR_DPI", "300")),
            PDF_TEXT_EXTRACTION=os.getenv("PDF_TEXT_EXTRACTION", "pdfplumber"),
            USE_PATTERNS=os.getenv("USE_PATTERNS", "true").lower() == "true",
            PATTERN_FILE=os.getenv("PATTERN_FILE", "training/patterns.json"),
            DEBUG_MODE=os.getenv("DEBUG_MODE", "false").lower() == "true",
            SAVE_INTERMEDIATE=os.getenv("SAVE_INTERMEDIATE", "false").lower() == "true",
        )
