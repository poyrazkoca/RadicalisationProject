import json
import re

class KeywordClassifier:
    def __init__(self, keywords_path='data/keywords.json'):
        with open(keywords_path, 'r', encoding='utf-8') as f:
            self.keywords = json.load(f)
    
    def classify_posts(self, posts):
        """Classify posts based on keyword matching"""
        print("🔍 Starting keyword classification...")
        
        matches = []
        for post in posts:
            text_lower = post['text'].lower()
            lang = post['language']
            
            for category, lang_keywords in self.keywords.items():
                if lang in lang_keywords:
                    for keyword in lang_keywords[lang]:
                        # Use word boundaries to avoid partial matches
                        pattern = r'\b' + re.escape(keyword.lower()) + r'\b'
                        if re.search(pattern, text_lower):
                            matches.append({
                                'platform': post['platform'],
                                'timestamp': post['timestamp'],
                                'region': post['region'],
                                'language': post['language'],
                                'category': category
                            })
                            break  # One match per category per post
    
        print(f"✅ Found {len(matches)} keyword matches")
        return matches