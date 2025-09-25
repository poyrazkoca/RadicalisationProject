"""
Keyword-based text classification module
"""

import json
import re
import logging
from datetime import datetime
from typing import Dict, List, Any, Set, Optional
from collections import defaultdict

try:
    from langdetect import detect, LangDetectError
    LANGDETECT_AVAILABLE = True
except ImportError:
    LANGDETECT_AVAILABLE = False
    detect = None
    LangDetectError = Exception

try:
    from textblob import TextBlob
    TEXTBLOB_AVAILABLE = True
except ImportError:
    TEXTBLOB_AVAILABLE = False
    TextBlob = None

class KeywordClassifier:
    """Classifier for categorizing text based on predefined keywords"""
    
    def __init__(self, keywords_path: str):
        self.logger = logging.getLogger(__name__)
        self.keywords = self._load_keywords(keywords_path)
        self.compiled_patterns = self._compile_keyword_patterns()
        
        # Language mapping for detection
        self.lang_mapping = {
            'tr': 'TR',
            'en': 'EN',
            'el': 'GR',  # Greek
            'de': 'DE',  # German
            'fr': 'FR',  # French
            'ar': 'AR',  # Arabic
        }
    
    def _load_keywords(self, keywords_path: str) -> Dict[str, Dict[str, List[str]]]:
        """Load keywords from JSON file"""
        try:
            with open(keywords_path, 'r', encoding='utf-8') as f:
                keywords = json.load(f)
            self.logger.info(f"Loaded {len(keywords)} keyword categories")
            return keywords
        except Exception as e:
            self.logger.error(f"Error loading keywords: {str(e)}")
            return {}
    
    def _compile_keyword_patterns(self) -> Dict[str, Dict[str, List[re.Pattern]]]:
        """Compile regex patterns for efficient keyword matching"""
        compiled = defaultdict(lambda: defaultdict(list))
        
        for category, languages in self.keywords.items():
            for lang, keywords in languages.items():
                for keyword in keywords:
                    # Create regex pattern for whole word matching
                    pattern = re.compile(
                        r'\b' + re.escape(keyword.lower()) + r'\b',
                        re.IGNORECASE | re.UNICODE
                    )
                    compiled[category][lang].append(pattern)
        
        return compiled
    
    def detect_language(self, text: str) -> str:
        """Detect the language of the text"""
        if LANGDETECT_AVAILABLE:
            try:
                detected_lang = detect(text)
                return self.lang_mapping.get(detected_lang, detected_lang.upper())
            except LangDetectError:
                pass
        
        # Fallback: Try to determine based on character patterns
        if self._contains_turkish_chars(text):
            return 'TR'
        elif self._contains_greek_chars(text):
            return 'GR'
        elif self._contains_arabic_chars(text):
            return 'AR'
        else:
            return 'EN'  # Default to English
    
    def _contains_turkish_chars(self, text: str) -> bool:
        """Check if text contains Turkish-specific characters"""
        turkish_chars = set('çğıöşüÇĞIİÖŞÜ')
        return any(char in turkish_chars for char in text)
    
    def _contains_greek_chars(self, text: str) -> bool:
        """Check if text contains Greek characters"""
        return any('\u0370' <= char <= '\u03FF' for char in text)
    
    def _contains_arabic_chars(self, text: str) -> bool:
        """Check if text contains Arabic characters"""
        return any('\u0600' <= char <= '\u06FF' for char in text)
    
    def classify_text(self, text: str, target_language: str = None) -> Dict[str, List[str]]:
        """
        Classify text into categories based on keyword matches
        
        Args:
            text: Text to classify
            target_language: Specific language to search (None for auto-detect)
        
        Returns:
            Dictionary mapping categories to matched keywords
        """
        if not text or not text.strip():
            return {}
        
        text_lower = text.lower()
        detected_lang = target_language or self.detect_language(text)
        matches = defaultdict(list)
        
        # Search for keywords in each category
        for category, languages in self.compiled_patterns.items():
            category_matches = set()
            
            # First try to match in detected/target language
            if detected_lang in languages:
                for pattern in languages[detected_lang]:
                    if pattern.search(text_lower):
                        # Extract the actual matched keyword
                        match = pattern.search(text_lower)
                        if match:
                            category_matches.add(match.group())
            
            # If no matches found and no specific language requested, try other languages
            if not category_matches and target_language is None:
                for lang, patterns in languages.items():
                    if lang != detected_lang:
                        for pattern in patterns:
                            if pattern.search(text_lower):
                                match = pattern.search(text_lower)
                                if match:
                                    category_matches.add(match.group())
            
            if category_matches:
                matches[category] = list(category_matches)
        
        return dict(matches)
    
    def classify_batch(self, texts: List[str], target_language: str = None) -> List[Dict[str, List[str]]]:
        """Classify multiple texts at once"""
        return [self.classify_text(text, target_language) for text in texts]
    
    def get_category_keywords(self, category: str, language: str = None) -> List[str]:
        """Get all keywords for a specific category and language"""
        if category not in self.keywords:
            return []
        
        if language:
            return self.keywords[category].get(language, [])
        else:
            # Return all keywords across all languages for the category
            all_keywords = []
            for lang_keywords in self.keywords[category].values():
                all_keywords.extend(lang_keywords)
            return list(set(all_keywords))  # Remove duplicates
    
    def get_all_categories(self) -> List[str]:
        """Get list of all available categories"""
        return list(self.keywords.keys())
    
    def get_supported_languages(self) -> Set[str]:
        """Get set of all supported languages"""
        languages = set()
        for category_data in self.keywords.values():
            languages.update(category_data.keys())
        return languages
    
    def calculate_radicalization_score(self, text: str) -> Dict[str, float]:
        """
        Calculate a radicalization score based on keyword matches
        
        Returns:
            Dictionary with category scores and overall score
        """
        matches = self.classify_text(text)
        scores = {}
        
        # Weight different categories differently
        category_weights = {
            'Violence_CallToAction': 3.0,
            'Group_Identity': 2.0,
            'Delegitimisation_Dehumanisation': 2.5,
            'Conspiracy_Polarising': 1.5,
            'Propaganda_Recruitment': 2.0,
            'Religious_Radical': 1.8,
            'PKK_Related': 2.2,
            'Conversion_Identity': 1.5
        }
        
        total_score = 0.0
        text_length = len(text.split())
        
        for category, matched_keywords in matches.items():
            # Score based on number of matches and category weight
            category_score = len(matched_keywords) * category_weights.get(category, 1.0)
            # Normalize by text length to account for longer texts
            normalized_score = category_score / max(text_length / 100, 1)
            scores[category] = normalized_score
            total_score += normalized_score
        
        scores['overall_score'] = total_score
        scores['risk_level'] = self._categorize_risk_level(total_score)
        
        return scores
    
    def _categorize_risk_level(self, score: float) -> str:
        """Categorize risk level based on score"""
        if score >= 5.0:
            return "HIGH"
        elif score >= 2.0:
            return "MEDIUM"
        elif score >= 0.5:
            return "LOW"
        else:
            return "MINIMAL"
    
    def analyze_text_details(self, text: str) -> Dict[str, Any]:
        """Provide detailed analysis of a text"""
        matches = self.classify_text(text)
        scores = self.calculate_radicalization_score(text)
        detected_lang = self.detect_language(text)
        
        # Get sentiment analysis
        if TEXTBLOB_AVAILABLE:
            try:
                blob = TextBlob(text)
                sentiment = {
                    'polarity': blob.sentiment.polarity,
                    'subjectivity': blob.sentiment.subjectivity
                }
            except:
                sentiment = {'polarity': 0.0, 'subjectivity': 0.0}
        else:
            sentiment = {'polarity': 0.0, 'subjectivity': 0.0}
        
        return {
            'text': text,
            'detected_language': detected_lang,
            'matched_categories': matches,
            'radicalization_scores': scores,
            'sentiment': sentiment,
            'word_count': len(text.split()),
            'char_count': len(text),
            'analysis_timestamp': str(datetime.now())
        }