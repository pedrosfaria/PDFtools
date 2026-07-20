# PDF Invoice Extractor

A simple tool to extract data from PDF invoices using OCR and pattern matching.

## Features
- Extract text from PDF invoices (with or without OCR)
- Train custom patterns for invoice field extraction
- Simple English-only interface

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Basic Extraction
```python
from pdf_extractor import PDFExtractor

extractor = PDFExtractor()
result = extractor.extract("invoice.pdf")
print(result)
```

### Training Mode
```python
from training.trainer import Trainer

trainer = Trainer()
trainer.train_from_pdf("invoice.pdf", {"invoice_number": "INV-001", "date": "2024-01-01"})
```

## Project Structure
- `pdf_extractor/` - Core extraction logic
- `training/` - Training and pattern management
- `tests/` - Test files
- `V1/` - Archived previous version (multi-language)
