#!/usr/bin/env python3
"""
Turkey Digital Radicalization Detection - Trial Version
Usage: python main.py
"""

import json
from scrapers.turkey_scraper import TurkeyScraper
from classifier import KeywordClassifier  
from aggregator import WeeklyAggregator

def main():
    print("🇹🇷 Turkey Digital Radicalization Detection - Starting Trial Run")
    print("=" * 60)
    
    # Step 1: Web Scraping
    scraper = TurkeyScraper()
    posts = scraper.scrape_sample_forum()
    
    # Step 2: Keyword Classification
    classifier = KeywordClassifier()
    matches = classifier.classify_posts(posts)
    
    # Step 3: Weekly Aggregation
    aggregator = WeeklyAggregator()
    results = aggregator.aggregate(matches)
    
    # Step 4: Output Results
    print("\n📋 FINAL RESULTS")
    print("=" * 60)
    
    if results:
        print(json.dumps(results, indent=2, ensure_ascii=False))
        
        # Save to file
        with open('turkey_results.json', 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print("\n💾 Results saved to 'turkey_results.json'")
    else:
        print("❌ No results found")

if __name__ == "__main__":
    main()