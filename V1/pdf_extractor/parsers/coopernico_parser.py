"""
Parser para faturas da Coopérnico (Cooperativa de Energia)
"""

from .base_parser import BaseInvoiceParser
from typing import Dict, Optional
import re
import logging

logger = logging.getLogger(__name__)


class CoopernicoParser(BaseInvoiceParser):
    """
    Parser específico para faturas da Coopérnico.
    
    A Coopérnico é uma cooperativa de energia renovável em Portugal
    que tem um formato específico para as suas faturas.
    """
    
    def __init__(self):
        super().__init__()
        self.provider_name = "coopernico"
        
    def detect(self, text: str) -> bool:
        """
        Detetar se o texto é de uma fatura Coopérnico.
        
        Args:
            text: Texto a analisar
            
        Returns:
            True se for da Coopérnico, False caso contrário
        """
        coopernico_indicators = [
            "Coopérnico",
            "Cooperativa de Energia",
            "Fatura Coopérnico",
            "www.coopernico.pt",
            "Coopérnico - Energia",
            "Cooperativa de Consumo de Energia",
            "cliente@coopernico.org",
            "FA CO",  # Formato de fatura: FA CO25/27 667
        ]
        
        text_upper = text.upper()
        for indicator in coopernico_indicators:
            if indicator.upper() in text_upper:
                return True
        
        return False
    
    def parse(self, text: str) -> Dict:
        """
        Parsear texto de fatura Coopérnico.
        
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
        data["invoice_number"] = self._extract_invoice_number(text)
        
        # Extrair datas
        data["issue_date"] = self._extract_issue_date(text)
        data["due_date"] = self._extract_due_date(text)
        
        # Extrair período de consumo
        consumption_period = self._extract_consumption_period(text)
        if consumption_period:
            data["consumption_period_start"] = consumption_period["start"]
            data["consumption_period_end"] = consumption_period["end"]
        
        # Extrair consumo
        data["consumption_kwh"] = self._extract_consumption(text)
        
        # Extrair potência contratada
        data["power_contracted_kva"] = self._extract_power_contracted(text)
        
        # Extrair preço por kWh
        data["price_per_kwh"] = self._extract_price_per_kwh(text)
        
        # Extrair valores monetários
        data["energy_cost"] = self._extract_energy_cost(text)
        data["network_cost"] = self._extract_network_cost(text)
        
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
        address_info = self._extract_address(text)
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
    
    def _extract_invoice_number(self, text: str) -> Optional[str]:
        """Extrair número da fatura Coopérnico."""
        # Padrões para faturas Coopérnico
        # Formato: "Fatura: FA CO25/27 667" ou "FA CO25/27 667"
        patterns = [
            r"Fatura\s*:?\s*(FA\s*CO\d{2}/\d{2}\s*\d+)",
            r"(FA\s*CO\d{2}/\d{2}\s*\d+)",
            r"N°\s*Fatura\s*:?\s*([A-Z0-9\-\s\/]+)",
            r"Fatura\s*n°\s*:?\s*([A-Z0-9\-\s\/]+)",
            r"Documento\s*n°\s*:?\s*([A-Z0-9\-\s\/]+)",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                invoice_number = match.group(1).strip()
                # Normalizar: remover espaços extra
                invoice_number = re.sub(r'\s+', ' ', invoice_number)
                return invoice_number
        
        return None
    
    def _extract_issue_date(self, text: str) -> Optional[str]:
        """Extrair data de emissão."""
        # Formato: "Data: 27/05/2025"
        patterns = [
            r"Data\s*:\s*(\d{2}/\d{2}/\d{4})",
            r"Data\s*da\s*Fatura\s*:?\s*(\d{2}/\d{2}/\d{4})",
            r"Emitida\s*em\s*(\d{2}/\d{2}/\d{4})",
            r"Data\s*Emissão\s*:?\s*(\d{2}/\d{2}/\d{4})",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return None
    
    def _extract_due_date(self, text: str) -> Optional[str]:
        """Extrair data de vencimento."""
        patterns = [
            r"Vencimento\s*:?\s*(\d{2}/\d{2}/\d{4})",
            r"Data\s*Vencimento\s*:?\s*(\d{2}/\d{2}/\d{4})",
            r"Pagar\s*até\s*(\d{2}/\d{2}/\d{4})",
            r"Débito\s*na\s*minha\s*conta\s*a\s*partir\s*de\s*(\d{2}/\d{2}/\d{4})",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return None
    
    def _extract_consumption_period(self, text: str) -> Optional[Dict]:
        """Extrair período de consumo."""
        # Formato: "Período de faturação: 18/04/2025 a 20/05/2025"
        pattern = r"Período\s*de\s*faturação\s*:?\s*(\d{2}/\d{2}/\d{4})\s*a\s*(\d{2}/\d{2}/\d{4})"
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return {
                "start": match.group(1).strip(),
                "end": match.group(2).strip()
            }
        return None
    
    def _extract_consumption(self, text: str) -> Optional[float]:
        """Extrair consumo em kWh."""
        # Procurar por valores numéricos seguidos de kWh
        patterns = [
            r"(\d+[.,]?\d*)\s*kWh",
            r"Consumo\s*:?\s*(\d+[.,]?\d*)\s*kWh",
            r"Energia\s*Consumida\s*:?\s*(\d+[.,]?\d*)",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                value = match.group(1).replace(",", ".")
                try:
                    return float(value)
                except ValueError:
                    continue
        
        return None
    
    def _extract_power_contracted(self, text: str) -> Optional[float]:
        """Extrair potência contratada em kVA."""
        # Formato: "3,45kVA" ou "Potência: 3,45 kVA"
        patterns = [
            r"(\d+[.,]?\d*)\s*kVA",
            r"Potência\s*[Cc]ontratada\s*:?\s*(\d+[.,]?\d*)\s*kVA",
            r"Potência\s*:?\s*(\d+[.,]?\d*)\s*kVA",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                value = match.group(1).replace(",", ".")
                try:
                    return float(value)
                except ValueError:
                    continue
        
        return None
    
    def _extract_price_per_kwh(self, text: str) -> Optional[float]:
        """Extrair preço por kWh."""
        patterns = [
            r"(\d+[.,]?\d*)\s*€/kWh",
            r"Preço\s*Energia\s*:?\s*(\d+[.,]?\d*)\s*€",
            r"Tarifa\s*Energia\s*:?\s*(\d+[.,]?\d*)\s*€",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                value = match.group(1).replace(",", ".")
                try:
                    return float(value)
                except ValueError:
                    continue
        
        return None
    
    def _extract_energy_cost(self, text: str) -> Optional[float]:
        """Extrair custo da energia."""
        patterns = [
            r"Energia\s*:?\s*(\d+[.,]?\d*)\s*€",
            r"Custo\s*Energia\s*:?\s*(\d+[.,]?\d*)\s*€",
            r"Valor\s*Energia\s*:?\s*(\d+[.,]?\d*)\s*€",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                value = match.group(1).replace(",", ".")
                try:
                    return float(value)
                except ValueError:
                    continue
        
        return None
    
    def _extract_network_cost(self, text: str) -> Optional[float]:
        """Extrair custo de acesso à rede."""
        patterns = [
            r"Pot[êe]ncia\s*:?\s*(\d+[.,]?\d*)\s*€",
            r"Acesso\s*Rede\s*:?\s*(\d+[.,]?\d*)\s*€",
            r"Encargos\s*e\s*Taxas\s*:?\s*(\d+[.,]?\d*)\s*€",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                value = match.group(1).replace(",", ".")
                try:
                    return float(value)
                except ValueError:
                    continue
        
        return None
    
    def _extract_total_amount(self, text: str) -> Optional[float]:
        """Extrair valor total da fatura."""
        # Formato: "Total a Pagar: 13,14 €" ou "Total: 13,14 €"
        patterns = [
            r"Total\s*a\s*Pagar\s*:?\s*(\d+[.,]?\d*)\s*€",
            r"Total\s*:?\s*(\d+[.,]?\d*)\s*€",
            r"Montante\s*Total\s*:?\s*(\d+[.,]?\d*)\s*€",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                value = match.group(1).replace(",", ".")
                try:
                    return float(value)
                except ValueError:
                    continue
        
        return None
    
    def _extract_nif(self, text: str) -> Optional[str]:
        """Extrair NIF do cliente."""
        # Formato: "NIF: 216031893"
        patterns = [
            r"NIF\s*:?\s*(\d{9})",
            r"N\.?\s*I\.?F\.?\s*:?\s*(\d{9})",
            r"Número\s*de\s*Identificação\s*Fiscal\s*:?\s*(\d{9})",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return None
    
    def _extract_client_name(self, text: str) -> Optional[str]:
        """Extrair nome do cliente."""
        # Formato: "Nome do Titular: Pedro Cabral Santiago Faria"
        patterns = [
            r"Nome\s*do\s*Titular\s*:?\s*([A-Za-z\s]+)",
            r"Titular\s*:?\s*([A-Za-z\s]+)",
            r"Cliente\s*:?\s*([A-Za-z\s]+)",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                name = match.group(1).strip()
                # Limpar caracteres estranhos
                name = re.sub(r'[^A-Za-z\s]', '', name)
                # Remover espaços duplos
                name = re.sub(r'\s+', ' ', name)
                return name if name else None
        
        return None
    
    def _extract_address(self, text: str) -> Optional[Dict]:
        """Extrair morada do cliente."""
        result = {}
        
        # Procurar por morada - Formato: "Morada do Titular: Rua do Martinho 4, 4"
        address_pattern = r"Morada\s*do\s*Titular\s*:?\s*([A-Za-z0-9\s,.-]+)"
        address_match = re.search(address_pattern, text, re.IGNORECASE)
        if address_match:
            address = address_match.group(1).strip()
            # Limpar a morada
            address = re.sub(r'\s+', ' ', address)
            result["address"] = address
        
        # Procurar por código postal - Formato: "6290-241 Gouveia"
        postal_pattern = r"(\d{4}-\d{3})"
        postal_match = re.search(postal_pattern, text)
        if postal_match:
            result["postal_code"] = postal_match.group(1).strip()
        
        # Procurar por localidade
        if "Gouveia" in text:
            result["city"] = "Gouveia"
        elif "Carcavelos" in text:
            result["city"] = "Carcavelos"
        
        return result if result else None
    
    def _extract_client_number(self, text: str) -> Optional[str]:
        """Extrair número de cliente."""
        # Formato: "CPE: PT0002000042226072KF"
        patterns = [
            r"CPE\s*:?\s*(PT\d+)",
            r"N°\s*Cliente\s*:?\s*([A-Za-z0-9]+)",
            r"Cliente\s*n°\s*:?\s*([A-Za-z0-9]+)",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return None
    
    def _extract_iva(self, text: str) -> Optional[Dict]:
        """Extrair informações de IVA."""
        result = {}
        
        # Procurar por valor de IVA
        iva_pattern = r"IVA\s*:?\s*(\d+[.,]?\d*)\s*€"
        iva_match = re.search(iva_pattern, text, re.IGNORECASE)
        if iva_match:
            value = iva_match.group(1).replace(",", ".")
            try:
                result["value"] = float(value)
            except ValueError:
                pass
        
        # Taxa de IVA (normalmente 23% em Portugal)
        result["rate"] = 0.23
        
        return result if result else None
    
    def _extract_payment_info(self, text: str) -> Optional[Dict]:
        """Extrair informações de pagamento."""
        result = {}
        
        # Método de pagamento
        if "Débito na minha conta" in text:
            result["method"] = "Débito Direto"
        
        return result if result else None
    
    def _extract_meter_info(self, text: str) -> Optional[Dict]:
        """Extrair informações do contador."""
        # Por agora, não temos informações do contador nestas faturas
        return None
