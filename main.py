import json
from src.scraper import WebScraper
from src.classifier import KeywordClassifier
from src.aggregator import EnhancedAggregator

def main():
    classifier = KeywordClassifier("keywords.json")
    aggregator = EnhancedAggregator()
    scraper = WebScraper()
    demo_data = scraper.collect_data(region="Turkey")

    classified = []
    for item in demo_data:
        matches = classifier.classify_text(item["text"], target_language=item.get("language", "TR"))
        for category, keywords in matches.items():
            classified.append({
                "text": item["text"],
                "platform": item["platform"],
                "timestamp": item["timestamp"],
                "location": item["location"],
                "category": category,
                "matched_keywords": keywords,
                "language": item.get("language", "TR")
            })

    aggregated = aggregator.aggregate_hierarchical(classified)

    with open("output/aggregated_results.json", "w", encoding="utf-8") as f:
        json.dump(aggregated, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()