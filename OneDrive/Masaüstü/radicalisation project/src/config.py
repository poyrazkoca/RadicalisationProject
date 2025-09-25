"""
Configuration management for the Digital Radicalization Research Project
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False
    yaml = None

class Config:
    """Configuration manager for the scraping and analysis pipeline"""
    
    def __init__(self, config_path: str = None):
        self.base_path = Path(__file__).parent.parent
        self.config_path = config_path or self.base_path / "config" / "config.yaml"
        self.keywords_path = self.base_path / "keywords.json"
        self.api_keys_path = self.base_path / "config" / "api_keys.env"
        
        # Default configuration
        self.default_config = {
            "scraping": {
                "delay_between_requests": 2,
                "max_retries": 3,
                "timeout": 30,
                "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            },
            "classification": {
                "min_keyword_length": 3,
                "case_sensitive": False,
                "language_detection_threshold": 0.8
            },
            "aggregation": {
                "default_region_priority": ["province", "language", "country"],
                "week_start_day": "monday",
                "time_zone": "UTC"
            },
            "output": {
                "format": "json",
                "include_raw_text": False,
                "max_text_length": 500
            },
            "platforms": {
                "twitter": {
                    "enabled": True,
                    "rate_limit": 100,
                    "search_operators": ["lang:tr", "lang:en"]
                },
                "reddit": {
                    "enabled": True,
                    "subreddits": ["worldnews", "turkey", "europe"],
                    "sort_by": "new"
                },
                "forum": {
                    "enabled": True,
                    "sites": ["example-forum.com"]
                },
                "news": {
                    "enabled": True,
                    "sites": ["bbc.com", "cnn.com", "hurriyet.com.tr"]
                }
            }
        }
        
        self.config = self.load_config()
        self.keywords = self.load_keywords()
        self.api_keys = self.load_api_keys()
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file or return defaults"""
        try:
            if self.config_path.exists() and YAML_AVAILABLE:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    loaded_config = yaml.safe_load(f)
                    # Merge with defaults
                    return self._merge_configs(self.default_config, loaded_config)
            else:
                # Create default config file or use defaults if YAML not available
                if YAML_AVAILABLE:
                    self.save_default_config()
                return self.default_config
        except Exception as e:
            print(f"Error loading config: {e}. Using defaults.")
            return self.default_config
    
    def load_keywords(self) -> Dict[str, Any]:
        """Load keywords from JSON file"""
        try:
            with open(self.keywords_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading keywords: {e}")
            return {}
    
    def save_default_config(self):
        """Save default configuration to file"""
        if not YAML_AVAILABLE:
            return
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, 'w', encoding='utf-8') as f:
            yaml.dump(self.default_config, f, default_flow_style=False, allow_unicode=True)
    
    def _merge_configs(self, default: Dict, override: Dict) -> Dict:
        """Recursively merge configuration dictionaries"""
        result = default.copy()
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value
        return result
    
    def get(self, key_path: str, default=None):
        """Get configuration value using dot notation (e.g., 'scraping.delay_between_requests')"""
        keys = key_path.split('.')
        value = self.config
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default
    
    def get_platform_config(self, platform: str) -> Dict[str, Any]:
        """Get configuration for specific platform"""
        return self.config.get("platforms", {}).get(platform, {})
    
    def is_platform_enabled(self, platform: str) -> bool:
        """Check if platform is enabled for scraping"""
        return self.get_platform_config(platform).get("enabled", False)
    
    def load_api_keys(self) -> Dict[str, str]:
        """Load API keys from environment file"""
        api_keys = {}
        try:
            if self.api_keys_path.exists():
                with open(self.api_keys_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            api_keys[key.strip()] = value.strip()
            
            # Also check environment variables (production deployment)
            import os
            for key in ['TWITTER_BEARER_TOKEN', 'TWITTER_API_KEY', 'TWITTER_API_SECRET', 
                       'REDDIT_CLIENT_ID', 'REDDIT_CLIENT_SECRET', 'YOUTUBE_API_KEY']:
                if key in os.environ:
                    api_keys[key] = os.environ[key]
                    
        except Exception as e:
            print(f"Warning: Could not load API keys: {e}")
        
        return api_keys
    
    def get_api_key(self, key: str) -> Optional[str]:
        """Get specific API key"""
        return self.api_keys.get(key)
    
    def has_api_keys_for_platform(self, platform: str) -> bool:
        """Check if required API keys are available for platform"""
        if platform == "twitter":
            return bool(self.get_api_key("TWITTER_BEARER_TOKEN"))
        elif platform == "reddit":
            return bool(self.get_api_key("REDDIT_CLIENT_ID") and 
                       self.get_api_key("REDDIT_CLIENT_SECRET"))
        elif platform == "youtube":
            return bool(self.get_api_key("YOUTUBE_API_KEY"))
        return False