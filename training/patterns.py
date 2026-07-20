"""
Pattern management for invoice field extraction
"""

import json
import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict


@dataclass
class Pattern:
    """A single extraction pattern"""
    pattern: str
    type: str = "regex"  # or "contains"
    field: str = ""
    description: str = ""
    group: int = 1  # Default group to capture
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class PatternManager:
    """
    Manage extraction patterns for invoice fields.
    
    Patterns are stored in JSON format and can be:
    - Regex patterns: for precise matching
    - Contains patterns: for simple text matching
    """
    
    DEFAULT_PATTERNS = {
        "invoice_number": [
            {"pattern": r"invoice[\s:]*([a-z0-9\-\s]+)", "type": "regex"},
            {"pattern": r"inv[\s:]*([a-z0-9\-\s]+)", "type": "regex"},
            {"pattern": "invoice no", "type": "contains"},
        ],
        "date": [
            {"pattern": r"date[\s:]*(\d{2}/\d{2}/\d{4})", "type": "regex"},
            {"pattern": r"date[\s:]*(\d{4}-\d{2}-\d{2})", "type": "regex"},
            {"pattern": "date", "type": "contains"},
        ],
        "total": [
            {"pattern": r"total[\s:]*([\d,]+\.?\d*)", "type": "regex"},
            {"pattern": r"amount[\s:]*([\d,]+\.?\d*)", "type": "regex"},
            {"pattern": "total", "type": "contains"},
        ],
        "customer": [
            {"pattern": r"customer[\s:]*([a-z0-9\s]+)", "type": "regex"},
            {"pattern": r"client[\s:]*([a-z0-9\s]+)", "type": "regex"},
            {"pattern": "customer", "type": "contains"},
        ],
        "supplier": [
            {"pattern": r"supplier[\s:]*([a-z0-9\s]+)", "type": "regex"},
            {"pattern": r"vendor[\s:]*([a-z0-9\s]+)", "type": "regex"},
            {"pattern": "supplier", "type": "contains"},
        ],
        "data_inicio": [
            {"pattern": r"Período de faturação: (\d{2}/\d{2}/\d{4}) a (\d{2}/\d{2}/\d{4})", "type": "regex", "group": 1},
            {"pattern": r"Período: (\d{2}/\d{2}/\d{4}) a (\d{2}/\d{2}/\d{4})", "type": "regex", "group": 1},
        ],
        "data_fim": [
            {"pattern": r"Período de faturação: (\d{2}/\d{2}/\d{4}) a (\d{2}/\d{2}/\d{4})", "type": "regex", "group": 2},
            {"pattern": r"Período: (\d{2}/\d{2}/\d{4}) a (\d{2}/\d{2}/\d{4})", "type": "regex", "group": 2},
        ],
    }
    
    def __init__(self, pattern_file: str = "training/patterns.json"):
        """
        Initialize pattern manager.
        
        Args:
            pattern_file: Path to JSON pattern file
        """
        self.pattern_file = pattern_file
        self.patterns = self._load_patterns()
    
    def _load_patterns(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load patterns from file or use defaults"""
        if os.path.exists(self.pattern_file):
            try:
                with open(self.pattern_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading patterns: {e}")
        return self.DEFAULT_PATTERNS.copy()
    
    def save_patterns(self) -> bool:
        """Save current patterns to file"""
        try:
            os.makedirs(os.path.dirname(self.pattern_file), exist_ok=True)
            with open(self.pattern_file, 'w', encoding='utf-8') as f:
                json.dump(self.patterns, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving patterns: {e}")
            return False
    
    def add_pattern(self, field: str, pattern: str, pattern_type: str = "regex", description: str = "", group: int = 1) -> bool:
        """
        Add a new pattern for a field.
        
        Args:
            field: Field name (e.g., "invoice_number")
            pattern: The pattern string
            pattern_type: "regex" or "contains"
            description: Optional description
            group: Group to capture (for regex patterns)
            
        Returns:
            True if added successfully
        """
        if field not in self.patterns:
            self.patterns[field] = []
        
        new_pattern = {
            "pattern": pattern,
            "type": pattern_type,
            "description": description,
            "group": group
        }
        
        # Check if pattern already exists
        for existing in self.patterns[field]:
            if (existing.get("pattern") == pattern and 
                existing.get("type") == pattern_type and
                existing.get("group", 1) == group):
                return False  # Pattern already exists
        
        self.patterns[field].append(new_pattern)
        return True
    
    def remove_pattern(self, field: str, pattern: str, pattern_type: str = "regex", group: int = 1) -> bool:
        """
        Remove a pattern from a field.
        
        Args:
            field: Field name
            pattern: Pattern string to remove
            pattern_type: Pattern type
            group: Group to match
            
        Returns:
            True if removed successfully
        """
        if field not in self.patterns:
            return False
        
        for i, existing in enumerate(self.patterns[field]):
            if (existing.get("pattern") == pattern and 
                existing.get("type") == pattern_type and
                existing.get("group", 1) == group):
                self.patterns[field].pop(i)
                return True
        
        return False
    
    def get_patterns_for_field(self, field: str) -> List[Dict[str, Any]]:
        """Get all patterns for a specific field"""
        return self.patterns.get(field, [])
    
    def get_all_fields(self) -> List[str]:
        """Get list of all field names"""
        return list(self.patterns.keys())
    
    def test_pattern(self, field: str, pattern: str, text: str) -> Optional[str]:
        """
        Test a pattern against text.
        
        Args:
            field: Field name
            pattern: Pattern to test
            text: Text to test against
            
        Returns:
            Matched value or None
        """
        import re
        from pdf_extractor.utils import normalize_text
        
        normalized_text = normalize_text(text)
        
        if pattern.startswith("regex:"):
            pattern = pattern[6:]  # Remove "regex:" prefix
            match = re.search(pattern, normalized_text, re.IGNORECASE)
            if match:
                return match.group(1) if match.groups() else match.group(0)
        else:
            # Simple contains
            if pattern.lower() in normalized_text:
                start = normalized_text.find(pattern.lower())
                if start != -1:
                    remaining = normalized_text[start + len(pattern):]
                    lines = remaining.split('\n')
                    if lines:
                        return lines[0].strip()
        
        return None
