"""
Scheduler for continuous data collection
"""

import schedule
import time
import logging
from datetime import datetime, timedelta
from typing import List
import threading
import json
from pathlib import Path

from src.config import Config
from src.production_scraper import ProductionScraper
from src.classifier import KeywordClassifier
from src.aggregator import EnhancedAggregator

class DataCollectionScheduler:
    """Scheduler for automated data collection"""
    
    def __init__(self, config_path: str = None):
        self.config = Config(config_path)
        self.scraper = ProductionScraper(self.config)
        self.classifier = KeywordClassifier(self.config.keywords_path)
        self.aggregator = EnhancedAggregator()
        self.logger = logging.getLogger(__name__)
        
        self.is_running = False
        self.last_collection_times = {}
        
        # Create data storage directories
        self.raw_data_dir = Path("data/raw")
        self.processed_data_dir = Path("data/processed")
        self.raw_data_dir.mkdir(parents=True, exist_ok=True)
        self.processed_data_dir.mkdir(parents=True, exist_ok=True)
    
    def setup_schedule(self):
        """Set up collection schedule"""
        # Twitter: Every 30 minutes (respects rate limits)
        schedule.every(30).minutes.do(self.collect_twitter_data)
        
        # Reddit: Every hour
        schedule.every().hour.do(self.collect_reddit_data)
        
        # News: Every 2 hours
        schedule.every(2).hours.do(self.collect_news_data)
        
        # Process and aggregate: Every 6 hours
        schedule.every(6).hours.do(self.process_and_aggregate)
        
        # Generate daily report: Every day at 6 AM
        schedule.every().day.at("06:00").do(self.generate_daily_report)
        
        # Generate weekly report: Every Monday at 8 AM
        schedule.every().monday.at("08:00").do(self.generate_weekly_report)
        
        self.logger.info("Collection schedule set up successfully")
    
    def collect_twitter_data(self):
        """Collect Twitter data"""
        self.logger.info("Starting Twitter data collection")
        
        try:
            # Get keywords from all categories
            all_keywords = []
            for category, languages in self.config.keywords.items():
                for lang, keywords in languages.items():
                    all_keywords.extend(keywords[:5])  # Max 5 keywords per category
            
            # Collect data from the last 30 minutes
            end_time = datetime.now()
            start_time = end_time - timedelta(minutes=30)
            
            data = self.scraper.collect_twitter_data(
                keywords=all_keywords[:50],  # Twitter query limit
                start_date=start_time,
                end_date=end_time,
                max_results=100
            )
            
            if data:
                self._save_raw_data(data, "twitter")
                self.logger.info(f"Collected {len(data)} Twitter items")
            
        except Exception as e:
            self.logger.error(f"Error in Twitter collection: {e}")
    
    def collect_reddit_data(self):
        """Collect Reddit data"""
        self.logger.info("Starting Reddit data collection")
        
        try:
            subreddits = self.config.get("platforms.reddit.subreddits", [])
            all_keywords = []
            for category, languages in self.config.keywords.items():
                for lang, keywords in languages.items():
                    all_keywords.extend(keywords)
            
            data = self.scraper.collect_reddit_data(
                subreddits=subreddits,
                keywords=all_keywords,
                limit=200
            )
            
            if data:
                self._save_raw_data(data, "reddit")
                self.logger.info(f"Collected {len(data)} Reddit items")
            
        except Exception as e:
            self.logger.error(f"Error in Reddit collection: {e}")
    
    def collect_news_data(self):
        """Collect news data"""
        self.logger.info("Starting news data collection")
        
        try:
            sites = self.config.get("platforms.news.sites", [])
            all_keywords = []
            for category, languages in self.config.keywords.items():
                for lang, keywords in languages.items():
                    all_keywords.extend(keywords)
            
            data = self.scraper.collect_news_data(
                sites=sites,
                keywords=all_keywords,
                max_articles=100
            )
            
            if data:
                self._save_raw_data(data, "news")
                self.logger.info(f"Collected {len(data)} news items")
            
        except Exception as e:
            self.logger.error(f"Error in news collection: {e}")
    
    def process_and_aggregate(self):
        """Process raw data and create aggregations"""
        self.logger.info("Starting data processing and aggregation")
        
        try:
            # Load all raw data from the last 6 hours
            cutoff_time = datetime.now() - timedelta(hours=6)
            raw_data = self._load_recent_raw_data(cutoff_time)
            
            if not raw_data:
                self.logger.info("No new data to process")
                return
            
            # Classify all texts
            classified_data = []
            for item in raw_data:
                matches = self.classifier.classify_text(item["text"])
                if matches:
                    for category, keywords in matches.items():
                        classified_item = {
                            **item,
                            "category": category,
                            "matched_keywords": keywords,
                            "language": self.classifier.detect_language(item["text"])
                        }
                        classified_data.append(classified_item)
            
            # Aggregate results
            if classified_data:
                aggregated_results = self.aggregator.aggregate_weekly(classified_data)
                
                # Save processed data
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_path = self.processed_data_dir / f"aggregated_{timestamp}.json"
                self.aggregator.save_results(aggregated_results, str(output_path))
                
                self.logger.info(f"Processed {len(classified_data)} items into {len(aggregated_results)} aggregated results")
            
        except Exception as e:
            self.logger.error(f"Error in processing and aggregation: {e}")
    
    def generate_daily_report(self):
        """Generate daily summary report"""
        self.logger.info("Generating daily report")
        
        try:
            # Load processed data from the last 24 hours
            cutoff_time = datetime.now() - timedelta(days=1)
            processed_files = list(self.processed_data_dir.glob("aggregated_*.json"))
            
            recent_data = []
            for file_path in processed_files:
                # Check file modification time
                if datetime.fromtimestamp(file_path.stat().st_mtime) > cutoff_time:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        recent_data.extend(data.get('data', []))
            
            if recent_data:
                # Generate summary
                summary = self.aggregator.generate_summary_statistics(recent_data)
                
                # Save daily report
                report_date = datetime.now().strftime("%Y%m%d")
                report_path = Path("output") / f"daily_report_{report_date}.json"
                
                report_data = {
                    "report_type": "daily",
                    "date": report_date,
                    "summary": summary,
                    "data": recent_data
                }
                
                with open(report_path, 'w', encoding='utf-8') as f:
                    json.dump(report_data, f, indent=2, ensure_ascii=False)
                
                self.logger.info(f"Daily report saved to {report_path}")
            
        except Exception as e:
            self.logger.error(f"Error generating daily report: {e}")
    
    def generate_weekly_report(self):
        """Generate weekly summary report"""
        self.logger.info("Generating weekly report")
        
        try:
            # Load processed data from the last 7 days
            cutoff_time = datetime.now() - timedelta(days=7)
            processed_files = list(self.processed_data_dir.glob("aggregated_*.json"))
            
            recent_data = []
            for file_path in processed_files:
                if datetime.fromtimestamp(file_path.stat().st_mtime) > cutoff_time:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        recent_data.extend(data.get('data', []))
            
            if recent_data:
                # Generate comprehensive summary
                summary = self.aggregator.generate_summary_statistics(recent_data)
                
                # Save weekly report
                week_number = datetime.now().isocalendar()[1]
                year = datetime.now().year
                report_path = Path("output") / f"weekly_report_{year}W{week_number:02d}.json"
                
                report_data = {
                    "report_type": "weekly",
                    "week": f"{year}-W{week_number:02d}",
                    "summary": summary,
                    "data": recent_data
                }
                
                with open(report_path, 'w', encoding='utf-8') as f:
                    json.dump(report_data, f, indent=2, ensure_ascii=False)
                
                # Also create HTML report
                from src.visualizer import create_html_report
                html_path = create_html_report(report_data, str(report_path.with_suffix('.html')))
                
                self.logger.info(f"Weekly report saved to {report_path} and {html_path}")
            
        except Exception as e:
            self.logger.error(f"Error generating weekly report: {e}")
    
    def _save_raw_data(self, data: List[dict], platform: str):
        """Save raw collected data"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = self.raw_data_dir / f"{platform}_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)
    
    def _load_recent_raw_data(self, cutoff_time: datetime) -> List[dict]:
        """Load raw data files created after cutoff time"""
        all_data = []
        
        for platform in ['twitter', 'reddit', 'news', 'forum']:
            pattern = f"{platform}_*.json"
            files = list(self.raw_data_dir.glob(pattern))
            
            for file_path in files:
                # Check file modification time
                if datetime.fromtimestamp(file_path.stat().st_mtime) > cutoff_time:
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            all_data.extend(data)
                    except Exception as e:
                        self.logger.error(f"Error loading {file_path}: {e}")
        
        return all_data
    
    def start(self):
        """Start the scheduler"""
        self.setup_schedule()
        self.is_running = True
        
        self.logger.info("Data collection scheduler started")
        
        # Run initial collection
        self.collect_twitter_data()
        self.collect_reddit_data()
        self.collect_news_data()
        
        # Start schedule loop
        while self.is_running:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    
    def stop(self):
        """Stop the scheduler"""
        self.is_running = False
        self.logger.info("Data collection scheduler stopped")
    
    def run_in_background(self):
        """Run scheduler in background thread"""
        scheduler_thread = threading.Thread(target=self.start, daemon=True)
        scheduler_thread.start()
        return scheduler_thread

def main():
    """Main function to run the scheduler"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Data Collection Scheduler")
    parser.add_argument("--config", default="config/config.yaml", help="Config file path")
    parser.add_argument("--daemon", action="store_true", help="Run as daemon")
    
    args = parser.parse_args()
    
    # Setup logging
    from src.utils import setup_logging
    setup_logging("INFO")
    
    scheduler = DataCollectionScheduler(args.config)
    
    if args.daemon:
        # Run in background
        thread = scheduler.run_in_background()
        print("Scheduler running in background. Press Ctrl+C to stop.")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            scheduler.stop()
            print("Scheduler stopped")
    else:
        # Run in foreground
        try:
            scheduler.start()
        except KeyboardInterrupt:
            scheduler.stop()
            print("Scheduler stopped")

if __name__ == "__main__":
    main()