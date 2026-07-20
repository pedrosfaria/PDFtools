#!/usr/bin/env python3
"""
Exemplo de uso do PDF Extractor

Este script demonstra como usar o sistema de extração de dados de faturas
em diferentes cenários.
"""

import sys
from pathlib import Path

# Adicionar o diretório ao path
sys.path.insert(0, str(Path(__file__).parent))

from pdf_extractor import PDFExtractor


def example_1_basic_extraction():
    """Exemplo 1: Extração básica de texto."""
    print("=" * 60)
    print("Exemplo 1: Extração básica de texto")
    print("=" * 60)
    
    # Criar extrator
    extractor = PDFExtractor()
    
    # Texto de exemplo de uma fatura EDP
    text = """
    EDP - Energias de Portugal
    Fatura nº: FA202400123456
    Data Emissão: 15-01-2024
    Data Vencimento: 30-01-2024
    
    Cliente: João Silva
    NIF: 123456789
    Morada: Rua da Liberdade, 123
    Código Postal: 1234-567
    Localidade: Lisboa
    
    Período de Consumo: 01-12-2023 a 31-12-2023
    Consumo Total: 350,50 kWh
    Potência Contratada: 6,90 kVA
    
    Preço da Energia: 0,15 €/kWh
    Custo da Energia: 52,58 €
    Acesso à Rede: 12,34 €
    IVA (23%): 14,68 €
    
    Total a Pagar: 79,60 €
    """
    
    # Extrair dados
    data = extractor.extract_from_text(text)
    
    # Mostrar resultados
    print("\nDados extraídos:")
    for key, value in data.items():
        if not key.startswith("_"):
            print(f"  {key:25}: {value}")
    
    print()


def example_2_multiple_invoices():
    """Exemplo 2: Processar múltiplas faturas."""
    print("=" * 60)
    print("Exemplo 2: Processar múltiplas faturas")
    print("=" * 60)
    
    # Criar extrator
    extractor = PDFExtractor()
    
    # Lista de textos de faturas
    invoices = [
        """
        EDP
        Fatura: FA001
        Data: 01-01-2024
        Consumo: 200 kWh
        Total: 45,00 €
        Cliente: Ana Costa
        NIF: 111111111
        """,
        """
        Galp Energia
        Fatura: GALP002
        Data: 02-01-2024
        Consumo: 250 kWh
        Total: 55,00 €
        Cliente: Pedro Santos
        NIF: 222222222
        """,
        """
        Ibersol
        Fatura: IB003
        Data: 03-01-2024
        Consumo: 300 kWh
        Total: 65,00 €
        Cliente: Maria Silva
        NIF: 333333333
        """
    ]
    
    # Extrair dados de todas as faturas
    all_data = []
    for i, text in enumerate(invoices, 1):
        data = extractor.extract_from_text(text)
        all_data.append(data)
        print(f"\nFatura {i} ({data.get('provider', 'desconhecido')}):")
        print(f"  Número: {data.get('invoice_number', 'N/A')}")
        print(f"  Cliente: {data.get('client_name', 'N/A')}")
        print(f"  Consumo: {data.get('consumption_kwh', 'N/A')} kWh")
        print(f"  Total: {data.get('total_amount', 'N/A')} €")
    
    print()


def example_3_export_to_csv():
    """Exemplo 3: Exportar para CSV."""
    print("=" * 60)
    print("Exemplo 3: Exportar para CSV")
    print("=" * 60)
    
    # Criar extrator
    extractor = PDFExtractor()
    
    # Dados de exemplo
    data = [
        {
            "provider": "edp",
            "invoice_number": "FA001",
            "issue_date": "01-01-2024",
            "due_date": "15-01-2024",
            "consumption_kwh": 200.0,
            "total_amount": 45.0,
            "client_name": "Ana Costa",
            "nif": "111111111"
        },
        {
            "provider": "galp",
            "invoice_number": "GALP002",
            "issue_date": "02-01-2024",
            "due_date": "16-01-2024",
            "consumption_kwh": 250.0,
            "total_amount": 55.0,
            "client_name": "Pedro Santos",
            "nif": "222222222"
        }
    ]
    
    # Exportar para CSV
    output_path = "example_output.csv"
    exported_path = extractor.export_to_csv(data, output_path)
    
    print(f"\nDados exportados para: {exported_path}")
    
    # Mostrar conteúdo do ficheiro
    with open(exported_path, 'r', encoding='utf-8') as f:
        content = f.read()
        print("\nConteúdo do CSV:")
        print(content)
    
    print()


def example_4_export_to_json():
    """Exemplo 4: Exportar para JSON."""
    print("=" * 60)
    print("Exemplo 4: Exportar para JSON")
    print("=" * 60)
    
    # Criar extrator
    extractor = PDFExtractor()
    
    # Dados de exemplo
    data = {
        "provider": "edp",
        "invoice_number": "FA001",
        "total_amount": 45.0,
        "client_name": "Ana Costa"
    }
    
    # Exportar para JSON
    output_path = "example_output.json"
    exported_path = extractor.export_to_json(data, output_path)
    
    print(f"\nDados exportados para: {exported_path}")
    
    # Mostrar conteúdo do ficheiro
    with open(exported_path, 'r', encoding='utf-8') as f:
        content = f.read()
        print("\nConteúdo do JSON:")
        print(content)
    
    print()


def example_5_export_to_excel():
    """Exemplo 5: Exportar para Excel."""
    print("=" * 60)
    print("Exemplo 5: Exportar para Excel")
    print("=" * 60)
    
    try:
        import pandas as pd
        import openpyxl
    except ImportError:
        print("Bibliotecas pandas ou openpyxl não estão instaladas")
        print("Instale com: pip install pandas openpyxl")
        return
    
    # Criar extrator
    extractor = PDFExtractor()
    
    # Dados de exemplo
    data = [
        {
            "provider": "edp",
            "invoice_number": "FA001",
            "consumption_kwh": 200.0,
            "total_amount": 45.0
        },
        {
            "provider": "galp",
            "invoice_number": "GALP002",
            "consumption_kwh": 250.0,
            "total_amount": 55.0
        }
    ]
    
    # Exportar para Excel
    output_path = "example_output.xlsx"
    exported_path = extractor.export_to_excel(data, output_path)
    
    print(f"\nDados exportados para: {exported_path}")
    
    # Mostrar informação do ficheiro
    df = pd.read_excel(exported_path)
    print(f"\nFicheiro Excel criado com {len(df)} linhas")
    print(f"Colunas: {list(df.columns)}")
    
    print()


def example_6_custom_parser():
    """Exemplo 6: Usar um parser personalizado."""
    print("=" * 60)
    print("Exemplo 6: Usar um parser personalizado")
    print("=" * 60)
    
    from pdf_extractor.parsers.base_parser import BaseInvoiceParser
    from typing import Dict
    import re
    
    # Criar um parser personalizado
    class CustomParser(BaseInvoiceParser):
        def __init__(self):
            super().__init__()
            self.provider_name = "custom"
        
        def detect(self, text: str) -> bool:
            return "Custom Energy" in text
        
        def parse(self, text: str) -> Dict:
            self.reset()
            self.raw_text = text
            
            data = {
                "provider": self.provider_name,
                "invoice_number": self._extract_custom_invoice_number(text),
                "total_amount": self._extract_total_amount(text),
                "client_name": self._extract_client_name(text)
            }
            
            self.extracted_data = data
            return data
        
        def _extract_custom_invoice_number(self, text: str):
            pattern = r"Invoice\s*No?\.?\s*:?\s*([A-Z0-9\-\s]+)"
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
            return None
    
    # Criar extrator e adicionar parser
    extractor = PDFExtractor()
    extractor.add_custom_parser("custom", CustomParser())
    
    # Testar com texto personalizado
    text = """
    Custom Energy
    Invoice No: CUST-2024-001
    Total Amount: $100.00
    Client: John Doe
    """
    
    data = extractor.extract_from_text(text)
    
    print("\nDados extraídos com parser personalizado:")
    for key, value in data.items():
        if not key.startswith("_"):
            print(f"  {key:25}: {value}")
    
    print()


def example_7_process_directory():
    """Exemplo 7: Processar um diretório de PDFs."""
    print("=" * 60)
    print("Exemplo 7: Processar um diretório de PDFs")
    print("=" * 60)
    
    # Criar extrator
    extractor = PDFExtractor()
    
    # Verificar se o diretório data/input existe
    input_dir = Path("data/input")
    if not input_dir.exists():
        print(f"\nDiretório {input_dir} não existe")
        print("Crie o diretório e adicione ficheiros PDF para testar")
        return
    
    # Listar ficheiros PDF
    pdf_files = list(input_dir.glob("*.pdf")) + list(input_dir.glob("*.PDF"))
    
    if not pdf_files:
        print(f"\nNão foram encontrados ficheiros PDF em {input_dir}")
        return
    
    print(f"\nEncontrados {len(pdf_files)} ficheiros PDF em {input_dir}")
    
    # Processar diretório
    output_files = extractor.process_directory(
        input_dir=str(input_dir),
        output_format="csv"
    )
    
    print(f"\nFicheiros criados:")
    for f in output_files:
        print(f"  - {f}")
    
    print()


def main():
    """Função principal."""
    print("\n" + "=" * 60)
    print("PDF Electricity Invoice Extractor - Exemplos de Uso")
    print("=" * 60 + "\n")
    
    # Executar exemplos
    examples = [
        ("Extração básica", example_1_basic_extraction),
        ("Múltiplas faturas", example_2_multiple_invoices),
        ("Exportar para CSV", example_3_export_to_csv),
        ("Exportar para JSON", example_4_export_to_json),
        ("Exportar para Excel", example_5_export_to_excel),
        ("Parser personalizado", example_6_custom_parser),
        ("Processar diretório", example_7_process_directory),
    ]
    
    for i, (name, func) in enumerate(examples, 1):
        print(f"[{i}] {name}")
    
    print(f"\n[0] Executar todos")
    print(f"[Q] Sair")
    
    choice = input("\nSelecionar exemplo (número ou Q): ").strip().upper()
    
    if choice == "Q":
        return
    elif choice == "0":
        for _, func in examples:
            try:
                func()
            except Exception as e:
                print(f"Erro no exemplo: {e}")
    else:
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(examples):
                examples[idx][1]()
            else:
                print("Opção inválida")
        except ValueError:
            print("Opção inválida")


if __name__ == '__main__':
    main()
