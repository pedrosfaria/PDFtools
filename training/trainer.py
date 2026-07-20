"""
Trainer for teaching the extractor new patterns from examples
"""

import json
import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from .patterns import PatternManager
from pdf_extractor.extractor import PDFExtractor
from pdf_extractor.utils import extract_text_from_pdf, clean_text


@dataclass
class TrainingExample:
    """A single training example"""
    pdf_path: str
    expected_fields: Dict[str, str]
    extracted_fields: Dict[str, str]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "pdf_path": self.pdf_path,
            "expected_fields": self.expected_fields,
            "extracted_fields": self.extracted_fields
        }


class Trainer:
    """
    Trainer class for teaching the extractor new patterns.
    
    This class:
    - Manages training examples
    - Suggests new patterns based on examples
    - Tests and validates patterns
    """
    
    def __init__(self, pattern_file: str = "training/patterns.json"):
        """
        Initialize trainer.
        
        Args:
            pattern_file: Path to pattern file
        """
        self.pattern_manager = PatternManager(pattern_file)
        self.extractor = PDFExtractor()
        self.examples: List[TrainingExample] = []
    
    def add_example(self, pdf_path: str, expected_fields: Dict[str, str]) -> TrainingExample:
        """
        Add a training example.
        
        Args:
            pdf_path: Path to PDF file
            expected_fields: Dictionary of expected field values
            
        Returns:
            TrainingExample object
        """
        # Extract current fields
        result = self.extractor.extract(pdf_path)
        extracted_fields = result.extracted_fields
        
        example = TrainingExample(
            pdf_path=pdf_path,
            expected_fields=expected_fields,
            extracted_fields=extracted_fields
        )
        
        self.examples.append(example)
        return example
    
    def suggest_patterns(self, field: str, examples: Optional[List[TrainingExample]] = None) -> List[str]:
        """
        Suggest new patterns based on training examples.
        
        Args:
            field: Field name to suggest patterns for
            examples: List of examples to use (uses all if None)
            
        Returns:
            List of suggested pattern strings
        """
        if examples is None:
            examples = self.examples
        
        if not examples:
            return []
        
        suggestions = []
        
        # Collect text samples where field should be found
        text_samples = []
        for example in examples:
            if field in example.expected_fields:
                # Get the text from the PDF
                text = extract_text_from_pdf(example.pdf_path)
                if text:
                    text_samples.append(clean_text(text))
        
        if not text_samples:
            return []
        
        # Simple pattern suggestion: look for common prefixes
        expected_values = [ex.expected_fields.get(field, "") for ex in examples if field in ex.expected_fields]
        
        # Suggest regex patterns based on expected values
        for value in expected_values:
            if value:
                # Escape special regex characters
                import re
                escaped = re.escape(value)
                
                # Suggest patterns that look for the field name followed by the value
                suggestions.append(f"{field}.*?({escaped})")
                suggestions.append(f"{field}[\\s:]+({escaped})")
        
        # Also suggest simple contains patterns
        suggestions.append(field)
        
        return suggestions
    
    def train_from_example(self, pdf_path: str, expected_fields: Dict[str, str], auto_add: bool = True) -> Dict[str, Any]:
        """
        Train from a single example.
        
        Args:
            pdf_path: Path to PDF file
            expected_fields: Dictionary of expected field values
            auto_add: Whether to automatically add suggested patterns
            
        Returns:
            Dictionary with training results
        """
        # Add example
        example = self.add_example(pdf_path, expected_fields)
        
        # Get extracted text
        text = extract_text_from_pdf(pdf_path)
        if not text:
            text = ""
        
        text = clean_text(text)
        
        results = {
            "example": example.to_dict(),
            "suggestions": {},
            "patterns_added": []
        }
        
        # For each expected field, suggest and optionally add patterns
        for field, expected_value in expected_fields.items():
            suggestions = self.suggest_patterns(field, [example])
            results["suggestions"][field] = suggestions
            
            if auto_add and suggestions:
                # Add the first suggestion
                pattern = suggestions[0]
                self.pattern_manager.add_pattern(field, pattern, "regex")
                results["patterns_added"].append({
                    "field": field,
                    "pattern": pattern
                })
        
        # Save patterns
        self.pattern_manager.save_patterns()
        
        # Reload extractor with new patterns
        self.extractor = PDFExtractor()
        
        return results
    
    def train_from_pdf(self, pdf_path: str, expected_fields: Dict[str, str]) -> Dict[str, Any]:
        """
        Convenience method for training from a PDF.
        
        Args:
            pdf_path: Path to PDF file
            expected_fields: Dictionary of expected field values
            
        Returns:
            Training results
        """
        return self.train_from_example(pdf_path, expected_fields, auto_add=True)
    
    def test_extraction(self, pdf_path: str) -> Dict[str, Any]:
        """
        Test extraction on a PDF and return results.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Dictionary with extraction results
        """
        result = self.extractor.extract(pdf_path)
        return result.to_dict()
    
    def get_training_stats(self) -> Dict[str, Any]:
        """Get statistics about training"""
        return {
            "total_examples": len(self.examples),
            "total_fields": len(self.pattern_manager.get_all_fields()),
            "patterns_per_field": {
                field: len(self.pattern_manager.get_patterns_for_field(field))
                for field in self.pattern_manager.get_all_fields()
            }
        }
