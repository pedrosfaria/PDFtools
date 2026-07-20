"""
Parser para faturas da Ibersol
"""

from .base_parser import BaseInvoiceParser
from typing import Dict, Optional
import re
import logging

logger = logging.getLogger(__name__)


class IbersolParser(BaseInvoiceParser):
    """
    Parser específico para faturas da Ibersol.
    """
    
    def __init__(self):
        super().__init__()
        self.provider_name = "ibersol"
        
    def detect(self, text: str) -> bool:
        """
        Detetar se o texto é de uma fatura Ibersol.
        
        Args:
            text: Texto a analisar
            
        Returns:
            True se for da Ibersol, False caso contrário
        """
        ibersol_indicators = [
            "Ibersol",
            "Fatura Ibersol",
            "www.ibersol.pt",
            "Ibersol Energia",
        ]
        
        text_upper = text.upper()
        for indicator in ibersol_indicators:
            if indicator.upper() in text_upper:
                return True
        
        return False
    
    def parse(self, text: str) -> Dict:
        """
        Parsear texto de fatura Ibersol.
        
        Args:
            text: Texto extraído do PDF
            
        Returns:
            Dicionário com os dados extraídos
        """
        self.reset()
        self.raw_text = text
        
        data = {
            "provider": self.provider_name,
        }
        
        # Extrair número da fatura
        data["invoice_number"] = self._extract_ibersol_invoice_number(text)
        
        # Extrair datas
        data["issue_date"] = self._extract_ibersol_issue_date(text)
        data["due_date"] = self._extract_ibersol_due_date(text)
        
        # Extrair período de consumo
        consumption_period = self._extract_consumption_period(text)
        if consumption_period:
            data["consumption_period_start"] = consumption_period["start"]
            data["consumption_period_end"] = consumption_period["end"]
        
        # Extrair consumo
        data["consumption_kwh"] = self._extract_ibersol_consumption(text)
        
        # Extrair potência contratada
        data["power_contracted_kva"] = self._extract_power_contracted(text)
        
        # Extrair preço por kWh
        data["price_per_kwh"] = self._extract_ibersol_price_per_kwh(text)
        
        # Extrair valores monetários
        data["energy_cost"] = self._extract_ibersol_energy_cost(text)
        data["network_cost"] = self._extract_ibersol_network_cost(text)
        
        # Extrair IVA
        iva_info = self._extract_iva(text)
        if iva_info:
            data["iva_rate"] = iva_info.get("rate")
            data["iva_value"] = iva_info.get("value")
        
        # Extrair total
        data["total_amount"] = self._extract_total_amount(text)
        
        # Extrair informações do cliente
        data["client_number"] = self._extract_client_number(text)
        data["nif"] = self._extract_nif(text)
        data["client_name"] = self._extract_client_name(text)
        
        # Extrair morada
        address_info = self._extract_ibersol_address(text)
        if address_info:
            data["address"] = address_info.get("address")
            data["postal_code"] = address_info.get("postal_code")
            data["city"] = address_info.get("city")
        
        # Extrair informações de pagamento
        payment_info = self._extract_payment_info(text)
        if payment_info:
            data["payment_method"] = payment_info.get("method")
            data["payment_reference"] = payment_info.get("reference")
        
        # Extrair informações do contador
        meter_info = self._extract_meter_info(text)
        if meter_info:
            data["meter_number"] = meter_info.get("number")
            data["current_reading"] = meter_info.get("current_reading")
            data["previous_reading"] = meter_info.get("previous_reading")
            data["reading_date"] = meter_info.get("date")
        
        self.extracted_data = data
        return data
    
    def _extract_ibersol_invoice_number(self, text: str) -> Optional[str]:
        """Extrair número da fatura Ibersol."""
        patterns = [
            r"Nº\s*Fatura\s*:?\s*([A-Z0-9\-\s]+)",
            r"Fatura\s*nº\s*:?\s*([A-Z0-9\-\s]+)",
            r"Fatura\s+([A-Z0-9\-\s]+)",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                invoice_number = match.group(1).strip()
                return self._normalize_ibersol_invoice_number(invoice_number)
        
        return None
    
    def _normalize_ibersol_invoice_number(self, invoice_number: str) -> str:
        """Normalizar número de fatura Ibersol."""
        invoice_number = re.sub(r'[\s\-]', '', invoice_number)
        return invoice_number.upper()
    
    def _extract_ibersol_issue_date(self, text: str) -> Optional[str]:
        """Extrair data de emissão Ibersol."""
        patterns = [
            r"Data\s*Emissão\s*:?\s*([\d\-\/\.]+)",
            r"Emitida\s*em\s*([\d\-\/\.]+)",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return None
    
    def _extract_ibersol_due_date(self, text: str) -> Optional[str]:
        """Extrair data de vencimento Ibersol."""
        patterns = [
            r"Data\s*Vencimento\s*:?\s*([\d\-\/\.]+)",
            r"Vence\s*em\s*([\d\-\/\.]+)",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return None
    
    def _extract_ibersol_consumption(self, text: str) -> Optional[float]:
        """Extrair consumo Ibersol em kWh."""
        patterns = [
            r"Consumo\s*Total\s*:?\s*([\d\.,]+)\s*kWh",
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
    
    def _extract_ibersol_price_per_kwh(self, text: str) -> Optional[float]:
        """Extrair preço por kWh Ibersol."""
        patterns = [
            r"Preço\s*da\s*Energia\s*:?\s*([\d\.,]+)\s*€\/kWh",
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
    
    def _extract_ibersol_energy_cost(self, text: str) -> Optional[float]:
        """Extrair custo da energia Ibersol."""
        patterns = [
            r"(?:Custo\s*da\s*Energia|Valor\s*Energia)\s*:?\s*([\d\.,]+)\s*€",
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
    
    def _extract_ibersol_network_cost(self, text: str) -> Optional[float]:
        """Extrair custo de acesso à rede Ibersol."""
        patterns = [
            r"(?:Acesso\s*à\s*Rede|Rede)\s*:?\s*([\d\.,]+)\s*€",
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
    
    def _extract_ibersol_address(self, text: str) -> Optional[Dict]:
        """Extrair morada Ibersol."""
        result = {}
        
        # Procurar por morada
        address_pattern = r"Morada\s*:?\s*([A-Za-z0-9\s,.-]+)"
        address_match = re.search(address_pattern, text, re.IGNORECASE)
        if address_match:
            result["address"] = address_match.group(1).strip()
        
        # Procurar por código postal
        postal_pattern = r"(?:Código\s*Postal|C\.?P\.?)\s*:?\s*([\d\-]+)"
        postal_match = re.search(postal_pattern, text, re.IGNORECASE)
        if postal_match:
            result["postal_code"] = postal_match.group(1).strip()
        
        # Procurar por localidade
        city_pattern = r"(?:Localidade|Cidade)\s*:?\s*([A-Za-z\s]+)"
        city_match = re.search(city_pattern, text, re.IGNORECASE)
        if city_match:
            result["city"] = city_match.group(1).strip()
        
        return result if result else None
