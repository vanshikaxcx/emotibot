"""
Utility functions for EmotiBot
"""
import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
import re
import unicodedata

def setup_logging(log_level: str = "INFO", log_file: str = None) -> logging.Logger:
    """
    Set up logging configuration
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_file: Optional log file path
        
    Returns:
        Configured logger
    """
    # Configure logging format
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Set up handlers
    handlers = [logging.StreamHandler()]
    
    if log_file:
        handlers.append(logging.FileHandler(log_file))
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format=log_format,
        handlers=handlers
    )
    
    return logging.getLogger(__name__)

def clean_text(text: str) -> str:
    """
    Clean and normalize text
    
    Args:
        text: Input text
        
    Returns:
        Cleaned text
    """
    if not text:
        return ""
    
    # Normalize unicode characters
    text = unicodedata.normalize('NFKD', text)
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Strip leading/trailing whitespace
    text = text.strip()
    
    return text

def truncate_text(text: str, max_length: int, add_ellipsis: bool = True) -> str:
    """
    Truncate text to maximum length
    
    Args:
        text: Input text
        max_length: Maximum length
        add_ellipsis: Whether to add ellipsis
        
    Returns:
        Truncated text
    """
    if not text or len(text) <= max_length:
        return text
    
    if add_ellipsis and max_length > 3:
        return text[:max_length-3] + "..."
    else:
        return text[:max_length]

def format_timestamp(timestamp: datetime = None) -> str:
    """
    Format timestamp for display
    
    Args:
        timestamp: Datetime object (default: now)
        
    Returns:
        Formatted timestamp string
    """
    if timestamp is None:
        timestamp = datetime.now()
    
    return timestamp.strftime("%Y-%m-%d %H:%M:%S")

def save_json(data: Any, file_path: str) -> bool:
    """
    Save data to JSON file
    
    Args:
        data: Data to save
        file_path: Output file path
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        return True
        
    except Exception as e:
        logging.error(f"Error saving JSON to {file_path}: {e}")
        return False

def load_json(file_path: str) -> Optional[Any]:
    """
    Load data from JSON file
    
    Args:
        file_path: Input file path
        
    Returns:
        Loaded data or None if failed
    """
    try:
        if not os.path.exists(file_path):
            return None
        
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
        
    except Exception as e:
        logging.error(f"Error loading JSON from {file_path}: {e}")
        return None

def ensure_directory(directory_path: str) -> bool:
    """
    Ensure directory exists, create if necessary
    
    Args:
        directory_path: Directory path
        
    Returns:
        True if directory exists or was created, False otherwise
    """
    try:
        os.makedirs(directory_path, exist_ok=True)
        return True
    except Exception as e:
        logging.error(f"Error creating directory {directory_path}: {e}")
        return False

def get_file_size(file_path: str) -> int:
    """
    Get file size in bytes
    
    Args:
        file_path: Path to file
        
    Returns:
        File size in bytes, -1 if error
    """
    try:
        return os.path.getsize(file_path)
    except Exception:
        return -1

def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human readable format
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Formatted size string
    """
    if size_bytes < 0:
        return "Unknown"
    
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    
    return f"{size_bytes:.1f} TB"

def extract_keywords(text: str, max_keywords: int = 10) -> List[str]:
    """
    Extract keywords from text
    
    Args:
        text: Input text
        max_keywords: Maximum number of keywords
        
    Returns:
        List of keywords
    """
    if not text:
        return []
    
    # Simple keyword extraction - remove common words and extract meaningful terms
    stop_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with',
        'by', 'from', 'up', 'about', 'into', 'through', 'during', 'before', 'after',
        'above', 'below', 'between', 'among', 'is', 'are', 'was', 'were', 'be', 'been',
        'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
        'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those'
    }
    
    # Extract words
    words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
    
    # Filter out stop words and get unique words
    keywords = []
    seen = set()
    
    for word in words:
        if word not in stop_words and word not in seen:
            keywords.append(word)
            seen.add(word)
            
            if len(keywords) >= max_keywords:
                break
    
    return keywords

def validate_email(email: str) -> bool:
    """
    Validate email address format
    
    Args:
        email: Email address
        
    Returns:
        True if valid, False otherwise
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename for safe file system usage
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    # Remove or replace invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Remove leading/trailing spaces and dots
    filename = filename.strip(' .')
    
    # Limit length
    if len(filename) > 255:
        name, ext = os.path.splitext(filename)
        filename = name[:255-len(ext)] + ext
    
    return filename

def chunk_list(lst: List[Any], chunk_size: int) -> List[List[Any]]:
    """
    Split list into chunks
    
    Args:
        lst: Input list
        chunk_size: Size of each chunk
        
    Returns:
        List of chunks
    """
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]

def merge_dicts(dict1: Dict, dict2: Dict) -> Dict:
    """
    Merge two dictionaries
    
    Args:
        dict1: First dictionary
        dict2: Second dictionary
        
    Returns:
        Merged dictionary
    """
    result = dict1.copy()
    result.update(dict2)
    return result

def get_user_input(prompt: str, valid_options: List[str] = None) -> str:
    """
    Get user input with validation
    
    Args:
        prompt: Input prompt
        valid_options: List of valid options (optional)
        
    Returns:
        User input
    """
    while True:
        user_input = input(prompt).strip()
        
        if not valid_options:
            return user_input
        
        if user_input.lower() in [opt.lower() for opt in valid_options]:
            return user_input
        
        print(f"Invalid option. Please choose from: {', '.join(valid_options)}")

def calculate_similarity(text1: str, text2: str) -> float:
    """
    Calculate simple similarity between two texts
    
    Args:
        text1: First text
        text2: Second text
        
    Returns:
        Similarity score (0-1)
    """
    if not text1 or not text2:
        return 0.0
    
    # Simple word-based similarity
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())
    
    intersection = words1.intersection(words2)
    union = words1.union(words2)
    
    if not union:
        return 0.0
    
    return len(intersection) / len(union)

class Timer:
    """Simple timer context manager"""
    
    def __init__(self, description: str = "Operation"):
        self.description = description
        self.start_time = None
    
    def __enter__(self):
        self.start_time = datetime.now()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time:
            duration = datetime.now() - self.start_time
            print(f"{self.description} took {duration.total_seconds():.2f} seconds")

def safe_divide(a: float, b: float, default: float = 0.0) -> float:
    """
    Safe division with default value for division by zero
    
    Args:
        a: Numerator
        b: Denominator
        default: Default value if division by zero
        
    Returns:
        Result of division or default value
    """
    try:
        return a / b if b != 0 else default
    except:
        return default
