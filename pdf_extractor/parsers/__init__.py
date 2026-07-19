"""
Parsers package - Parsers específicos por fornecedor
"""

from .base_parser import BaseInvoiceParser
from .edp_parser import EDPParser
from .galp_parser import GalpParser
from .ibersol_parser import IbersolParser
from .coopernico_parser import CoopernicoParser

__all__ = ["BaseInvoiceParser", "EDPParser", "GalpParser", "IbersolParser", "CoopernicoParser"]

# Dicionário de parsers por fornecedor
PARSERS = {
    "edp": EDPParser,
    "galp": GalpParser,
    "ibersol": IbersolParser,
    "coopernico": CoopernicoParser,
}
