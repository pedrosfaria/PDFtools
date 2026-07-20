"""
Testes para o extrator de faturas de eletricidade
"""

import unittest
import tempfile
import os
from pathlib import Path
import json

# Adicionar o diretório pai ao path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from pdf_extractor import PDFExtractor
from pdf_extractor.parsers import EDPParser, GalpParser, IbersolParser


class TestPDFExtractor(unittest.TestCase):
    """Testes para a classe PDFExtractor."""
    
    def setUp(self):
        """Configurar testes."""
        self.extractor = PDFExtractor(use_ocr=False)
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Limpar após testes."""
        # Remover ficheiros temporários
        for f in Path(self.temp_dir).glob("*"):
            f.unlink()
        Path(self.temp_dir).rmdir()
    
    def test_extractor_initialization(self):
        """Testar inicialização do extrator."""
        self.assertIsNotNone(self.extractor)
        self.assertFalse(self.extractor.use_ocr)
        self.assertEqual(len(self.extractor.parsers), 3)  # EDP, Galp, Ibersol
    
    def test_extract_from_text_edp(self):
        """Testar extração de texto EDP."""
        text = """
        EDP - Energias de Portugal
        Fatura nº: FA202400123456
        Data Emissão: 15-01-2024
        Data Vencimento: 30-01-2024
        
        Cliente: João Silva
        NIF: 123456789
        
        Período de Consumo: 01-12-2023 a 31-12-2023
        Consumo Total: 350,50 kWh
        
        Total a Pagar: 79,60 €
        """
        
        result = self.extractor.extract_from_text(text)
        
        self.assertEqual(result["provider"], "edp")
        self.assertEqual(result["invoice_number"], "FA202400123456")
        self.assertEqual(result["issue_date"], "15-01-2024")
        self.assertEqual(result["due_date"], "30-01-2024")
        self.assertAlmostEqual(result["consumption_kwh"], 350.50, places=2)
        self.assertAlmostEqual(result["total_amount"], 79.60, places=2)
        self.assertEqual(result["client_name"], "João Silva")
        self.assertEqual(result["nif"], "123456789")
    
    def test_extract_from_text_galp(self):
        """Testar extração de texto Galp."""
        text = """
        Galp Energia
        Fatura: GALP202400789
        Emitida em: 10-01-2024
        Vence em: 25-01-2024
        
        Titular: Maria Santos
        NIF: 987654321
        
        Consumo: 280 kWh
        
        Total: 65,40 €
        """
        
        result = self.extractor.extract_from_text(text)
        
        self.assertEqual(result["provider"], "galp")
        self.assertEqual(result["invoice_number"], "GALP202400789")
        self.assertEqual(result["issue_date"], "10-01-2024")
        self.assertAlmostEqual(result["consumption_kwh"], 280.0, places=2)
        self.assertAlmostEqual(result["total_amount"], 65.40, places=2)
    
    def test_extract_from_text_ibersol(self):
        """Testar extração de texto Ibersol."""
        text = """
        Ibersol
        Fatura nº IB202400456
        Data: 05-01-2024
        Vencimento: 20-01-2024
        
        Cliente: Carlos Pereira
        NIF: 111222333
        
        kWh Consumidos: 420,25
        
        Total Fatura: 89,90 €
        """
        
        result = self.extractor.extract_from_text(text)
        
        self.assertEqual(result["provider"], "ibersol")
        self.assertEqual(result["invoice_number"], "IB202400456")
        self.assertAlmostEqual(result["consumption_kwh"], 420.25, places=2)
        self.assertAlmostEqual(result["total_amount"], 89.90, places=2)
    
    def test_export_to_csv(self):
        """Testar exportação para CSV."""
        data = [
            {
                "provider": "edp",
                "invoice_number": "FA001",
                "total_amount": 100.0,
                "client_name": "Teste 1"
            },
            {
                "provider": "galp",
                "invoice_number": "FA002",
                "total_amount": 200.0,
                "client_name": "Teste 2"
            }
        ]
        
        output_path = os.path.join(self.temp_dir, "test.csv")
        result_path = self.extractor.export_to_csv(data, output_path)
        
        self.assertTrue(os.path.exists(result_path))
        
        # Verificar conteúdo
        with open(result_path, 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIn("provider", content)
            self.assertIn("FA001", content)
            self.assertIn("FA002", content)
    
    def test_export_to_json(self):
        """Testar exportação para JSON."""
        data = {
            "provider": "edp",
            "invoice_number": "FA001",
            "total_amount": 100.0
        }
        
        output_path = os.path.join(self.temp_dir, "test.json")
        result_path = self.extractor.export_to_json(data, output_path)
        
        self.assertTrue(os.path.exists(result_path))
        
        # Verificar conteúdo
        with open(result_path, 'r', encoding='utf-8') as f:
            loaded_data = json.load(f)
            self.assertEqual(loaded_data[0]["provider"], "edp")
            self.assertEqual(loaded_data[0]["invoice_number"], "FA001")
    
    def test_export_to_excel(self):
        """Testar exportação para Excel."""
        try:
            import pandas as pd
            import openpyxl
        except ImportError:
            self.skipTest("Bibliotecas pandas ou openpyxl não estão instaladas")
        
        data = [
            {
                "provider": "edp",
                "invoice_number": "FA001",
                "total_amount": 100.0
            },
            {
                "provider": "galp",
                "invoice_number": "FA002",
                "total_amount": 200.0
            }
        ]
        
        output_path = os.path.join(self.temp_dir, "test.xlsx")
        result_path = self.extractor.export_to_excel(data, output_path)
        
        self.assertTrue(os.path.exists(result_path))
        
        # Verificar conteúdo
        df = pd.read_excel(result_path)
        self.assertEqual(len(df), 2)
        self.assertIn("provider", df.columns)
        self.assertIn("invoice_number", df.columns)
    
    def test_get_supported_providers(self):
        """Testar obtenção de fornecedores suportados."""
        providers = self.extractor.get_supported_providers()
        
        self.assertIn("edp", providers)
        self.assertIn("galp", providers)
        self.assertIn("ibersol", providers)


class TestEDPParser(unittest.TestCase):
    """Testes para o parser EDP."""
    
    def setUp(self):
        """Configurar testes."""
        self.parser = EDPParser()
    
    def test_detect_edp(self):
        """Testar deteção de fatura EDP."""
        text = "EDP - Energias de Portugal"
        self.assertTrue(self.parser.detect(text))
        
        text = "Fatura EDP"
        self.assertTrue(self.parser.detect(text))
        
        text = "Galp Energia"
        self.assertFalse(self.parser.detect(text))
    
    def test_parse_edp_invoice(self):
        """Testar parsing de fatura EDP."""
        text = """
        EDP Comercial
        Nº Fatura: FA202400123456
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
        
        Nº Contador: ED12345678
        Leitura Atual: 12345
        Leitura Anterior: 12000
        Data da Leitura: 31-12-2023
        
        Referência: 123 456 789
        Método de Pagamento: Débito Direto
        """
        
        result = self.parser.parse(text)
        
        self.assertEqual(result["provider"], "edp")
        self.assertEqual(result["invoice_number"], "FA202400123456")
        self.assertEqual(result["issue_date"], "15-01-2024")
        self.assertEqual(result["due_date"], "30-01-2024")
        self.assertEqual(result["consumption_period_start"], "01-12-2023")
        self.assertEqual(result["consumption_period_end"], "31-12-2023")
        self.assertAlmostEqual(result["consumption_kwh"], 350.50, places=2)
        self.assertAlmostEqual(result["power_contracted_kva"], 6.90, places=2)
        self.assertAlmostEqual(result["price_per_kwh"], 0.15, places=2)
        self.assertAlmostEqual(result["energy_cost"], 52.58, places=2)
        self.assertAlmostEqual(result["network_cost"], 12.34, places=2)
        self.assertAlmostEqual(result["iva_rate"], 23.0, places=2)
        self.assertAlmostEqual(result["iva_value"], 14.68, places=2)
        self.assertAlmostEqual(result["total_amount"], 79.60, places=2)
        self.assertEqual(result["client_name"], "João Silva")
        self.assertEqual(result["nif"], "123456789")
        self.assertEqual(result["address"], "Rua da Liberdade, 123")
        self.assertEqual(result["postal_code"], "1234-567")
        self.assertEqual(result["city"], "Lisboa")
        self.assertEqual(result["meter_number"], "ED12345678")
        self.assertEqual(result["current_reading"], 12345)
        self.assertEqual(result["previous_reading"], 12000)
        self.assertEqual(result["reading_date"], "31-12-2023")
        self.assertEqual(result["payment_reference"], "123 456 789")
        self.assertEqual(result["payment_method"], "Débito Direto")


class TestGalpParser(unittest.TestCase):
    """Testes para o parser Galp."""
    
    def setUp(self):
        """Configurar testes."""
        self.parser = GalpParser()
    
    def test_detect_galp(self):
        """Testar deteção de fatura Galp."""
        text = "Galp Energia"
        self.assertTrue(self.parser.detect(text))
        
        text = "Fatura Galp"
        self.assertTrue(self.parser.detect(text))
        
        text = "EDP"
        self.assertFalse(self.parser.detect(text))


class TestIbersolParser(unittest.TestCase):
    """Testes para o parser Ibersol."""
    
    def setUp(self):
        """Configurar testes."""
        self.parser = IbersolParser()
    
    def test_detect_ibersol(self):
        """Testar deteção de fatura Ibersol."""
        text = "Ibersol"
        self.assertTrue(self.parser.detect(text))
        
        text = "Ibersol Energia"
        self.assertTrue(self.parser.detect(text))
        
        text = "Galp"
        self.assertFalse(self.parser.detect(text))


if __name__ == '__main__':
    unittest.main()
