"""
Main PDF Extractor class
"""

import json
import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from .config import Config
from .utils import extract_text_from_pdf, perform_ocr_on_pdf, clean_text, normalize_text


@dataclass
class ExtractionResult:
    """Result of PDF extraction"""
    raw_text: str
    extracted_fields: Dict[str, str]
    confidence: Dict[str, float]
    errors: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "raw_text": self.raw_text,
            "extracted_fields": self.extracted_fields,
            "confidence": self.confidence,
            "errors": self.errors
        }


class PDFExtractor:
    """
    Main class for extracting data from PDF invoices.
    
    This class handles:
    - Text extraction from PDFs (with or without OCR)
    - Field extraction using patterns
    - Basic validation
    """
    
    def __init__(self, config: Optional[Config] = None):
        """
        Initialize the PDF extractor.
        
        Args:
            config: Configuration object (uses defaults if None)
        """
        self.config = config or Config.load()
        self.patterns = self._load_patterns()
    
    def _load_patterns(self) -> Dict[str, List[str]]:
        """Load extraction patterns from file"""
        patterns = {}
        if os.path.exists(self.config.PATTERN_FILE):
            try:
                with open(self.config.PATTERN_FILE, 'r', encoding='utf-8') as f:
                    patterns = json.load(f)
            except Exception as e:
                print(f"Error loading patterns: {e}")
        return patterns
    
    def _extract_text(self, pdf_path: str) -> Optional[str]:
        """
        Extract text from PDF, trying direct extraction first, then OCR.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Extracted text or None
        """
        # Try direct text extraction first
        text = extract_text_from_pdf(pdf_path)
        if text:
            return text
        
        # Fall back to OCR if enabled
        if self.config.OCR_ENABLED:
            text = perform_ocr_on_pdf(pdf_path, self.config.OCR_LANGUAGE)
            if text:
                return text
        
        return None
    
    def _extract_field(self, text: str, field_name: str) -> Optional[str]:
        """
        Extract a specific field using patterns.
        
        Args:
            text: Text to search
            field_name: Name of the field to extract
            
        Returns:
            Extracted value or None
        """
        if field_name not in self.patterns:
            return None
        
        normalized_text = normalize_text(text)
        
        for pattern_info in self.patterns[field_name]:
            pattern = pattern_info.get("pattern", "")
            pattern_type = pattern_info.get("type", "regex")
            
            if pattern_type == "regex":
                import re
                match = re.search(pattern, normalized_text)
                if match:
                    return match.group(1) if match.groups() else match.group(0)
            
            elif pattern_type == "contains":
                if pattern.lower() in normalized_text:
                    # Return the part after the pattern
                    start = normalized_text.find(pattern.lower())
                    if start != -1:
                        remaining = normalized_text[start + len(pattern):]
                        # Get next line or reasonable chunk
                        lines = remaining.split('\n')
                        if lines:
                            return lines[0].strip()
        
        return None
    
    def extract(self, pdf_path: str) -> ExtractionResult:
        """
        Extract data from a PDF invoice.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            ExtractionResult with all extracted data
        """
        errors = []
        extracted_fields = {}
        confidence = {}
        
        # Extract raw text
        raw_text = self._extract_text(pdf_path)
        if not raw_text:
            errors.append("Failed to extract text from PDF")
            return ExtractionResult(
                raw_text="",
                extracted_fields={},
                confidence={},
                errors=errors
            )
        
        raw_text = clean_text(raw_text)
        
        # Extract fields using patterns
        for field_name in self.patterns:
            value = self._extract_field(raw_text, field_name)
            if value:
                extracted_fields[field_name] = value
                confidence[field_name] = 0.9  # High confidence for pattern matches
            else:
                confidence[field_name] = 0.1  # Low confidence for no match
        
        return ExtractionResult(
            raw_text=raw_text,
            extracted_fields=extracted_fields,
            confidence=confidence,
            errors=errors
        )
    
    def extract_all(self, pdf_path: str) -> Dict[str, Any]:
        """
        Convenience method to extract and return dictionary.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Dictionary with extraction results
        """
        result = self.extract(pdf_path)
        return result.to_dict()
