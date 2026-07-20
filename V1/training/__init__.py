"""
Training package - Sistema de treino para ensinar o programa a reconhecer faturas
"""

from .trainer import InvoiceTrainer
from .patterns import PatternManager

__all__ = ["InvoiceTrainer", "PatternManager"]
