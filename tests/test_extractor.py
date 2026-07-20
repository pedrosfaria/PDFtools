"""
Tests for PDF Extractor functionality
"""

import unittest
import os
import tempfile
from pdf_extractor.extractor import PDFExtractor
from pdf_extractor.utils import clean_text, normalize_text, extract_numbers, extract_dates


class TestTextUtils(unittest.TestCase):
    """Test text processing utilities"""
    
    def test_clean_text(self):
        """Test text cleaning"""
        dirty_text = "  Hello   World  \n\n  Test  "
        clean = clean_text(dirty_text)
        self.assertEqual(clean, "Hello World Test")
    
    def test_normalize_text(self):
        """Test text normalization"""
        text = "  Hello WORLD  "
        normalized = normalize_text(text)
        self.assertEqual(normalized, "hello world")
    
    def test_extract_numbers(self):
        """Test number extraction"""
        text = "Total: 100.50 EUR, Quantity: 5"
        numbers = extract_numbers(text)
        self.assertIn("100.50", numbers)
        self.assertIn("5", numbers)
    
    def test_extract_dates(self):
        """Test date extraction"""
        text = "Date: 2024-01-15, Due: 15/02/2024"
        dates = extract_dates(text)
        self.assertIn("2024-01-15", dates)
        self.assertIn("15/02/2024", dates)


class TestPDFExtractor(unittest.TestCase):
    """Test PDF extractor"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.extractor = PDFExtractor()
    
    def test_extractor_initialization(self):
        """Test extractor can be initialized"""
        self.assertIsNotNone(self.extractor)
        self.assertIsNotNone(self.extractor.config)
        self.assertIsNotNone(self.extractor.patterns)
    
    def test_extract_nonexistent_file(self):
        """Test extraction of non-existent file"""
        result = self.extractor.extract("nonexistent.pdf")
        self.assertTrue(len(result.errors) > 0)


class TestPatternManager(unittest.TestCase):
    """Test pattern manager"""
    
    def test_pattern_manager_initialization(self):
        """Test pattern manager can be initialized"""
        from training.patterns import PatternManager
        manager = PatternManager()
        self.assertIsNotNone(manager)
        self.assertIsNotNone(manager.patterns)
    
    def test_add_pattern(self):
        """Test adding a pattern"""
        from training.patterns import PatternManager
        manager = PatternManager()
        
        # Add a test pattern
        result = manager.add_pattern("test_field", r"test[\s]+(\w+)", "regex")
        self.assertTrue(result)
        
        # Check pattern was added
        patterns = manager.get_patterns_for_field("test_field")
        self.assertEqual(len(patterns), 1)
    
    def test_save_and_load_patterns(self):
        """Test saving and loading patterns"""
        from training.patterns import PatternManager
        import tempfile
        import os
        
        # Create a temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_file = f.name
        
        try:
            manager = PatternManager(temp_file)
            manager.add_pattern("test_field", r"test[\s]+(\w+)", "regex")
            
            # Save patterns
            result = manager.save_patterns()
            self.assertTrue(result)
            
            # Create new manager and load
            manager2 = PatternManager(temp_file)
            patterns = manager2.get_patterns_for_field("test_field")
            self.assertEqual(len(patterns), 1)
        finally:
            # Clean up
            if os.path.exists(temp_file):
                os.remove(temp_file)


if __name__ == "__main__":
    unittest.main()
