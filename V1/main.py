#!/usr/bin/env python3
"""
Script principal para extração de dados de faturas de eletricidade em PDF.

Uso:
    python main.py <comando> [opções]

Comandos:
    extract    - Extrair dados de um ou mais PDFs
    directory  - Processar todos os PDFs num diretório
    test       - Testar a extração com um ficheiro de exemplo
"""

import argparse
import sys
import logging
from pathlib import Path
from typing import List

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('pdf_extractor.log')
    ]
)
logger = logging.getLogger(__name__)

# Adicionar o diretório pai ao path
sys.path.insert(0, str(Path(__file__).parent))

from pdf_extractor import PDFExtractor, SUPPORTED_PROVIDERS


def print_banner():
    """Imprimir banner do programa."""
    print("""
    ╔══════════════════════════════════════════════════════════════════╗
    ║   PDF Electricity Invoice Extractor                              ║
    ║   Extrai dados de faturas de eletricidade em PDF para XL        ║
    ╚══════════════════════════════════════════════════════════════════╝
    """)


def print_supported_providers():
    """Imprimir fornecedores suportados."""
    print("\nFornecedores suportados:")
    for provider in SUPPORTED_PROVIDERS:
        print(f"  - {provider}")
    print()


def command_extract(args):
    """
    Comando para extrair dados de um ou mais PDFs.
    
    Args:
        args: Argumentos da linha de comandos
    """
    print_banner()
    
    # Criar extrator
    extrator = PDFExtractor(use_ocr=args.ocr)
    
    # Processar ficheiros
    if not args.files:
        print("Erro: Não foram especificados ficheiros PDF")
        print("Uso: python main.py extract <ficheiro1.pdf> [ficheiro2.pdf ...]")
        sys.exit(1)
    
    # Verificar se os ficheiros existem
    valid_files = []
    for file_path in args.files:
        path = Path(file_path)
        if not path.exists():
            logger.error(f"Ficheiro não encontrado: {file_path}")
        else:
            valid_files.append(str(path))
    
    if not valid_files:
        logger.error("Nenhum ficheiro válido encontrado")
        sys.exit(1)
    
    # Extrair dados
    logger.info(f"A processar {len(valid_files)} ficheiro(s)...")
    results = extrator.extract_multiple(valid_files, use_ocr=args.ocr)
    
    # Exportar dados
    output_format = args.format if args.format else "csv"
    output_path = args.output if args.output else None
    
    if args.output:
        output_path = Path(args.output)
    
    logger.info(f"A exportar para formato {output_format}...")
    exported_path = extrator.export(results, format=output_format, output_path=output_path)
    
    logger.info(f"Sucesso! Dados exportados para: {exported_path}")
    
    # Mostrar amostra dos dados
    if results:
        print("\nAmostra dos dados extraídos:")
        sample = results[0]
        for key, value in list(sample.items())[:10]:
            print(f"  {key}: {value}")
        if len(sample) > 10:
            print(f"  ... e mais {len(sample) - 10} campos")


def command_directory(args):
    """
    Comando para processar todos os PDFs num diretório.
    
    Args:
        args: Argumentos da linha de comandos
    """
    print_banner()
    
    # Criar extrator
    extrator = PDFExtractor(use_ocr=args.ocr)
    
    # Processar diretório
    input_dir = args.input_dir
    output_format = args.format if args.format else "csv"
    
    logger.info(f"A processar diretório: {input_dir}")
    output_paths = extrator.process_directory(
        input_dir=input_dir,
        output_format=output_format,
        use_ocr=args.ocr
    )
    
    logger.info(f"Sucesso! Ficheiros criados:")
    for path in output_paths:
        logger.info(f"  - {path}")


def command_test(args):
    """
    Comando para testar a extração.
    
    Args:
        args: Argumentos da linha de comandos
    """
    print_banner()
    print_supported_providers()
    
    # Criar extrator
    extrator = PDFExtractor(use_ocr=args.ocr)
    
    # Mostrar informações
    print(f"Fornecedores suportados: {extrator.get_supported_providers()}")
    print(f"Diretório de saída padrão: {extrator.output_dir}")
    
    # Testar com um texto de exemplo
    sample_text = """
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
    
    print("\nA testar extração com texto de exemplo...")
    try:
        result = extrator.extract_from_text(sample_text)
        print("\nDados extraídos:")
        for key, value in result.items():
            if not key.startswith("_"):
                print(f"  {key}: {value}")
    except Exception as e:
        logger.error(f"Erro no teste: {e}")


def command_info(args):
    """
    Comando para mostrar informações sobre o sistema.
    
    Args:
        args: Argumentos da linha de comandos
    """
    print_banner()
    print_supported_providers()
    
    # Criar extrator
    extrator = PDFExtractor()
    
    print(f"Fornecedores com parsers disponíveis: {extrator.get_supported_providers()}")
    print(f"Diretório de saída padrão: {extrator.output_dir}")
    print(f"Formatos de exportação suportados: {EXPORT_FORMATS}")


def main():
    """Função principal."""
    parser = argparse.ArgumentParser(
        description='Extrair dados de faturas de eletricidade em PDF',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  python main.py extract fatura1.pdf fatura2.pdf
  python main.py extract fatura.pdf --format excel --output saida.xlsx
  python main.py directory ./faturas/ --format csv
  python main.py test
  python main.py info
        """
    )
    
    # Subcomandos
    subparsers = parser.add_subparsers(dest='command', help='Comandos disponíveis')
    
    # Comando extract
    extract_parser = subparsers.add_parser('extract', help='Extrair dados de PDFs')
    extract_parser.add_argument('files', nargs='+', help='Ficheiros PDF a processar')
    extract_parser.add_argument('--format', '-f', choices=['csv', 'json', 'excel'], 
                                help='Formato de saída (padrão: csv)')
    extract_parser.add_argument('--output', '-o', help='Ficheiro de saída')
    extract_parser.add_argument('--ocr', action='store_true', 
                                help='Usar OCR para extrair texto de imagens')
    
    # Comando directory
    directory_parser = subparsers.add_parser('directory', help='Processar diretório de PDFs')
    directory_parser.add_argument('input_dir', help='Diretório com os PDFs')
    directory_parser.add_argument('--format', '-f', choices=['csv', 'json', 'excel'],
                                  help='Formato de saída (padrão: csv)')
    directory_parser.add_argument('--ocr', action='store_true',
                                  help='Usar OCR para extrair texto de imagens')
    
    # Comando test
    test_parser = subparsers.add_parser('test', help='Testar a extração')
    test_parser.add_argument('--ocr', action='store_true',
                             help='Usar OCR no teste')
    
    # Comando info
    info_parser = subparsers.add_parser('info', help='Mostrar informações do sistema')
    
    # Parsear argumentos
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Executar comando
    if args.command == 'extract':
        command_extract(args)
    elif args.command == 'directory':
        command_directory(args)
    elif args.command == 'test':
        command_test(args)
    elif args.command == 'info':
        command_info(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()
