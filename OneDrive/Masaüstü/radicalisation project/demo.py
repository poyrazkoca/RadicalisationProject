"""
Enhanced demo script with realistic data simulation
Incorporates best practices from the reference implementation
"""

import sys
from pathlib import Path
import json
from datetime import datetime, timedelta
import argparse

# Add src directory to path
sys.path.append(str(Path(__file__).parent / "src"))

from src.classifier import KeywordClassifier
from src.aggregator import EnhancedAggregator
from src.config import Config
from src.utils import setup_logging

def get_realistic_demo_data():
    """
    Generate realistic demo data that acknowledges real-world challenges:
    - Most posts don't have reliable location data (region=None)  
    - Language detection is more reliable than location
    - Platform variety represents real usage patterns
    """
    demo_data = [
        # Turkish content with varied location reliability
        {
            'platform': 'Twitter',
            'timestamp': '2025-09-20T10:00:00Z',
            'language': 'TR',
            'location': 'Ankara, Turkey',  # Clear location
            'text': 'Bu kutsal savaşta yanımızda olan kardeşlerimizle zafer elde edeceğiz'
        },
        {
            'platform': 'ForumX', 
            'timestamp': '2025-09-21T15:30:00Z',
            'language': 'TR',
            'location': None,  # No location data (realistic)
            'text': 'PKK ile hendek savaşı devam ediyor, direniş hakkımız'
        },
        {
            'platform': 'Reddit',
            'timestamp': '2025-09-22T18:00:00Z',
            'language': 'TR',
            'location': 'Istanbul',  # Partial location
            'text': 'Hilafet kurulmalı, şeriat getirilmeli bu topraklara'
        },
        {
            'platform': 'Twitter',
            'timestamp': '2025-09-23T11:20:00Z', 
            'language': 'TR',
            'location': None,  # No location (common case)
            'text': 'Kafir ve hainler yakında cezasını bulacak, intikam alınacak'
        },
        
        # English content
        {
            'platform': 'Twitter',
            'timestamp': '2025-09-20T12:00:00Z',
            'language': 'EN',
            'location': 'London, UK',
            'text': 'The holy war is upon us, we must strike against the enemy'
        },
        {
            'platform': 'Reddit',
            'timestamp': '2025-09-21T18:00:00Z',
            'language': 'EN', 
            'location': None,  # No location data
            'text': 'They are talking about a great reset, new world order is coming'
        },
        {
            'platform': 'ForumX',
            'timestamp': '2025-09-22T21:00:00Z',
            'language': 'EN',
            'location': 'New York, USA',
            'text': 'We need to join the resistance against the globalist agenda'
        },
        {
            'platform': 'Twitter',
            'timestamp': '2025-09-24T14:00:00Z',
            'language': 'EN',
            'location': None,  # No location
            'text': 'A call for all brothers to embrace faith and join the struggle'
        }
    ]
    
    return demo_data

def run_enhanced_demo():
    """Run enhanced demo with realistic data and hierarchical aggregation"""
    print("🚀 Enhanced Digital Radicalization Research Demo")
    print("=" * 55)
    print("📋 Features:")
    print("   • Realistic data simulation (acknowledges location data scarcity)")
    print("   • Hierarchical aggregation: Region > Country > Language") 
    print("   • Word boundary keyword matching (prevents false positives)")
    print("   • Multiple aggregation outputs for different analysis needs")
    print()
    
    # Setup logging
    setup_logging()
    
    # Initialize components
    config = Config()
    classifier = KeywordClassifier(config.keywords_path)
    aggregator = EnhancedAggregator()
    
    # Load realistic demo data
    demo_data = get_realistic_demo_data()
    print(f"📊 Processing {len(demo_data)} realistic demo texts...")
    print()
    
    # Show data characteristics
    with_location = sum(1 for item in demo_data if item['location'])
    without_location = len(demo_data) - with_location
    print(f"📍 Location Data Availability (realistic scenario):")
    print(f"   • With location: {with_location} texts ({with_location/len(demo_data)*100:.1f}%)")
    print(f"   • Without location: {without_location} texts ({without_location/len(demo_data)*100:.1f}%)")
    print(f"   • This reflects real-world data scarcity challenges")
    print()
    
    # Classify texts
    print("🔍 Classifying texts with keyword matching...")
    classified_results = []
    
    for item in demo_data:
        # Use the correct classifier interface 
        classification = classifier.classify_text(
            text=item['text'],
            target_language=item['language']
        )
        
        # classification returns dict mapping categories to matched keywords
        if classification:
            for category, matched_keywords in classification.items():
                classified_results.append({
                    'platform': item['platform'],
                    'timestamp': item['timestamp'],
                    'language': item['language'],
                    'location': item['location'],
                    'category': category,
                    'matched_keywords': matched_keywords,
                    'text_preview': item['text'][:50] + '...' if len(item['text']) > 50 else item['text']
                })
    
    print(f"✅ Found {len(classified_results)} matches across {len(demo_data)} texts")
    print()
    
    # Show found matches
    print("📝 Classification Results:")
    for i, result in enumerate(classified_results, 1):
        location_str = result['location'] or 'No location data'
        print(f"   {i}. [{result['platform']}] {result['category']} - {location_str}")
        print(f"      Keywords: {', '.join(result['matched_keywords'])}")
        print(f"      Text: {result['text_preview']}")
        print()
    
    # Hierarchical aggregation
    print("📊 Performing Hierarchical Aggregation...")
    aggregated = aggregator.aggregate_hierarchical(classified_results)
    
    # Display results for each aggregation level
    print()
    print("=" * 55)
    print("📈 AGGREGATION RESULTS")
    print("=" * 55)
    
    # 1. Region-based aggregation (most granular)
    if aggregated['by_region']:
        print()
        print("🏛️ REGION-BASED AGGREGATION (Most Granular - NUTS-2)")
        print("-" * 50)
        for result in aggregated['by_region']:
            print(f"   Region: {result['region']}, Week: {result['week']}, Platform: {result['platform']}")
            print(f"   Category: {result['category']}, Count: {result['count']}")
            print()
    else:
        print()
        print("🏛️ REGION-BASED AGGREGATION: No region data available")
        print("   (This is realistic - most social media posts lack precise location data)")
    
    # 2. Country-based aggregation (medium granularity)  
    if aggregated['by_country']:
        print()
        print("🌍 COUNTRY-BASED AGGREGATION (Medium Granularity)")
        print("-" * 50)
        for result in aggregated['by_country']:
            print(f"   Country: {result['country']}, Week: {result['week']}, Platform: {result['platform']}")
            print(f"   Category: {result['category']}, Count: {result['count']}")
            print()
    else:
        print()
        print("🌍 COUNTRY-BASED AGGREGATION: Limited country data available")
    
    # 3. Language-based aggregation (fallback - always available)
    print()
    print("🗣️ LANGUAGE-BASED AGGREGATION (Primary Feasible Method)")
    print("-" * 50)
    for result in aggregated['by_language']:
        print(f"   Language: {result['language']}, Week: {result['week']}, Platform: {result['platform']}")
        print(f"   Category: {result['category']}, Count: {result['count']}")
        print()
    
    # Get preferred aggregation
    preferred = aggregator.get_preferred_aggregation(aggregated)
    aggregation_type = 'region' if aggregated['by_region'] else 'country' if aggregated['by_country'] else 'language'
    print(f"🎯 PREFERRED AGGREGATION: Using {aggregation_type}-based aggregation")
    print(f"   Total aggregated records: {len(preferred)}")
    
    # Export results
    output_file = aggregator.export_results(aggregated)
    if output_file:
        print(f"💾 Results exported to: {output_file}")
    
    # Summary statistics
    print()
    print("=" * 55)
    print("📊 SUMMARY STATISTICS")
    print("=" * 55)
    print(f"   • Total texts processed: {len(demo_data)}")
    print(f"   • Texts with matches: {len(classified_results)}")
    print(f"   • Classification accuracy: {len(classified_results)/len(demo_data)*100:.1f}%")
    print(f"   • Region aggregations: {len(aggregated['by_region'])}")
    print(f"   • Country aggregations: {len(aggregated['by_country'])}")
    print(f"   • Language aggregations: {len(aggregated['by_language'])}")
    
    # Category breakdown
    categories = {}
    for result in classified_results:
        categories[result['category']] = categories.get(result['category'], 0) + 1
    
    print(f"   📂 Categories detected:")
    for category, count in sorted(categories.items()):
        print(f"      • {category}: {count} matches")
    
    print()
    print("=" * 55)
    print("✅ Enhanced Demo Completed Successfully!")
    print()
    print("💡 Key Insights:")
    print("   • Language-based aggregation is most reliable (always available)")
    print("   • Region/Country data is sparse but valuable when available")
    print("   • Hierarchical approach provides multiple analysis perspectives")
    print("   • Word boundary matching prevents false positives")
    print("=" * 55)

def show_statistics():
    """Show detailed statistics about the keyword database"""
    config = Config()
    
    try:
        with open(config.keywords_path, 'r', encoding='utf-8') as f:
            keywords = json.load(f)
        
        print()
        print("📊 KEYWORD DATABASE STATISTICS")
        print("=" * 40)
        
        total_keywords = 0
        for category, languages in keywords.items():
            category_total = 0
            print(f"📂 {category}:")
            for lang, keyword_list in languages.items():
                count = len(keyword_list)
                category_total += count
                print(f"   • {lang}: {count} keywords")
            print(f"   📊 Category total: {category_total} keywords")
            print()
            total_keywords += category_total
        
        print(f"🎯 OVERALL STATISTICS:")
        print(f"   • Total categories: {len(keywords)}")
        print(f"   • Total keywords: {total_keywords}")
        print(f"   • Average keywords per category: {total_keywords/len(keywords):.1f}")
        
    except Exception as e:
        print(f"Error loading keywords: {e}")

def main():
    """Main function with command line arguments"""
    parser = argparse.ArgumentParser(description='Enhanced Demo for Digital Radicalization Research')
    parser.add_argument('--stats', action='store_true', help='Show keyword database statistics')
    parser.add_argument('--demo', action='store_true', help='Run the enhanced demo')
    
    args = parser.parse_args()
    
    if args.stats:
        show_statistics()
    elif args.demo or len(sys.argv) == 1:  # Default to demo if no args
        run_enhanced_demo()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()