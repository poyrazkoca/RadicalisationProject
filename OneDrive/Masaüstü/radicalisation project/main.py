"""
Digital Radicalization Research Project
=====================================

A comprehensive web scraping and text analysis system for monitoring 
digital radicalization patterns across social media and web platforms.

Features:
- Multi-platform web scraping (Twitter, Reddit, news sites, forums)
- Keyword-based classification using predefined categories
- Geographic and temporal aggregation
- Multi-language support (Turkish, English, Greek)
- Weekly reporting and visualization

Structure:
- src/: Main source code modules
- data/: Raw and processed data storage
- config/: Configuration files and keywords
- output/: Generated reports and visualizations
- logs/: Application logs

Usage:
    python main.py --platform twitter --region TR --weeks 4
    python main.py --demo  # Run demo flow for feasibility testing
"""

import argparse
import logging
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add src directory to path
sys.path.append(str(Path(__file__).parent / "src"))

from src.scraper import WebScraper
from src.classifier import KeywordClassifier
from src.aggregator import EnhancedAggregator
from src.config import Config
from src.utils import setup_logging

def run_demo():
    """Run a demo flow for feasibility testing"""
    print("🚀 Starting Digital Radicalization Research Demo")
    print("=" * 50)
    
    # Initialize components
    config = Config()
    scraper = WebScraper(config)
    classifier = KeywordClassifier(config.keywords_path)
    aggregator = EnhancedAggregator()
    
    # Demo data collection
    print("📊 Demo: Collecting sample data...")
    demo_texts = [
        {"text": "This is a test about jihad and holy war", "platform": "twitter", "timestamp": datetime.now(), "location": "Turkey"},
        {"text": "Discussion about PKK and şehir savaşı", "platform": "forum", "timestamp": datetime.now(), "location": "Turkey"},
        {"text": "Religious content about takbir", "platform": "reddit", "timestamp": datetime.now(), "location": "USA"},
    ]
    
    # Classify texts
    print("🔍 Demo: Classifying texts with keywords...")
    classified_data = []
    for item in demo_texts:
        matches = classifier.classify_text(item["text"])
        if matches:
            for category, keywords in matches.items():
                classified_data.append({
                    "text": item["text"],
                    "platform": item["platform"],
                    "timestamp": item["timestamp"],
                    "location": item["location"],
                    "category": category,
                    "matched_keywords": keywords,
                    "language": classifier.detect_language(item["text"])
                })
    
    # Aggregate results using hierarchical approach
    print("📈 Demo: Aggregating results...")
    aggregated = aggregator.aggregate_hierarchical(classified_data)
    
    # Get preferred aggregation
    preferred_results = aggregator.get_preferred_aggregation(aggregated)
    
    # Display results
    print("\n📋 Demo Results:")
    print("-" * 30)
    for result in preferred_results:
        # Handle different aggregation types
        location_key = 'region' if 'region' in result else 'country' if 'country' in result else 'language'
        location_value = result.get(location_key, 'Unknown')
        
        print(f"{location_key.title()}: {location_value}")
        print(f"Week: {result['week']}")
        print(f"Platform: {result['platform']}")
        print(f"Category: {result['category']}")
        print(f"Count: {result['count']}")
        print("-" * 30)
    
    print("✅ Demo completed successfully!")
    return preferred_results

def main():
    parser = argparse.ArgumentParser(description="Digital Radicalization Research Tool")
    parser.add_argument("--platform", choices=["twitter", "reddit", "forum", "news"], 
                       help="Platform to scrape")
    parser.add_argument("--region", help="Region/country code (e.g., TR, US, GR)")
    parser.add_argument("--weeks", type=int, default=1, help="Number of weeks to analyze")
    parser.add_argument("--demo", action="store_true", help="Run demo mode")
    parser.add_argument("--config", default="config/config.yaml", help="Config file path")
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        if args.demo:
            return run_demo()
        
        # Initialize components
        config = Config(args.config)
        scraper = WebScraper(config)
        classifier = KeywordClassifier(config.keywords_path)
        aggregator = EnhancedAggregator()
        
        # Data collection
        logger.info(f"Starting data collection for {args.weeks} weeks")
        end_date = datetime.now()
        start_date = end_date - timedelta(weeks=args.weeks)
        
        raw_data = scraper.collect_data(
            platform=args.platform,
            region=args.region,
            start_date=start_date,
            end_date=end_date
        )
        
        # Classification
        logger.info("Classifying collected texts")
        classified_data = []
        for item in raw_data:
            matches = classifier.classify_text(item["text"])
            if matches:
                for category, keywords in matches.items():
                    classified_data.append({
                        **item,
                        "category": category,
                        "matched_keywords": keywords,
                        "language": classifier.detect_language(item["text"])
                    })
        
        # Aggregation using hierarchical approach
        logger.info("Aggregating results with hierarchical fallback")
        aggregated_results = aggregator.aggregate_hierarchical(classified_data)
        
        # Save results
        output_path = aggregator.export_results(aggregated_results)
        
        logger.info(f"Analysis completed. Results saved to {output_path}")
        return aggregated_results
        
    except Exception as e:
        logger.error(f"Error during execution: {str(e)}")
        raise

if __name__ == "__main__":
    main()