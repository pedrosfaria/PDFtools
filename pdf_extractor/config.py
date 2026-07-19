"""
Configurações do sistema de extração de PDFs
"""

# Fornecedores de energia suportados
SUPPORTED_PROVIDERS = [
    "edp",      # EDP - Energias de Portugal
    "galp",     # Galp Energia
    "ibersol",  # Ibersol
    "endesa",   # Endesa
    "goldenergy", # Goldenergy
    "luzboom",  # Luzboom
]

# Campos padrão a extrair de uma fatura de eletricidade
STANDARD_FIELDS = [
    "provider",           # Fornecedor
    "invoice_number",     # Número da fatura
    "issue_date",         # Data de emissão
    "due_date",           # Data de vencimento
    "consumption_period_start",  # Início do período de consumo
    "consumption_period_end",    # Fim do período de consumo
    "consumption_kwh",    # Consumo em kWh
    "power_contracted_kva",  # Potência contratada em kVA
    "price_per_kwh",      # Preço por kWh (€)
    "energy_cost",        # Custo da energia (€)
    "network_cost",       # Custo de acesso à rede (€)
    "iva_value",          # Valor do IVA (€)
    "iva_rate",           # Taxa de IVA (%)
    "total_amount",       # Total a pagar (€)
    "client_number",      # Número do cliente
    "nif",                # NIF do cliente
    "client_name",        # Nome do cliente
    "address",            # Morada
    "postal_code",        # Código postal
    "city",               # Localidade
    "payment_method",     # Método de pagamento
    "payment_reference",  # Referência de pagamento
    "meter_number",       # Número do contador
    "reading_date",       # Data da leitura
    "previous_reading",   # Leitura anterior
    "current_reading",    # Leitura atual
]

# Configuração de exportação
EXPORT_FORMATS = ["csv", "json", "excel"]
DEFAULT_EXPORT_FORMAT = "csv"
DEFAULT_OUTPUT_DIR = "data/output"

# Configuração de OCR (para PDFs com imagens)
OCR_CONFIG = {
    "enabled": True,
    "lang": "por+eng",
    "dpi": 300,
}

# Expressões regulares comuns
REGEX_PATTERNS = {
    "nif": r"\b\d{9}\b",
    "invoice_number": r"(?:Nº\s*Fatura|Fatura\s*nº|Invoice\s*No?\.?)\s*:?\s*([A-Z0-9\-\/\s]+)",
    "date": r"\b\d{2}[/-]\d{2}[/-]\d{4}\b|\b\d{4}[/-]\d{2}[/-]\d{2}\b",
    "amount": r"\b\d{1,3}(?:\.\d{3})*(?:,\d{2})?\s*€\b|\b€\s*\d{1,3}(?:\.\d{3})*(?:,\d{2})?\b",
    "kwh": r"\b\d{1,7}(?:\.\d{3})*(?:,\d+)?\s*kWh\b",
    "kva": r"\b\d{1,3}(?:\.\d{3})*(?:,\d+)?\s*kVA\b",
}
