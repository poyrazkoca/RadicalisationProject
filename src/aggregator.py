from collections import Counter, defaultdict
from datetime import datetime

class EnhancedAggregator:
    def aggregate_hierarchical(self, classified_data):
        results = []
        counter = Counter()
        for item in classified_data:
            week = datetime.fromisoformat(item["timestamp"]).isocalendar()[1]
            key = (item["location"], f"{datetime.now().year}-W{week:02d}", item["platform"], item["category"])
            counter[key] += 1
        for (region, week, platform, category), count in counter.items():
            results.append({
                "region": region,
                "week": week,
                "platform": platform,
                "category": category,
                "count": count
            })
        return results