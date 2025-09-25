"""
Production web scraper with real API integrations
"""

import time
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

# Production imports with fallbacks
try:
    import tweepy  # Twitter API
    TWEEPY_AVAILABLE = True
except ImportError:
    TWEEPY_AVAILABLE = False

try:
    import praw  # Reddit API
    PRAW_AVAILABLE = True
except ImportError:
    PRAW_AVAILABLE = False

try:
    import requests
    from bs4 import BeautifulSoup
    WEB_SCRAPING_AVAILABLE = True
except ImportError:
    WEB_SCRAPING_AVAILABLE = False

try:
    import feedparser  # RSS feeds
    FEEDPARSER_AVAILABLE = True
except ImportError:
    FEEDPARSER_AVAILABLE = False

class ProductionScraper:
    """Production-ready scraper with real API integrations"""
    
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize API clients
        self.twitter_client = self._init_twitter_client()
        self.reddit_client = self._init_reddit_client()
        
        # Initialize web scraping session
        if WEB_SCRAPING_AVAILABLE:
            self.session = requests.Session()
            self.session.headers.update({
                'User-Agent': config.get('scraping.user_agent')
            })
    
    def _init_twitter_client(self):
        """Initialize Twitter API client"""
        if not TWEEPY_AVAILABLE:
            self.logger.warning("Tweepy not available - Twitter scraping disabled")
            return None
            
        bearer_token = self.config.get_api_key("TWITTER_BEARER_TOKEN")
        if not bearer_token:
            self.logger.warning("Twitter Bearer Token not found - Twitter scraping disabled")
            return None
        
        try:
            client = tweepy.Client(bearer_token=bearer_token, wait_on_rate_limit=True)
            # Test the connection
            client.get_me()
            self.logger.info("Twitter API client initialized successfully")
            return client
        except Exception as e:
            self.logger.error(f"Failed to initialize Twitter client: {e}")
            return None
    
    def _init_reddit_client(self):
        """Initialize Reddit API client"""
        if not PRAW_AVAILABLE:
            self.logger.warning("PRAW not available - Reddit scraping disabled")
            return None
            
        client_id = self.config.get_api_key("REDDIT_CLIENT_ID")
        client_secret = self.config.get_api_key("REDDIT_CLIENT_SECRET")
        user_agent = self.config.get_api_key("REDDIT_USER_AGENT")
        
        if not all([client_id, client_secret, user_agent]):
            self.logger.warning("Reddit API credentials not complete - Reddit scraping disabled")
            return None
        
        try:
            reddit = praw.Reddit(
                client_id=client_id,
                client_secret=client_secret,
                user_agent=user_agent
            )
            # Test the connection
            reddit.user.me()
            self.logger.info("Reddit API client initialized successfully")
            return reddit
        except Exception as e:
            self.logger.error(f"Failed to initialize Reddit client: {e}")
            return None
    
    def collect_twitter_data(self, keywords: List[str], start_date: datetime, end_date: datetime, max_results: int = 100) -> List[Dict[str, Any]]:
        """Collect data from Twitter using API v2"""
        if not self.twitter_client:
            self.logger.warning("Twitter client not available")
            return []
        
        collected_data = []
        
        try:
            # Build search query
            query_parts = []
            
            # Add keywords
            if keywords:
                keyword_query = " OR ".join([f'"{keyword}"' for keyword in keywords[:10]])  # Max 10 keywords
                query_parts.append(f"({keyword_query})")
            
            # Add language filters
            search_operators = self.config.get("platforms.twitter.search_operators", [])
            for operator in search_operators[:3]:  # Max 3 operators
                query_parts.append(operator)
            
            # Remove retweets for original content
            query_parts.append("-is:retweet")
            
            query = " ".join(query_parts)
            
            self.logger.info(f"Twitter search query: {query}")
            
            # Search tweets
            tweets = tweepy.Paginator(
                self.twitter_client.search_recent_tweets,
                query=query,
                start_time=start_date,
                end_time=end_date,
                tweet_fields=['created_at', 'author_id', 'geo', 'lang', 'public_metrics', 'context_annotations'],
                max_results=min(max_results, 100)  # API limit
            ).flatten(limit=max_results)
            
            for tweet in tweets:
                # Extract location information
                location = "Unknown"
                if tweet.geo and tweet.geo.get('place_id'):
                    try:
                        place = self.twitter_client.get_place(tweet.geo['place_id'])
                        location = place.data.full_name if place.data else "Unknown"
                    except:
                        pass
                
                # Determine region from context annotations or language
                region = self._determine_region_from_tweet(tweet, location)
                
                collected_data.append({
                    'text': tweet.text,
                    'platform': 'twitter',
                    'timestamp': tweet.created_at,
                    'location': location,
                    'region': region,
                    'url': f"https://twitter.com/user/status/{tweet.id}",
                    'author_id': str(tweet.author_id),
                    'language': tweet.lang,
                    'engagement': {
                        'retweets': tweet.public_metrics.get('retweet_count', 0),
                        'likes': tweet.public_metrics.get('like_count', 0),
                        'replies': tweet.public_metrics.get('reply_count', 0)
                    },
                    'tweet_id': str(tweet.id)
                })
            
            self.logger.info(f"Collected {len(collected_data)} tweets")
            
        except Exception as e:
            self.logger.error(f"Error collecting Twitter data: {e}")
        
        return collected_data
    
    def collect_reddit_data(self, subreddits: List[str], keywords: List[str], limit: int = 100) -> List[Dict[str, Any]]:
        """Collect data from Reddit using PRAW"""
        if not self.reddit_client:
            self.logger.warning("Reddit client not available")
            return []
        
        collected_data = []
        
        try:
            for subreddit_name in subreddits:
                try:
                    subreddit = self.reddit_client.subreddit(subreddit_name)
                    
                    # Get recent posts
                    posts = subreddit.new(limit=limit // len(subreddits))
                    
                    for post in posts:
                        # Check if post contains keywords
                        text_to_check = f"{post.title} {post.selftext}".lower()
                        if any(keyword.lower() in text_to_check for keyword in keywords):
                            
                            # Determine region from subreddit
                            region = self._determine_region_from_subreddit(subreddit_name)
                            
                            collected_data.append({
                                'text': f"{post.title}\n{post.selftext}",
                                'platform': 'reddit',
                                'timestamp': datetime.fromtimestamp(post.created_utc),
                                'location': region,
                                'region': region,
                                'url': f"https://reddit.com{post.permalink}",
                                'subreddit': subreddit_name,
                                'author': str(post.author) if post.author else '[deleted]',
                                'score': post.score,
                                'num_comments': post.num_comments,
                                'post_id': post.id
                            })
                            
                            # Also collect top comments if enabled
                            if self.config.get("platforms.reddit.include_comments", True):
                                post.comments.replace_more(limit=3)  # Load more comments
                                for comment in post.comments.list()[:5]:  # Top 5 comments
                                    if hasattr(comment, 'body') and len(comment.body) > 20:
                                        collected_data.append({
                                            'text': comment.body,
                                            'platform': 'reddit',
                                            'timestamp': datetime.fromtimestamp(comment.created_utc),
                                            'location': region,
                                            'region': region,
                                            'url': f"https://reddit.com{post.permalink}{comment.id}",
                                            'subreddit': subreddit_name,
                                            'author': str(comment.author) if comment.author else '[deleted]',
                                            'score': comment.score,
                                            'parent_post': post.id,
                                            'comment_id': comment.id
                                        })
                
                except Exception as e:
                    self.logger.error(f"Error collecting from subreddit {subreddit_name}: {e}")
                    continue
            
            self.logger.info(f"Collected {len(collected_data)} Reddit items")
            
        except Exception as e:
            self.logger.error(f"Error collecting Reddit data: {e}")
        
        return collected_data
    
    def collect_news_data(self, sites: List[str], keywords: List[str], max_articles: int = 50) -> List[Dict[str, Any]]:
        """Collect data from news sites using RSS and web scraping"""
        if not WEB_SCRAPING_AVAILABLE:
            self.logger.warning("Web scraping libraries not available")
            return []
        
        collected_data = []
        
        # First try RSS feeds
        rss_feeds = self.config.get("platforms.news.rss_feeds", [])
        for rss_url in rss_feeds:
            try:
                if FEEDPARSER_AVAILABLE:
                    feed = feedparser.parse(rss_url)
                    for entry in feed.entries[:max_articles // len(rss_feeds)]:
                        # Check if article contains keywords
                        text_to_check = f"{entry.title} {entry.get('summary', '')}".lower()
                        if any(keyword.lower() in text_to_check for keyword in keywords):
                            
                            # Extract full article content
                            article_text = self._extract_article_content(entry.link)
                            
                            collected_data.append({
                                'text': f"{entry.title}\n{article_text}",
                                'platform': 'news',
                                'timestamp': datetime(*entry.published_parsed[:6]) if hasattr(entry, 'published_parsed') else datetime.now(),
                                'location': self._determine_region_from_url(entry.link),
                                'region': self._determine_region_from_url(entry.link),
                                'url': entry.link,
                                'title': entry.title,
                                'site': rss_url.split('/')[2],  # Extract domain
                                'summary': entry.get('summary', ''),
                                'article_id': entry.get('id', entry.link)
                            })
            except Exception as e:
                self.logger.error(f"Error processing RSS feed {rss_url}: {e}")
        
        self.logger.info(f"Collected {len(collected_data)} news articles")
        return collected_data
    
    def _extract_article_content(self, url: str) -> str:
        """Extract main content from news article"""
        try:
            response = self.session.get(url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Common article content selectors
            content_selectors = [
                'article', '.article-content', '.post-content', 
                '.entry-content', '.content', 'main', '.story-body'
            ]
            
            for selector in content_selectors:
                content = soup.select_one(selector)
                if content:
                    # Remove ads, social media, etc.
                    for remove in content.find_all(['script', 'style', '.ad', '.social', '.comments']):
                        remove.decompose()
                    
                    text = content.get_text(strip=True)
                    if len(text) > 100:  # Minimum article length
                        return text[:2000]  # Limit length
            
            # Fallback: get all paragraph text
            paragraphs = soup.find_all('p')
            text = ' '.join([p.get_text(strip=True) for p in paragraphs])
            return text[:2000] if text else ""
            
        except Exception as e:
            self.logger.error(f"Error extracting article content from {url}: {e}")
            return ""
    
    def _determine_region_from_tweet(self, tweet, location: str) -> str:
        """Determine region from tweet data"""
        # Priority: geo location > context annotations > language
        if location and location != "Unknown":
            return self._standardize_location(location)
        
        # Check context annotations for geographic info
        if hasattr(tweet, 'context_annotations'):
            for annotation in tweet.context_annotations or []:
                if annotation.get('domain', {}).get('name') == 'Place':
                    return self._standardize_location(annotation.get('entity', {}).get('name', ''))
        
        # Fallback to language-based region
        lang_to_region = {'tr': 'TR', 'en': 'XX', 'ar': 'SY', 'de': 'DE', 'fr': 'FR'}
        return lang_to_region.get(tweet.lang, 'XX')
    
    def _determine_region_from_subreddit(self, subreddit_name: str) -> str:
        """Determine region from subreddit name"""
        region_mapping = {
            'turkey': 'TR',
            'europe': 'EU', 
            'syriancivilwar': 'SY',
            'kurdistan': 'IQ',
            'germany': 'DE',
            'france': 'FR',
            'greece': 'GR'
        }
        return region_mapping.get(subreddit_name.lower(), 'XX')
    
    def _determine_region_from_url(self, url: str) -> str:
        """Determine region from news site URL"""
        if '.tr' in url:
            return 'TR'
        elif 'bbc.com' in url or '.uk' in url:
            return 'GB'
        elif 'dw.com' in url or '.de' in url:
            return 'DE'
        elif '.fr' in url:
            return 'FR'
        elif 'aljazeera' in url:
            return 'QA'
        elif 'rudaw' in url or 'kurdistan24' in url:
            return 'IQ'
        else:
            return 'XX'
    
    def _standardize_location(self, location: str) -> str:
        """Standardize location string to region code"""
        location_lower = location.lower()
        if any(term in location_lower for term in ['turkey', 'türkiye', 'istanbul', 'ankara']):
            return 'TR'
        elif any(term in location_lower for term in ['syria', 'damascus', 'aleppo']):
            return 'SY'
        elif any(term in location_lower for term in ['iraq', 'baghdad', 'kurdistan']):
            return 'IQ'
        elif any(term in location_lower for term in ['germany', 'berlin', 'deutschland']):
            return 'DE'
        elif any(term in location_lower for term in ['france', 'paris']):
            return 'FR'
        elif any(term in location_lower for term in ['greece', 'athens']):
            return 'GR'
        else:
            return 'XX'