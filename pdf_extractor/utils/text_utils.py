"""
Text processing utilities
"""

import re
from typing import List, Dict, Optional


def clean_text(text: str) -> str:
    """
    Clean extracted text by removing extra whitespace and special characters.
    
    Args:
        text: Raw extracted text
        
    Returns:
        Cleaned text
    """
    if not text:
        return ""
    
    # Remove multiple spaces and newlines
    text = re.sub(r'\s+', ' ', text)
    
    # Remove non-printable characters
    text = re.sub(r'[^\x20-\x7E\n\r\t]', '', text)
    
    return text.strip()


def normalize_text(text: str) -> str:
    """
    Normalize text for pattern matching.
    
    Args:
        text: Text to normalize
        
    Returns:
        Normalized text (lowercase, no extra spaces)
    """
    if not text:
        return ""
    
    text = text.lower()
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def extract_numbers(text: str) -> List[str]:
    """
    Extract all numbers from text.
    
    Args:
        text: Text to search
        
    Returns:
        List of found numbers as strings
    """
    return re.findall(r'\d+[.,]?\d*', text)


def extract_dates(text: str) -> List[str]:
    """
    Extract date patterns from text.
    
    Args:
        text: Text to search
        
    Returns:
        List of found date strings
    """
    # Common date patterns: DD/MM/YYYY, MM/DD/YYYY, YYYY-MM-DD
    date_patterns = [
        r'\d{2}/\d{2}/\d{4}',
        r'\d{4}-\d{2}-\d{2}',
        r'\d{2}-\d{2}-\d{4}',
        r'\d{1,2}\s+[A-Za-z]{3}\s+\d{4}',
    ]
    
    dates = []
    for pattern in date_patterns:
        dates.extend(re.findall(pattern, text))
    
    return dates
