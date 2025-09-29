import pandas as pd
from collections import defaultdict

class WeeklyAggregator:
    def aggregate(self, matches):
        """Aggregate matches by week and location"""
        print("📊 Starting weekly aggregation...")
        
        if not matches:
            return []
        
        df = pd.DataFrame(matches)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Create week format: YYYY-W##
        df['week'] = df['timestamp'].dt.isocalendar().year.astype(str) + '-W' + \
                     df['timestamp'].dt.isocalendar().week.astype(str).str.zfill(2)
        
        # Aggregate by region first (preferred)
        results = []
        
        # 1. By Region (where available)
        region_data = df.dropna(subset=['region'])
        if not region_data.empty:
            region_agg = region_data.groupby(['region', 'week', 'platform', 'category']).size().reset_index(name='count')
            for _, row in region_agg.iterrows():
                results.append({
                    'location': row['region'],
                    'location_type': 'region',
                    'week': row['week'],
                    'platform': row['platform'],
                    'category': row['category'],
                    'count': row['count']
                })
        
        # 2. By Language (fallback)
        lang_agg = df.groupby(['language', 'week', 'platform', 'category']).size().reset_index(name='count')
        for _, row in lang_agg.iterrows():
            results.append({
                'location': row['language'],
                'location_type': 'language', 
                'week': row['week'],
                'platform': row['platform'],
                'category': row['category'],
                'count': row['count']
            })
        
        print(f"✅ Generated {len(results)} aggregated records")
        return results