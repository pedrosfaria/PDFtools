# PDF Electricity Invoice Extractor

Sistema para extrair dados de faturas de eletricidade em PDF e exportar para formatos processáveis no Excel (CSV, JSON, Excel).

## 📋 Visão Geral

Este sistema permite:
- Ler ficheiros PDF de faturas de eletricidade
- Identificar automaticamente o fornecedor (EDP, Galp, Ibersol, etc.)
- Extrair dados estruturados (consumo, valores, datas, etc.)
- Exportar para CSV, JSON ou Excel
- Processar múltiplos ficheiros em batch

## 🏗️ Arquitetura

```
PDFtools/
├── pdf_extractor/                    # Pacote principal
│   ├── __init__.py
│   ├── extractor.py                 # Motor de extração
│   ├── config.py                    # Configurações
│   ├── parsers/                     # Parsers por fornecedor
│   │   ├── __init__.py
│   │   ├── base_parser.py           # Classe base
│   │   ├── edp_parser.py            # Parser EDP
│   │   ├── galp_parser.py           # Parser Galp
│   │   └── ibersol_parser.py        # Parser Ibersol
│   └── utils/                       # Funções utilitárias
│       ├── __init__.py
│       ├── pdf_utils.py             # Utilitários PDF
│       ├── text_utils.py            # Utilitários texto
│       └── ocr_utils.py             # Utilitários OCR
├── data/
│   ├── input/                       # PDFs de entrada
│   └── output/                      # Ficheiros de saída
├── tests/                           # Testes
├── main.py                         # Script principal
├── requirements.txt                 # Dependências
└── README.md
```

## 📦 Instalação

### Pré-requisitos

- Python 3.8 ou superior
- pip

### Instalar dependências

```bash
# Criar ambiente virtual (recomendado)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Instalar dependências
pip install -r requirements.txt
```

### Dependências opcionais (OCR)

Para extrair texto de PDFs com imagens (scans):

```bash
# Instalar Tesseract OCR
# Ubuntu/Debian:
sudo apt install tesseract-ocr
sudo apt install libtesseract-dev
sudo apt install tesseract-ocr-por  # Português
sudo apt install tesseract-ocr-eng  # Inglês

# Mac:
brew install tesseract

# Windows:
# Baixar instalador de: https://github.com/UB-Mannheim/tesseract/wiki

# Instalar biblioteca Python
pip install pytesseract pillow
```

## 🚀 Uso

### Comando básico

```bash
# Extrair dados de um PDF
python main.py extract fatura_edp.pdf

# Extrair dados de múltiplos PDFs
python main.py extract fatura1.pdf fatura2.pdf fatura3.pdf

# Processar todos os PDFs num diretório
python main.py directory ./faturas/
```

### Opções de exportação

```bash
# Exportar para CSV (padrão)
python main.py extract fatura.pdf --format csv --output saida.csv

# Exportar para Excel
python main.py extract fatura.pdf --format excel --output saida.xlsx

# Exportar para JSON
python main.py extract fatura.pdf --format json --output saida.json
```

### Usar OCR (para PDFs com imagens)

```bash
# Ativar OCR para um ficheiro
python main.py extract fatura_scan.pdf --ocr

# Ativar OCR para um diretório
python main.py directory ./scans/ --ocr
```

### Testar o sistema

```bash
# Executar teste com dados de exemplo
python main.py test

# Mostrar informações do sistema
python main.py info
```

## 📊 Dados Extraídos

O sistema extrai os seguintes campos padrão das faturas:

### Informações da Fatura
- `provider` - Fornecedor (EDP, Galp, Ibersol, etc.)
- `invoice_number` - Número da fatura
- `issue_date` - Data de emissão
- `due_date` - Data de vencimento

### Período de Consumo
- `consumption_period_start` - Início do período
- `consumption_period_end` - Fim do período
- `consumption_kwh` - Consumo em kWh
- `power_contracted_kva` - Potência contratada em kVA

### Valores Monetários
- `price_per_kwh` - Preço por kWh (€)
- `energy_cost` - Custo da energia (€)
- `network_cost` - Custo de acesso à rede (€)
- `iva_rate` - Taxa de IVA (%)
- `iva_value` - Valor do IVA (€)
- `total_amount` - Total a pagar (€)

### Informações do Cliente
- `client_number` - Número do cliente
- `nif` - NIF do cliente
- `client_name` - Nome do cliente
- `address` - Morada
- `postal_code` - Código postal
- `city` - Localidade

### Informações de Pagamento
- `payment_method` - Método de pagamento
- `payment_reference` - Referência de pagamento

### Informações do Contador
- `meter_number` - Número do contador
- `reading_date` - Data da leitura
- `previous_reading` - Leitura anterior
- `current_reading` - Leitura atual

## 🔧 Personalização

### Adicionar um novo fornecedor

1. Criar um novo parser em `pdf_extractor/parsers/`:

```python
from .base_parser import BaseInvoiceParser
from typing import Dict, Optional
import re

class NovoFornecedorParser(BaseInvoiceParser):
    def __init__(self):
        super().__init__()
        self.provider_name = "novo_fornecedor"
    
    def detect(self, text: str) -> bool:
        # Detetar se o texto é deste fornecedor
        return "Novo Fornecedor" in text
    
    def parse(self, text: str) -> Dict:
        # Implementar parsing específico
        data = super().parse(text)
        # Adicionar lógica específica
        return data
```

2. Adicionar o parser ao ficheiro `__init__.py`:

```python
from .novo_fornecedor_parser import NovoFornecedorParser

PARSERS = {
    "edp": EDPParser,
    "galp": GalpParser,
    "ibersol": IbersolParser,
    "novo_fornecedor": NovoFornecedorParser,  # Adicionar aqui
}
```

### Usar como biblioteca

```python
from pdf_extractor import PDFExtractor

# Criar extrator
extractor = PDFExtractor(use_ocr=False)

# Extrair de um PDF
data = extrator.extract_from_pdf("fatura.pdf")

# Extrair de texto diretamente
data = extrator.extract_from_text("Fatura nº: 12345...")

# Exportar para CSV
extractor.export_to_csv(data, "saida.csv")

# Exportar para Excel
extractor.export_to_excel(data, "saida.xlsx")
```

## 📁 Estrutura dos Dados de Saída

### CSV

```csv
provider,invoice_number,issue_date,due_date,consumption_kwh,total_amount,client_name,nif
edp,FA202400123456,15-01-2024,30-01-2024,350.5,79.60,João Silva,123456789
```

### JSON

```json
[
  {
    "provider": "edp",
    "invoice_number": "FA202400123456",
    "issue_date": "15-01-2024",
    "due_date": "30-01-2024",
    "consumption_kwh": 350.5,
    "total_amount": 79.60,
    "client_name": "João Silva",
    "nif": "123456789"
  }
]
```

### Excel

Cria um ficheiro Excel com uma folha contendo todos os dados em formato tabular.

## 🔍 Resolução de Problemas

### Erro: "Não foi possível extrair texto do PDF"

- Verifique se o ficheiro PDF não está corrompido
- Tente usar a opção `--ocr` para PDFs com imagens
- Instale o Tesseract OCR se ainda não o fez

### Erro: "Parser não disponível para fornecedor"

- O fornecedor pode não estar suportado
- Adicione um parser personalizado (ver secção de personalização)

### OCR não funciona

- Verifique se o Tesseract está instalado
- Verifique se as linguagens estão instaladas (por, eng)
- Teste com: `tesseract --list-langs`

## 📝 Licença

Este projeto é de código aberto e pode ser usado livremente.

## 🤝 Contribuições

Contribuições são bem-vindas! Por favor abra um issue ou submeta um pull request.

## 📞 Suporte

Para questões ou problemas, por favor abra um issue no repositório.
