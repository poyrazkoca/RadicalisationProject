"""
Web scraping module for collecting data from various platforms
"""

import time
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    requests = None

try:
    from urllib.parse import urljoin, urlparse
    URLLIB_AVAILABLE = True
except ImportError:
    URLLIB_AVAILABLE = False

try:
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False
    BeautifulSoup = None

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

class WebScraper:
    """Multi-platform web scraper for social media and news content"""
    
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize HTTP session if requests is available
        if REQUESTS_AVAILABLE:
            self.session = requests.Session()
            self.session.headers.update({
                'User-Agent': config.get('scraping.user_agent')
            })
        else:
            self.session = None
        
        # Setup Selenium WebDriver (headless) if available
        if SELENIUM_AVAILABLE:
            self.driver_options = Options()
            self.driver_options.add_argument('--headless')
            self.driver_options.add_argument('--no-sandbox')
            self.driver_options.add_argument('--disable-dev-shm-usage')
            self.driver_options.add_argument(f'--user-agent={config.get("scraping.user_agent")}')
        else:
            self.driver_options = None
    
    def collect_data(self, platform: str, region: str = None, 
                    start_date: datetime = None, end_date: datetime = None) -> List[Dict[str, Any]]:
        """Main data collection method"""
        
        if not self.config.is_platform_enabled(platform):
            self.logger.warning(f"Platform {platform} is not enabled")
            return []
        
        self.logger.info(f"Starting data collection for {platform}")
        
        # Set default date range if not provided
        if not end_date:
            end_date = datetime.now()
        if not start_date:
            start_date = end_date - timedelta(days=7)
        
        try:
            if platform == "twitter":
                return self._scrape_twitter(region, start_date, end_date)
            elif platform == "reddit":
                return self._scrape_reddit(region, start_date, end_date)
            elif platform == "forum":
                return self._scrape_forums(region, start_date, end_date)
            elif platform == "news":
                return self._scrape_news(region, start_date, end_date)
            else:
                self.logger.error(f"Unsupported platform: {platform}")
                return []
                
        except Exception as e:
            self.logger.error(f"Error scraping {platform}: {str(e)}")
            return []
    
    def _scrape_twitter(self, region: str, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """Scrape Twitter/X content (Note: Requires API access in real implementation)"""
        self.logger.info("Scraping Twitter content")
        
        # Demo data for feasibility testing
        demo_tweets = [
            {
                "text": "Political discussion about current events and social issues",
                "platform": "twitter",
                "timestamp": datetime.now() - timedelta(hours=2),
                "location": region or "Unknown",
                "url": "https://twitter.com/demo/status/123",
                "user_id": "demo_user_1",
                "engagement": {"likes": 5, "retweets": 2, "replies": 1}
            },
            {
                "text": "News discussion with strong opinions about recent developments",
                "platform": "twitter",
                "timestamp": datetime.now() - timedelta(hours=5),
                "location": region or "Unknown",
                "url": "https://twitter.com/demo/status/124",
                "user_id": "demo_user_2",
                "engagement": {"likes": 12, "retweets": 6, "replies": 3}
            }
        ]
        
        # In real implementation, you would use Twitter API v2:
        # - tweepy library for API access
        # - Search tweets with relevant keywords
        # - Filter by location and date range
        # - Handle rate limiting
        
        return demo_tweets
    
    def _scrape_reddit(self, region: str, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """Scrape Reddit content"""
        self.logger.info("Scraping Reddit content")
        
        # Demo data for feasibility testing
        demo_posts = [
            {
                "text": "Discussion thread about regional politics and social movements",
                "platform": "reddit",
                "timestamp": datetime.now() - timedelta(hours=1),
                "location": region or "Unknown",
                "url": "https://reddit.com/r/worldnews/comments/demo1",
                "subreddit": "worldnews",
                "score": 45,
                "num_comments": 23
            }
        ]
        
        # In real implementation, you would use PRAW (Python Reddit API Wrapper):
        # - Search subreddits for relevant content
        # - Filter by date range and region-specific subreddits
        # - Extract post and comment text
        # - Handle API rate limits
        
        return demo_posts
    
    def _scrape_forums(self, region: str, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """Scrape forum content using web scraping"""
        self.logger.info("Scraping forum content")
        
        forum_sites = self.config.get("platforms.forum.sites", [])
        all_posts = []
        
        for site in forum_sites:
            try:
                posts = self._scrape_generic_forum(site, region, start_date, end_date)
                all_posts.extend(posts)
                
                # Rate limiting
                time.sleep(self.config.get("scraping.delay_between_requests", 2))
                
            except Exception as e:
                self.logger.error(f"Error scraping forum {site}: {str(e)}")
                continue
        
        return all_posts
    
    def _scrape_generic_forum(self, site: str, region: str, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """Generic forum scraping method"""
        
        # Demo data - in real implementation, this would scrape actual forums
        demo_posts = [
            {
                "text": "Forum discussion about local issues and community concerns",
                "platform": "forum",
                "timestamp": datetime.now() - timedelta(hours=3),
                "location": region or "Unknown",
                "url": f"https://{site}/thread/demo",
                "forum_name": site,
                "thread_title": "Community Discussion",
                "author": "forum_user_1"
            }
        ]
        
        return demo_posts
    
    def _scrape_news(self, region: str, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """Scrape news articles"""
        self.logger.info("Scraping news content")
        
        news_sites = self.config.get("platforms.news.sites", [])
        all_articles = []
        
        for site in news_sites:
            try:
                articles = self._scrape_news_site(site, region, start_date, end_date)
                all_articles.extend(articles)
                
                # Rate limiting
                time.sleep(self.config.get("scraping.delay_between_requests", 2))
                
            except Exception as e:
                self.logger.error(f"Error scraping news site {site}: {str(e)}")
                continue
        
        return all_articles
    
    def _scrape_news_site(self, site: str, region: str, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """Scrape individual news site"""
        
        # Demo data - in real implementation, this would scrape actual news sites
        demo_articles = [
            {
                "text": "News article discussing recent political and social developments in the region",
                "platform": "news",
                "timestamp": datetime.now() - timedelta(hours=4),
                "location": region or "Unknown",
                "url": f"https://{site}/article/demo",
                "title": "Regional News Update",
                "author": "News Reporter",
                "site": site
            }
        ]
        
        return demo_articles
    
    def _make_request(self, url: str, retries: int = None):
        """Make HTTP request with retry logic"""
        if not REQUESTS_AVAILABLE or not self.session:
            self.logger.error("Requests library not available for HTTP requests")
            return None
        
        max_retries = retries or self.config.get("scraping.max_retries", 3)
        timeout = self.config.get("scraping.timeout", 30)
        
        for attempt in range(max_retries):
            try:
                response = self.session.get(url, timeout=timeout)
                response.raise_for_status()
                return response
            except Exception as e:
                if attempt == max_retries - 1:
                    raise e
                self.logger.warning(f"Request failed (attempt {attempt + 1}/{max_retries}): {str(e)}")
                time.sleep(2 ** attempt)  # Exponential backoff
    
    def _extract_text_from_html(self, html: str) -> str:
        """Extract clean text from HTML content"""
        if not BS4_AVAILABLE:
            # Simple text extraction without BeautifulSoup
            import re
            # Remove script and style tags
            html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
            html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL | re.IGNORECASE)
            # Remove all HTML tags
            text = re.sub(r'<[^>]+>', '', html)
            # Clean up whitespace
            text = ' '.join(text.split())
            return text
        
        soup = BeautifulSoup(html, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Get text and clean it
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        return text
    
    def close(self):
        """Clean up resources"""
        if hasattr(self, 'driver'):
            self.driver.quit()
        if self.session:
            self.session.close()