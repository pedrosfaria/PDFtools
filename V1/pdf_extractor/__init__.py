"""
PDF Extractor - Sistema de extração de dados de faturas de eletricidade
"""

from .extractor import PDFExtractor
from .config import SUPPORTED_PROVIDERS

__version__ = "1.0.0"
__all__ = ["PDFExtractor", "SUPPORTED_PROVIDERS"]
