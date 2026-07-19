#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script simples para testar upload e extracao de faturas PDF.

Uso:
    python test_upload.py "caminho/para/fatura.pdf"

Exemplo:
    python test_upload.py "faturas_fornecedores/coopernico/faturacoop.pdf"
"""

import sys
import json
from pathlib import Path

# Adicionar o diretorio ao path
sys.path.insert(0, str(Path(__file__).parent))

from pdf_extractor import PDFExtractor
from pdf_extractor.extractor import extract_text_from_pdf

def test_pdf_extraction(pdf_path):
    """Testa a extracao de texto de um PDF."""
    print(f"\n{'='*60}")
    print(f"TESTANDO EXTRACAO: {pdf_path}")
    print(f"{'='*60}\n")
    
    try:
        # Verificar se o ficheiro existe
        pdf_path = Path(pdf_path)
        if not pdf_path.exists():
            print(f"❌ ERRO: Ficheiro nao encontrado: {pdf_path}")
            return None
        
        # Extrair texto
        print("📄 A extrair texto do PDF...")
        text = extract_text_from_pdf(str(pdf_path))
        
        if not text or len(text.strip()) == 0:
            print("⚠️  AVISO: Nenhum texto extraido. O PDF pode ser uma imagem (scan).")
            print("   Tente usar OCR com: PDFExtractor(use_ocr=True)")
            return None
        
        print(f"✅ SUCESSO: Extraido {len(text)} caracteres")
        print(f"\n{'='*60}")
        print("TEXTO EXTRAIDO (primeiros 1000 caracteres):")
        print(f"{'='*60}")
        print(text[:1000])
        if len(text) > 1000:
            print(f"\n... (e mais {len(text) - 1000} caracteres)")
        
        # Tentar extrair dados com o extrator
        print(f"\n{'='*60}")
        print("A EXTRATIR DADOS ESTRUTURADOS...")
        print(f"{'='*60}\n")
        
        extractor = PDFExtractor(use_ocr=False)
        result = extractor.extract_from_pdf(str(pdf_path))
        
        if result:
            print("✅ Dados extraidos com sucesso:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print("⚠️  Nenhum dado estruturado extraido.")
        
        return result
        
    except Exception as e:
        print(f"❌ ERRO: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """Funcao principal."""
    print("="*60)
    print("TEST UPLOAD - Extrator de Faturas PDF")
    print("="*60)
    
    if len(sys.argv) < 2:
        print("\nUso:")
        print("  python test_upload.py <caminho_para_fatura.pdf>")
        print("\nExemplo:")
        print("  python test_upload.py faturas_fornecedores/coopernico/faturacoop.pdf")
        print("\nFicheiros de exemplo disponiveis:")
        
        # Listar ficheiros PDF disponiveis
        pdf_files = list(Path("faturas_fornecedores").rglob("*.pdf"))
        if pdf_files:
            print("\n📁 Ficheiros PDF encontrados:")
            for i, pdf in enumerate(pdf_files[:10], 1):  # Mostrar primeiros 10
                print(f"  {i}. {pdf}")
            if len(pdf_files) > 10:
                print(f"  ... e mais {len(pdf_files) - 10} ficheiros")
        else:
            print("\n⚠️  Nenhum ficheiro PDF encontrado na pasta 'faturas_fornecedores'")
        
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    result = test_pdf_extraction(pdf_path)
    
    if result:
        print(f"\n{'='*60}")
        print("✅ TESTE CONCLUIDO COM SUCESSO")
        print(f"{'='*60}")
    else:
        print(f"\n{'='*60}")
        print("❌ TESTE FALHOU")
        print(f"{'='*60}")
        sys.exit(1)

if __name__ == "__main__":
    main()
