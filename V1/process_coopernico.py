#!/usr/bin/env python3
"""
Script simplificado para processar faturas da Coopérnico.

Uso:
    python process_coopernico.py <comando> [opções]

Comandos:
    single <ficheiro.pdf>          - Processar um ficheiro
    directory <pasta/>            - Processar todos os PDFs numa pasta
    test                          - Testar com dados de exemplo
"""

import sys
import os
from pathlib import Path

# Adicionar o diretório ao path
sys.path.insert(0, str(Path(__file__).parent))

from pdf_extractor import PDFExtractor


def print_header():
    """Imprimir cabeçalho."""
    print("""
    ╔══════════════════════════════════════════════════════════════════╗
    ║   Coopérnico Invoice Extractor                               ║
    ║   Extrai dados de faturas da Coopérnico para Excel/CSV       ║
    ╚══════════════════════════════════════════════════════════════════╝
    """)


def process_single_file(file_path, output_format="csv", output_path=None, use_ocr=False):
    """
    Processar um único ficheiro PDF.
    
    Args:
        file_path: Caminho para o ficheiro PDF
        output_format: Formato de saída (csv, json, excel)
        output_path: Caminho de saída (opcional)
        use_ocr: Usar OCR para PDFs com imagens
    """
    print_header()
    
    file_path = Path(file_path)
    
    if not file_path.exists():
        print(f"❌ Erro: Ficheiro não encontrado: {file_path}")
        return None
    
    print(f"📄 A processar: {file_path.name}")
    
    # Criar extrator
    extractor = PDFExtractor(use_ocr=use_ocr)
    
    try:
        # Extrair dados
        data = extractor.extract_from_pdf(str(file_path), use_ocr=use_ocr)
        
        # Definir caminho de saída
        if not output_path:
            output_path = file_path.parent / f"{file_path.stem}.{output_format}"
        else:
            output_path = Path(output_path)
        
        # Exportar
        print(f"📤 A exportar para {output_format.upper()}...")
        result_path = extractor.export(data, format=output_format, output_path=str(output_path))
        
        print(f"✅ Sucesso! Dados exportados para: {result_path}")
        
        # Mostrar amostra dos dados
        print("\n📊 Dados extraídos:")
        important_fields = [
            "provider", "invoice_number", "issue_date", "due_date",
            "consumption_kwh", "total_amount", "client_name", "nif"
        ]
        for field in important_fields:
            if field in data:
                print(f"   {field:20}: {data[field]}")
        
        return result_path
        
    except Exception as e:
        print(f"❌ Erro a processar {file_path}: {e}")
        return None


def process_directory(input_dir, output_format="csv", output_path=None, use_ocr=False):
    """
    Processar todos os PDFs num diretório.
    
    Args:
        input_dir: Diretório com os PDFs
        output_format: Formato de saída
        output_path: Caminho de saída (opcional)
        use_ocr: Usar OCR
    """
    print_header()
    
    input_dir = Path(input_dir)
    
    if not input_dir.exists():
        print(f"❌ Erro: Diretório não encontrado: {input_dir}")
        return []
    
    # Encontrar todos os PDFs
    pdf_files = list(input_dir.glob("*.pdf")) + list(input_dir.glob("*.PDF"))
    
    if not pdf_files:
        print(f"⚠️  Não foram encontrados ficheiros PDF em: {input_dir}")
        return []
    
    print(f"📁 Encontrados {len(pdf_files)} ficheiros PDF em: {input_dir}")
    
    # Criar extrator
    extractor = PDFExtractor(use_ocr=use_ocr)
    
    # Processar todos os ficheiros
    all_data = []
    success_count = 0
    error_count = 0
    
    for pdf_file in pdf_files:
        try:
            print(f"\n📄 A processar: {pdf_file.name}...")
            data = extractor.extract_from_pdf(str(pdf_file), use_ocr=use_ocr)
            all_data.append(data)
            success_count += 1
            print(f"   ✅ Processado com sucesso")
        except Exception as e:
            error_count += 1
            print(f"   ❌ Erro: {e}")
            all_data.append({"_source_file": str(pdf_file), "_error": str(e)})
    
    # Exportar todos os dados
    if not output_path:
        output_path = input_dir / f"faturas_coopernico.{output_format}"
    else:
        output_path = Path(output_path)
    
    print(f"\n📤 A exportar {len(all_data)} faturas para: {output_path}")
    result_path = extractor.export(all_data, format=output_format, output_path=str(output_path))
    
    print(f"\n✅ Sucesso!")
    print(f"   Ficheiros processados: {success_count}")
    print(f"   Erros: {error_count}")
    print(f"   Saída: {result_path}")
    
    return [result_path]


def test_extraction():
    """Testar a extração com dados de exemplo da Coopérnico."""
    print_header()
    print("🧪 A testar extração com dados de exemplo da Coopérnico...\n")
    
    # Criar extrator
    extractor = PDFExtractor()
    
    # Texto de exemplo de uma fatura Coopérnico
    sample_text = """
    Coopérnico - Cooperativa de Energia
    
    Fatura nº: COOP-2024-001234
    Data Emissão: 15-01-2024
    Data Vencimento: 30-01-2024
    
    Sócio: João Silva
    NIF: 123456789
    Morada: Rua da Cooperativa, 123
    Código Postal: 1234-567
    Localidade: Lisboa
    
    Período de Consumo: 01-12-2023 a 31-12-2023
    Consumo: 350,50 kWh
    Potência Contratada: 6,90 kVA
    
    Preço da Energia: 0,14 €/kWh
    Custo da Energia: 49,07 €
    Acesso à Rede: 10,50 €
    IVA (23%): 13,84 €
    
    Total a Pagar: 73,41 €
    
    Nº Contador: COOP123456
    Leitura Atual: 12345
    Leitura Anterior: 12000
    Data da Leitura: 31-12-2023
    
    Referência: 123 456 789
    Método de Pagamento: Transferência Bancária
    """
    
    # Extrair dados
    data = extractor.extract_from_text(sample_text)
    
    # Mostrar resultados
    print("✅ Dados extraídos com sucesso:\n")
    for key, value in data.items():
        if not key.startswith("_"):
            print(f"   {key:25}: {value}")
    
    # Exportar para CSV
    output_path = "test_coopernico.csv"
    exported = extractor.export_to_csv([data], output_path)
    print(f"\n📄 Ficheiro de teste criado: {exported}")
    
    # Mostrar conteúdo do CSV
    with open(exported, 'r', encoding='utf-8') as f:
        content = f.read()
        print("\n📊 Conteúdo do CSV:")
        print(content)


def main():
    """Função principal."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Processar faturas da Coopérnico',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  python process_coopernico.py single fatura.pdf
  python process_coopernico.py single fatura.pdf --format excel
  python process_coopernico.py directory ./faturas/
  python process_coopernico.py directory ./faturas/ --format excel --output saida.xlsx
  python process_coopernico.py test
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Comandos disponíveis')
    
    # Comando single
    single_parser = subparsers.add_parser('single', help='Processar um ficheiro')
    single_parser.add_argument('file', help='Ficheiro PDF a processar')
    single_parser.add_argument('--format', '-f', choices=['csv', 'json', 'excel'], 
                                default='csv', help='Formato de saída (padrão: csv)')
    single_parser.add_argument('--output', '-o', help='Ficheiro de saída')
    single_parser.add_argument('--ocr', action='store_true',
                                help='Usar OCR para PDFs com imagens')
    
    # Comando directory
    dir_parser = subparsers.add_parser('directory', help='Processar um diretório')
    dir_parser.add_argument('input_dir', help='Diretório com os PDFs')
    dir_parser.add_argument('--format', '-f', choices=['csv', 'json', 'excel'],
                             default='csv', help='Formato de saída (padrão: csv)')
    dir_parser.add_argument('--output', '-o', help='Ficheiro de saída')
    dir_parser.add_argument('--ocr', action='store_true',
                             help='Usar OCR para PDFs com imagens')
    
    # Comando test
    test_parser = subparsers.add_parser('test', help='Testar com dados de exemplo')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    if args.command == 'single':
        process_single_file(
            args.file,
            output_format=args.format,
            output_path=args.output,
            use_ocr=args.ocr
        )
    elif args.command == 'directory':
        process_directory(
            args.input_dir,
            output_format=args.format,
            output_path=args.output,
            use_ocr=args.ocr
        )
    elif args.command == 'test':
        test_extraction()
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()
