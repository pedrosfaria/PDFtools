#!/usr/bin/env python3
"""
Main entry point for PDF Invoice Extractor
"""

import argparse
import json
import sys

from pdf_extractor import PDFExtractor
from training.trainer import Trainer


def extract_command(args):
    """Handle extract command"""
    extractor = PDFExtractor()
    
    for pdf_path in args.files:
        print(f"\nProcessing: {pdf_path}")
        result = extractor.extract(pdf_path)
        
        if args.json:
            print(json.dumps(result.to_dict(), indent=2))
        else:
            print(f"Raw text length: {len(result.raw_text)} characters")
            print("\nExtracted fields:")
            for field, value in result.extracted_fields.items():
                confidence = result.confidence.get(field, 0)
                print(f"  {field}: {value} (confidence: {confidence:.2f})")
            
            if result.errors:
                print(f"\nErrors: {result.errors}")


def train_command(args):
    """Handle train command"""
    trainer = Trainer()
    
    # Parse expected fields from command line
    expected_fields = {}
    if args.fields:
        for field_spec in args.fields:
            if '=' in field_spec:
                field, value = field_spec.split('=', 1)
                expected_fields[field.strip()] = value.strip()
    
    if not expected_fields:
        print("Error: No fields specified for training. Use --fields field=value")
        sys.exit(1)
    
    results = trainer.train_from_pdf(args.file, expected_fields)
    
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print(f"Training completed for: {args.file}")
        print(f"Patterns added: {len(results.get('patterns_added', []))}")
        
        if results.get('suggestions'):
            print("\nSuggestions:")
            for field, suggestions in results['suggestions'].items():
                print(f"  {field}: {suggestions}")


def test_command(args):
    """Handle test command"""
    trainer = Trainer()
    result = trainer.test_extraction(args.file)
    
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"Extraction test for: {args.file}")
        print(f"Raw text length: {len(result.get('raw_text', ''))} characters")
        print("\nExtracted fields:")
        for field, value in result.get('extracted_fields', {}).items():
            confidence = result.get('confidence', {}).get(field, 0)
            print(f"  {field}: {value} (confidence: {confidence:.2f})")


def stats_command(args):
    """Handle stats command"""
    trainer = Trainer()
    stats = trainer.get_training_stats()
    
    if args.json:
        print(json.dumps(stats, indent=2))
    else:
        print("Training Statistics:")
        print(f"  Total examples: {stats.get('total_examples', 0)}")
        print(f"  Total fields: {stats.get('total_fields', 0)}")
        print("\nPatterns per field:")
        for field, count in stats.get('patterns_per_field', {}).items():
            print(f"  {field}: {count} patterns")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="PDF Invoice Extractor - Extract data from PDF invoices"
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Extract command
    extract_parser = subparsers.add_parser('extract', help='Extract data from PDF')
    extract_parser.add_argument('files', nargs='+', help='PDF files to extract')
    extract_parser.add_argument('--json', action='store_true', help='Output in JSON format')
    
    # Train command
    train_parser = subparsers.add_parser('train', help='Train extractor with example')
    train_parser.add_argument('file', help='PDF file to train with')
    train_parser.add_argument('--fields', nargs='+', help='Expected fields (format: field=value)')
    train_parser.add_argument('--json', action='store_true', help='Output in JSON format')
    
    # Test command
    test_parser = subparsers.add_parser('test', help='Test extraction on PDF')
    test_parser.add_argument('file', help='PDF file to test')
    test_parser.add_argument('--json', action='store_true', help='Output in JSON format')
    
    # Stats command
    stats_parser = subparsers.add_parser('stats', help='Show training statistics')
    stats_parser.add_argument('--json', action='store_true', help='Output in JSON format')
    
    args = parser.parse_args()
    
    if args.command == 'extract':
        extract_command(args)
    elif args.command == 'train':
        train_command(args)
    elif args.command == 'test':
        test_command(args)
    elif args.command == 'stats':
        stats_command(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
