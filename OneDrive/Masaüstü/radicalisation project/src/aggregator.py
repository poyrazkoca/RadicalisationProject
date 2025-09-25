"""
Enhanced aggregation module with hierarchical fallback logic
Incorporates best practices from reference implementation
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from collections import defaultdict, Counter

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    pd = None

class EnhancedAggregator:
    """
    Enhanced aggregator with hierarchical fallback logic:
    1. Region (NUTS-2) - highest priority
    2. Country - medium priority  
    3. Language - fallback when location unavailable
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # NUTS-2 Region mapping (most granular)
        self.nuts2_regions = {
            # Turkey NUTS-2 regions
            'istanbul': 'TR10', 'ankara': 'TR51', 'izmir': 'TR31',
            'bursa': 'TR41', 'antalya': 'TR61', 'adana': 'TR62',
            'konya': 'TR52', 'gaziantep': 'TR63', 'şanlıurfa': 'TRC2',
            'kayseri': 'TR72', 'mersin': 'TR62', 'diyarbakır': 'TRC1',
            'hatay': 'TR63', 'manisa': 'TR33', 'van': 'TRC1',
            
            # Greece NUTS-2 regions
            'athens': 'EL30', 'thessaloniki': 'EL52', 'patras': 'EL65',
            'heraklion': 'EL43', 'larissa': 'EL61', 'volos': 'EL61',
            
            # Other regions
            'london': 'UKI', 'manchester': 'UKD', 'birmingham': 'UKG',
            'paris': 'FR10', 'marseille': 'FR82', 'lyon': 'FR71',
            'berlin': 'DE30', 'munich': 'DE21', 'hamburg': 'DE60',
            'new york': 'US-NY', 'california': 'US-CA', 'texas': 'US-TX'
        }
        
        # Country mapping (medium granularity)
        self.country_mapping = {
            'turkey': 'TR', 'greece': 'GR', 'cyprus': 'CY',
            'united states': 'US', 'usa': 'US', 'america': 'US',
            'united kingdom': 'GB', 'uk': 'GB', 'britain': 'GB',
            'germany': 'DE', 'france': 'FR', 'syria': 'SY', 'iraq': 'IQ'
        }
        
        # Language mapping (fallback)
        self.language_mapping = {
            'TR': 'Turkish', 'EN': 'English', 'GR': 'Greek',
            'DE': 'German', 'FR': 'French', 'AR': 'Arabic'
        }
    
    def aggregate_hierarchical(self, classified_data: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Aggregate data using hierarchical fallback logic:
        Region > Country > Language
        
        Returns:
            {
                'by_region': [...],    # Most granular (NUTS-2)
                'by_country': [...],   # Medium granularity  
                'by_language': [...]   # Fallback aggregation
            }
        """
        if not classified_data:
            self.logger.warning("No classified data to aggregate")
            return {'by_region': [], 'by_country': [], 'by_language': []}
        
        self.logger.info(f"Aggregating {len(classified_data)} classified items using hierarchical approach")
        
        # Use pandas if available for better performance
        if PANDAS_AVAILABLE:
            return self._aggregate_with_pandas(classified_data)
        else:
            return self._aggregate_manual(classified_data)
    
    def _aggregate_with_pandas(self, classified_data: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Aggregate using pandas for better performance"""
        df = pd.DataFrame(classified_data)
        
        # Ensure timestamp is datetime and add ISO week
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['week'] = df['timestamp'].dt.isocalendar().week
        df['year'] = df['timestamp'].dt.year
        df['week_iso'] = df['year'].astype(str) + '-W' + df['week'].astype(str).str.zfill(2)
        
        # Extract region, country, and ensure language is available
        df['region'] = df['location'].apply(self._extract_nuts2_region)
        df['country'] = df['location'].apply(self._extract_country)
        df['language'] = df['language'].fillna('UNKNOWN')
        
        results = {}
        
        # 1. Aggregate by Region (highest priority - most granular)
        df_region = df.dropna(subset=['region'])  # Only use rows with region data
        if not df_region.empty:
            agg_region = df_region.groupby(['region', 'week_iso', 'platform', 'category']).size().reset_index(name='count')
            results['by_region'] = agg_region.to_dict('records')
            self.logger.info(f"Region aggregation: {len(results['by_region'])} records")
        else:
            results['by_region'] = []
            self.logger.warning("No region data available for aggregation")
        
        # 2. Aggregate by Country (medium priority)
        df_country = df.dropna(subset=['country'])
        if not df_country.empty:
            agg_country = df_country.groupby(['country', 'week_iso', 'platform', 'category']).size().reset_index(name='count')
            results['by_country'] = agg_country.to_dict('records')
            self.logger.info(f"Country aggregation: {len(results['by_country'])} records")
        else:
            results['by_country'] = []
            self.logger.warning("No country data available for aggregation")
        
        # 3. Aggregate by Language (fallback - always available)
        agg_language = df.groupby(['language', 'week_iso', 'platform', 'category']).size().reset_index(name='count')
        results['by_language'] = agg_language.to_dict('records')
        self.logger.info(f"Language aggregation: {len(results['by_language'])} records (primary feasible method)")
        
        return results
    
    def _aggregate_manual(self, classified_data: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Manual aggregation when pandas is not available"""
        
        # Initialize counters for each aggregation level
        region_counter = Counter()
        country_counter = Counter()
        language_counter = Counter()
        
        for item in classified_data:
            # Extract week in ISO format
            timestamp = item.get('timestamp')
            if isinstance(timestamp, str):
                timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            elif not isinstance(timestamp, datetime):
                timestamp = datetime.now()
            
            year, week, _ = timestamp.isocalendar()
            week_iso = f"{year}-W{week:02d}"
            
            platform = item.get('platform', 'unknown')
            category = item.get('category', 'unknown')
            location = item.get('location', '')
            language = item.get('language', 'UNKNOWN')
            
            # Extract geographic information
            region = self._extract_nuts2_region(location)
            country = self._extract_country(location)
            
            # Count for each aggregation level
            if region:
                region_key = (region, week_iso, platform, category)
                region_counter[region_key] += 1
            
            if country:
                country_key = (country, week_iso, platform, category)
                country_counter[country_key] += 1
            
            # Language is always available (fallback)
            language_key = (language, week_iso, platform, category)
            language_counter[language_key] += 1
        
        # Convert counters to result format
        results = {
            'by_region': [
                {'region': key[0], 'week': key[1], 'platform': key[2], 'category': key[3], 'count': count}
                for key, count in region_counter.items()
            ],
            'by_country': [
                {'country': key[0], 'week': key[1], 'platform': key[2], 'category': key[3], 'count': count}
                for key, count in country_counter.items()
            ],
            'by_language': [
                {'language': key[0], 'week': key[1], 'platform': key[2], 'category': key[3], 'count': count}
                for key, count in language_counter.items()
            ]
        }
        
        self.logger.info(f"Manual aggregation completed: Region={len(results['by_region'])}, Country={len(results['by_country'])}, Language={len(results['by_language'])}")
        return results
    
    def _extract_nuts2_region(self, location: str) -> Optional[str]:
        """Extract NUTS-2 region code from location string"""
        if not location:
            return None
        
        location_lower = location.lower().strip()
        
        # Direct mapping lookup
        for city, nuts2_code in self.nuts2_regions.items():
            if city in location_lower:
                return nuts2_code
        
        # Fuzzy matching for common variations
        if 'istanbul' in location_lower or 'constantinople' in location_lower:
            return 'TR10'
        elif 'ankara' in location_lower or 'angora' in location_lower:
            return 'TR51'
        elif 'izmir' in location_lower or 'smyrna' in location_lower:
            return 'TR31'
        
        return None
    
    def _extract_country(self, location: str) -> Optional[str]:
        """Extract country code from location string"""
        if not location:
            return None
        
        location_lower = location.lower().strip()
        
        # Direct mapping lookup
        for country_name, country_code in self.country_mapping.items():
            if country_name in location_lower:
                return country_code
        
        # Check if it contains common country indicators
        if any(indicator in location_lower for indicator in ['turkey', 'türkiye', 'tr']):
            return 'TR'
        elif any(indicator in location_lower for indicator in ['greece', 'hellas', 'gr']):
            return 'GR'
        elif any(indicator in location_lower for indicator in ['usa', 'america', 'united states']):
            return 'US'
        
        return None
    
    def get_preferred_aggregation(self, aggregated_results: Dict[str, List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """Get the most granular aggregation available with data"""
        # Priority: Region > Country > Language
        if aggregated_results.get('by_region'):
            self.logger.info("Using region-based aggregation (most granular)")
            return aggregated_results['by_region']
        elif aggregated_results.get('by_country'):
            self.logger.info("Using country-based aggregation (medium granularity)")
            return aggregated_results['by_country']
        else:
            self.logger.info("Using language-based aggregation (fallback method)")
            return aggregated_results.get('by_language', [])
    
    def export_results(self, aggregated_results: Dict[str, List[Dict[str, Any]]], output_path: str = None) -> str:
        """Export aggregated results to JSON file"""
        if not output_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"output/aggregated_results_{timestamp}.json"
        
        # Create output directory if it doesn't exist
        from pathlib import Path
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Add metadata
        export_data = {
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'aggregation_levels': ['region', 'country', 'language'],
                'total_records': {
                    'by_region': len(aggregated_results.get('by_region', [])),
                    'by_country': len(aggregated_results.get('by_country', [])),
                    'by_language': len(aggregated_results.get('by_language', []))
                }
            },
            'results': aggregated_results
        }
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False, default=str)
            
            self.logger.info(f"Results exported to {output_path}")
            return output_path
        except Exception as e:
            self.logger.error(f"Failed to export results: {e}")
            return ""