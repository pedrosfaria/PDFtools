#!/usr/bin/env python3
"""
Example usage of the PDF Invoice Extractor
"""

from pdf_extractor import PDFExtractor
from training.trainer import Trainer
import json


def example_basic_extraction():
    """Example: Basic PDF extraction"""
    print("=== Basic Extraction Example ===")
    
    extractor = PDFExtractor()
    
    # Replace with your PDF path
    pdf_path = "example_invoice.pdf"
    
    try:
        result = extractor.extract(pdf_path)
        print(f"Raw text length: {len(result.raw_text)} characters")
        print(f"Extracted fields: {result.extracted_fields}")
        print(f"Confidence: {result.confidence}")
        if result.errors:
            print(f"Errors: {result.errors}")
    except Exception as e:
        print(f"Error: {e}")


def example_training():
    """Example: Training the extractor"""
    print("\n=== Training Example ===")
    
    trainer = Trainer()
    
    # Replace with your PDF path
    pdf_path = "example_invoice.pdf"
    
    # Define expected fields for this invoice
    expected_fields = {
        "invoice_number": "INV-2024-001",
        "date": "2024-01-15",
        "total": "1000.00",
        "customer": "John Doe Inc"
    }
    
    try:
        # Train from example
        results = trainer.train_from_pdf(pdf_path, expected_fields)
        print(f"Training results: {json.dumps(results, indent=2)}")
        
        # Test extraction after training
        test_results = trainer.test_extraction(pdf_path)
        print(f"Test extraction: {json.dumps(test_results, indent=2)}")
        
        # Get training stats
        stats = trainer.get_training_stats()
        print(f"Training stats: {json.dumps(stats, indent=2)}")
        
    except Exception as e:
        print(f"Error: {e}")


def example_pattern_management():
    """Example: Manual pattern management"""
    print("\n=== Pattern Management Example ===")
    
    from training.patterns import PatternManager
    
    manager = PatternManager()
    
    # Add a custom pattern
    manager.add_pattern(
        field="invoice_number",
        pattern=r"Invoice[\s:]+([A-Z0-9\-]+)",
        pattern_type="regex",
        description="Match invoice numbers like INV-2024-001"
    )
    
    # Save patterns
    manager.save_patterns()
    
    # List all fields
    print(f"All fields: {manager.get_all_fields()}")
    
    # Get patterns for a specific field
    patterns = manager.get_patterns_for_field("invoice_number")
    print(f"Patterns for 'invoice_number': {patterns}")


if __name__ == "__main__":
    print("PDF Invoice Extractor - Example Usage")
    print("=" * 50)
    
    # Create a sample patterns file if it doesn't exist
    from training.patterns import PatternManager
    manager = PatternManager()
    manager.save_patterns()
    
    example_basic_extraction()
    example_training()
    example_pattern_management()
    
    print("\nDone!")
