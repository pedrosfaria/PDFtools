"""
Classe base para parsers de faturas de eletricidade
"""

from abc import ABC, abstractmethod
from typing import Dict, Optional, List
from datetime import datetime
from ..config import STANDARD_FIELDS
from ..utils import pdf_utils, text_utils
import re
import logging

logger = logging.getLogger(__name__)


class BaseInvoiceParser(ABC):
    """
    Classe base abstrata para parsers de faturas.
    
    Cada fornecedor deve implementar a sua própria classe parser
    que herda desta classe base.
    """
    
    def __init__(self):
        """Inicializar o parser."""
        self.provider_name = self.__class__.__name__.replace("Parser", "").lower()
        self.extracted_data = {}
        self.raw_text = ""
        
    @abstractmethod
    def parse(self, text: str) -> Dict:
        """
        Método principal para parsear o texto da fatura.
        
        Args:
            text: Texto extraído do PDF
            
        Returns:
            Dicionário com os dados extraídos
        """
        pass
    
    @abstractmethod
    def detect(self, text: str) -> bool:
        """
        Detetar se o texto pertence a este fornecedor.
        
        Args:
            text: Texto a analisar
            
        Returns:
            True se for deste fornecedor, False caso contrário
        """
        pass
    
    def get_provider_name(self) -> str:
        """Obter o nome do fornecedor."""
        return self.provider_name
    
    def get_extracted_data(self) -> Dict:
        """Obter os dados extraídos."""
        return self.extracted_data
    
    def reset(self):
        """Resetar os dados extraídos."""
        self.extracted_data = {}
        self.raw_text = ""
    
    # Métodos utilitários para os parsers
    
    def _extract_invoice_number(self, text: str) -> Optional[str]:
        """Extrair número da fatura."""
        patterns = [
            r"(?:Nº\s*Fatura|Fatura\s*nº|Invoice\s*No?\.?|N\.?º\s*Fatura)\s*:?\s*([A-Z0-9\-\/\s]+)",
            r"Fatura\s+([A-Z0-9\-\/]+)",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                invoice_number = match.group(1).strip()
                return text_utils.normalize_invoice_number(invoice_number)
        
        return None
    
    def _extract_issue_date(self, text: str) -> Optional[str]:
        """Extrair data de emissão."""
        patterns = [
            r"(?:Data\s*Emissão|Emissão|Issue\s*Date|Data\s*da\s*Fatura)\s*:?\s*([\d\-\/\.]+)",
            r"Emitida\s*em\s*([\d\-\/\.]+)",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                date_str = match.group(1).strip()
                return date_str
        
        return None
    
    def _extract_due_date(self, text: str) -> Optional[str]:
        """Extrair data de vencimento."""
        patterns = [
            r"(?:Data\s*Vencimento|Vencimento|Due\s*Date|Pagar\s*até)\s*:?\s*([\d\-\/\.]+)",
            r"Vence\s*em\s*([\d\-\/\.]+)",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                date_str = match.group(1).strip()
                return date_str
        
        return None
    
    def _extract_consumption_period(self, text: str) -> Optional[Dict]:
        """Extrair período de consumo."""
        patterns = [
            r"(?:Período\s*de\s*Consumo|Consumo\s*de|Period)\s*:?\s*([\d\-\/\.]+)\s*a\s*([\d\-\/\.]+)",
            r"de\s*([\d\-\/\.]+)\s*a\s*([\d\-\/\.]+)",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return {
                    "start": match.group(1).strip(),
                    "end": match.group(2).strip()
                }
        
        return None
    
    def _extract_consumption_kwh(self, text: str) -> Optional[float]:
        """Extrair consumo em kWh."""
        patterns = [
            r"(?:Consumo\s*Total|Total\s*Consumo|kWh\s*Consumidos|Energia\s*Consumida)\s*:?\s*([\d\.,]+)\s*kWh",
            r"([\d\.,]+)\s*kWh",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                consumption_str = match.group(1).strip()
                consumption_str = consumption_str.replace(",", ".")
                try:
                    return float(consumption_str)
                except ValueError:
                    continue
        
        return None
    
    def _extract_total_amount(self, text: str) -> Optional[float]:
        """Extrair valor total a pagar."""
        patterns = [
            r"(?:Total\s*a\s*Pagar|Valor\s*Total|Total\s*Due|Montante\s*Total)\s*:?\s*([\d\.,]+)\s*€",
            r"€\s*([\d\.,]+)",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                amount_str = match.group(1).strip()
                amount_str = amount_str.replace(",", ".")
                try:
                    return float(amount_str)
                except ValueError:
                    continue
        
        return None
    
    def _extract_nif(self, text: str) -> Optional[str]:
        """Extrair NIF."""
        # Procurar por NIF seguido de 9 dígitos
        patterns = [
            r"(?:NIF|N\.?º\s*Identificação\s*Fiscal|Contribuinte)\s*:?\s*([\d\s\-]+)",
            r"NIF\s*([\d\s\-]+)",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                nif_str = match.group(1).strip()
                nif_str = re.sub(r'[\s\-]', '', nif_str)
                return text_utils.normalize_nif(nif_str)
        
        # Procurar apenas por 9 dígitos
        nif_match = re.search(r'\b(\d{9})\b', text)
        if nif_match:
            return text_utils.normalize_nif(nif_match.group(1))
        
        return None
    
    def _extract_client_number(self, text: str) -> Optional[str]:
        """Extrair número do cliente."""
        patterns = [
            r"(?:Nº\s*Cliente|Cliente\s*nº|Client\s*No?\.?|N\.?º\s*do\s*Cliente)\s*:?\s*([A-Z0-9\-\s]+)",
            r"Cliente\s*([A-Z0-9\-\s]+)",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                client_num = match.group(1).strip()
                return text_utils.normalize_invoice_number(client_num)
        
        return None
    
    def _extract_client_name(self, text: str) -> Optional[str]:
        """Extrair nome do cliente."""
        patterns = [
            r"(?:Nome|Cliente|Titular)\s*:?\s*([A-Za-z\s]+)",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                name = match.group(1).strip()
                return text_utils.clean_text(name)
        
        return None
    
    def _extract_address(self, text: str) -> Optional[str]:
        """Extrair morada."""
        patterns = [
            r"(?:Morada|Endereço|Address)\s*:?\s*([A-Za-z0-9\s,.-]+)",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                address = match.group(1).strip()
                return text_utils.clean_text(address)
        
        return None
    
    def _extract_iva(self, text: str) -> Optional[Dict]:
        """Extrair informações do IVA."""
        # Procurar por taxa de IVA
        iva_rate_pattern = r"(?:IVA|Imposto)\s*:?\s*([\d]+)%"
        iva_rate_match = re.search(iva_rate_pattern, text, re.IGNORECASE)
        
        # Procurar por valor de IVA
        iva_value_pattern = r"(?:Valor\s*IVA|IVA\s*a\s*Pagar|Montante\s*IVA)\s*:?\s*([\d\.,]+)\s*€"
        iva_value_match = re.search(iva_value_pattern, text, re.IGNORECASE)
        
        result = {}
        
        if iva_rate_match:
            try:
                result["rate"] = float(iva_rate_match.group(1))
            except ValueError:
                pass
        
        if iva_value_match:
            try:
                amount_str = iva_value_match.group(1).replace(",", ".")
                result["value"] = float(amount_str)
            except ValueError:
                pass
        
        return result if result else None
    
    def _extract_payment_info(self, text: str) -> Optional[Dict]:
        """Extrair informações de pagamento."""
        result = {}
        
        # Método de pagamento
        payment_method_pattern = r"(?:Método\s*de\s*Pagamento|Forma\s*de\s*Pagamento|Payment\s*Method)\s*:?\s*([A-Za-z\s]+)"
        payment_method_match = re.search(payment_method_pattern, text, re.IGNORECASE)
        if payment_method_match:
            result["method"] = payment_method_match.group(1).strip()
        
        # Referência de pagamento
        payment_ref_pattern = r"(?:Referência|Entidade\s*e\s*Referência|Payment\s*Reference)\s*:?\s*([A-Za-z0-9\s\-]+)"
        payment_ref_match = re.search(payment_ref_pattern, text, re.IGNORECASE)
        if payment_ref_match:
            result["reference"] = payment_ref_match.group(1).strip()
        
        return result if result else None
    
    def _extract_meter_info(self, text: str) -> Optional[Dict]:
        """Extrair informações do contador."""
        result = {}
        
        # Número do contador
        meter_number_pattern = r"(?:Nº\s*Contador|Contador\s*nº|Meter\s*No?\.?)\s*:?\s*([A-Z0-9\-\s]+)"
        meter_number_match = re.search(meter_number_pattern, text, re.IGNORECASE)
        if meter_number_match:
            result["number"] = meter_number_match.group(1).strip()
        
        # Leitura atual
        current_reading_pattern = r"(?:Leitura\s*Atual|Leitura\s*Final|Current\s*Reading)\s*:?\s*([\d]+)"
        current_reading_match = re.search(current_reading_pattern, text, re.IGNORECASE)
        if current_reading_match:
            try:
                result["current_reading"] = int(current_reading_match.group(1))
            except ValueError:
                pass
        
        # Leitura anterior
        previous_reading_pattern = r"(?:Leitura\s*Anterior|Leitura\s*Inicial|Previous\s*Reading)\s*:?\s*([\d]+)"
        previous_reading_match = re.search(previous_reading_pattern, text, re.IGNORECASE)
        if previous_reading_match:
            try:
                result["previous_reading"] = int(previous_reading_match.group(1))
            except ValueError:
                pass
        
        # Data da leitura
        reading_date_pattern = r"(?:Data\s*da\s*Leitura|Reading\s*Date)\s*:?\s*([\d\-\/\.]+)"
        reading_date_match = re.search(reading_date_pattern, text, re.IGNORECASE)
        if reading_date_match:
            result["date"] = reading_date_match.group(1).strip()
        
        return result if result else None
    
    def _extract_power_contracted(self, text: str) -> Optional[float]:
        """Extrair potência contratada em kVA."""
        patterns = [
            r"(?:Potência\s*Contratada|Potência|kVA\s*Contratados|Contrated\s*Power)\s*:?\s*([\d\.,]+)\s*kVA",
            r"([\d\.,]+)\s*kVA",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                power_str = match.group(1).strip()
                power_str = power_str.replace(",", ".")
                try:
                    return float(power_str)
                except ValueError:
                    continue
        
        return None
    
    def _extract_price_per_kwh(self, text: str) -> Optional[float]:
        """Extrair preço por kWh."""
        patterns = [
            r"(?:Preço\s*da\s*Energia|Tarifa\s*de\s*Energia|Price\s*per\s*kWh|€\/kWh)\s*:?\s*([\d\.,]+)\s*€\/kWh",
            r"([\d\.,]+)\s*€\/kWh",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                price_str = match.group(1).strip()
                price_str = price_str.replace(",", ".")
                try:
                    return float(price_str)
                except ValueError:
                    continue
        
        return None
