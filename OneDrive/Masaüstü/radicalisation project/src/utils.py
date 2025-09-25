"""
Utility functions for the Digital Radicalization Research Project
"""

import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

def setup_logging(log_level: str = "INFO", log_file: str = None) -> logging.Logger:
    """Setup logging configuration"""
    
    # Create logs directory
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    # Default log file with timestamp
    if not log_file:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = logs_dir / f"radicalization_research_{timestamp}.log"
    
    # Configure logging
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format=log_format,
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    logger = logging.getLogger(__name__)
    logger.info(f"Logging initialized. Log file: {log_file}")
    
    return logger

def validate_date_range(start_date: datetime, end_date: datetime) -> bool:
    """Validate date range parameters"""
    if start_date >= end_date:
        return False
    
    # Check if date range is reasonable (not too far in the past or future)
    now = datetime.now()
    if end_date > now:
        return False
    
    # Maximum range of 1 year
    if (end_date - start_date).days > 365:
        return False
    
    return True

def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe file system usage"""
    # Remove or replace unsafe characters
    unsafe_chars = '<>:"/\\|?*'
    for char in unsafe_chars:
        filename = filename.replace(char, '_')
    
    # Limit length
    if len(filename) > 200:
        filename = filename[:200]
    
    return filename

def ensure_directory(path: str) -> Path:
    """Ensure directory exists, create if it doesn't"""
    path_obj = Path(path)
    path_obj.mkdir(parents=True, exist_ok=True)
    return path_obj

def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"

def get_platform_icon(platform: str) -> str:
    """Get emoji icon for platform"""
    icons = {
        'twitter': '🐦',
        'reddit': '🤖',
        'forum': '💬',
        'news': '📰',
        'facebook': '📘',
        'instagram': '📷',
        'telegram': '✈️',
        'youtube': '📹'
    }
    return icons.get(platform.lower(), '🌐')

def get_category_color(category: str) -> str:
    """Get color code for category visualization"""
    colors = {
        'Violence_CallToAction': '#FF4444',      # Red
        'Group_Identity': '#FF8800',              # Orange  
        'Delegitimisation_Dehumanisation': '#CC0000',  # Dark Red
        'Conspiracy_Polarising': '#FFAA00',      # Yellow-Orange
        'Propaganda_Recruitment': '#FF6600',     # Red-Orange
        'Religious_Radical': '#8800FF',          # Purple
        'PKK_Related': '#0088FF',                # Blue
        'Conversion_Identity': '#00AA88'         # Teal
    }
    return colors.get(category, '#808080')  # Default gray

def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate text with ellipsis if too long"""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."

def calculate_percentage(part: int, total: int) -> float:
    """Calculate percentage safely"""
    if total == 0:
        return 0.0
    return round((part / total) * 100, 2)

def normalize_text(text: str) -> str:
    """Normalize text for processing"""
    if not text:
        return ""
    
    # Basic normalization
    text = text.strip()
    text = ' '.join(text.split())  # Remove extra whitespace
    
    return text

def extract_hashtags(text: str) -> List[str]:
    """Extract hashtags from text"""
    import re
    hashtag_pattern = r'#\w+'
    hashtags = re.findall(hashtag_pattern, text.lower())
    return [tag[1:] for tag in hashtags]  # Remove # symbol

def extract_mentions(text: str) -> List[str]:
    """Extract mentions (@username) from text"""
    import re
    mention_pattern = r'@\w+'
    mentions = re.findall(mention_pattern, text.lower())
    return [mention[1:] for mention in mentions]  # Remove @ symbol

def detect_urls(text: str) -> List[str]:
    """Detect URLs in text"""
    import re
    url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    urls = re.findall(url_pattern, text)
    return urls

def create_summary_report(data: Dict[str, Any]) -> str:
    """Create a formatted summary report"""
    report_lines = []
    report_lines.append("=" * 50)
    report_lines.append("DIGITAL RADICALIZATION RESEARCH SUMMARY")
    report_lines.append("=" * 50)
    report_lines.append("")
    
    if 'metadata' in data:
        metadata = data['metadata']
        report_lines.append(f"Generated: {metadata.get('generated_at', 'Unknown')}")
        report_lines.append(f"Total Records: {metadata.get('total_records', 0)}")
        report_lines.append("")
    
    if 'summary' in data:
        summary = data['summary']
        report_lines.append("OVERVIEW:")
        report_lines.append(f"  Total Count: {summary.get('total_count', 0)}")
        report_lines.append(f"  Platforms: {len(summary.get('platforms', []))}")
        report_lines.append(f"  Regions: {len(summary.get('regions', []))}")
        report_lines.append(f"  Categories: {len(summary.get('categories', []))}")
        report_lines.append("")
        
        # Top categories
        if 'top_categories' in summary:
            report_lines.append("TOP CATEGORIES:")
            for category, count in summary['top_categories'].items():
                report_lines.append(f"  {category}: {count}")
            report_lines.append("")
        
        # Platform distribution
        if 'platform_distribution' in summary:
            report_lines.append("PLATFORM DISTRIBUTION:")
            for platform, count in summary['platform_distribution'].items():
                icon = get_platform_icon(platform)
                report_lines.append(f"  {icon} {platform}: {count}")
            report_lines.append("")
    
    report_lines.append("=" * 50)
    
    return "\n".join(report_lines)

def progress_bar(current: int, total: int, width: int = 50) -> str:
    """Create a simple progress bar"""
    if total == 0:
        return "[" + " " * width + "] 0%"
    
    progress = current / total
    filled = int(width * progress)
    bar = "█" * filled + "░" * (width - filled)
    percentage = int(progress * 100)
    
    return f"[{bar}] {percentage}%"

class Timer:
    """Simple timer context manager"""
    
    def __init__(self, name: str = "Operation"):
        self.name = name
        self.start_time = None
    
    def __enter__(self):
        self.start_time = datetime.now()
        print(f"Starting {self.name}...")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        end_time = datetime.now()
        duration = end_time - self.start_time
        print(f"{self.name} completed in {duration.total_seconds():.2f} seconds")

def format_duration(seconds: float) -> str:
    """Format duration in human readable format"""
    if seconds < 60:
        return f"{seconds:.1f} seconds"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f} minutes"
    else:
        hours = seconds / 3600
        return f"{hours:.1f} hours"