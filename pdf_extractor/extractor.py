"""
Main PDF Extractor class
"""

import json
import os
import re
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
    
    def _load_patterns(self) -> Dict[str, List[Dict[str, str]]]:
        """Load extraction patterns from file"""
        patterns = {}
        if os.path.exists(self.config.PATTERN_FILE):
            try:
                with open(self.config.PATTERN_FILE, 'r', encoding='utf-8') as f:
                    loaded_patterns = json.load(f)
                    # Ensure patterns are in the correct format (list of dicts)
                    for field, field_patterns in loaded_patterns.items():
                        if isinstance(field_patterns, list):
                            # Convert string patterns to dict format
                            normalized_patterns = []
                            for p in field_patterns:
                                if isinstance(p, str):
                                    normalized_patterns.append({"pattern": p, "type": "regex"})
                                else:
                                    normalized_patterns.append(p)
                            patterns[field] = normalized_patterns
                        else:
                            patterns[field] = field_patterns
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
            # Handle both string and dict patterns
            if isinstance(pattern_info, str):
                pattern = pattern_info
                pattern_type = "regex"
            else:
                pattern = pattern_info.get("pattern", pattern_info)
                pattern_type = pattern_info.get("type", "regex")
            
            if pattern_type == "regex":
                try:
                    match = re.search(pattern, normalized_text, re.IGNORECASE)
                    if match:
                        return match.group(1) if match.groups() else match.group(0)
                except re.error:
                    continue
            
            elif pattern_type == "contains":
                if str(pattern).lower() in normalized_text:
                    start = normalized_text.find(str(pattern).lower())
                    if start != -1:
                        remaining = normalized_text[start + len(str(pattern)):]
                        lines = remaining.split('\n')
                        if lines:
                            return lines[0].strip()
        
        return None
    
    def _extract_all_fields(self, text: str) -> Dict[str, str]:
        """
        Extract all known fields from text.
        
        Args:
            text: Text to search
            
        Returns:
            Dictionary of field names to extracted values
        """
        fields = {}
        for field_name in self.patterns:
            value = self._extract_field(text, field_name)
            if value:
                fields[field_name] = value
        return fields
    
    def extract(self, pdf_path: str) -> ExtractionResult:
        """
        Extract data from a PDF file.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            ExtractionResult containing raw text, extracted fields, confidence, and errors
        """
        errors = []
        raw_text = self._extract_text(pdf_path)
        
        if not raw_text:
            errors.append("Failed to extract text from PDF")
            return ExtractionResult(
                raw_text="",
                extracted_fields={},
                confidence={},
                errors=errors
            )
        
        extracted_fields = self._extract_all_fields(raw_text)
        
        # Calculate confidence (simple heuristic for now)
        confidence = {}
        for field, value in extracted_fields.items():
            if field in self.patterns:
                confidence[field] = 1.0 / len(self.patterns[field])
            else:
                confidence[field] = 0.5
        
        return ExtractionResult(
            raw_text=raw_text,
            extracted_fields=extracted_fields,
            confidence=confidence,
            errors=errors
        )
