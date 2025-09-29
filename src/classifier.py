import json
import re

class KeywordClassifier:
    def __init__(self, keyword_file):
        with open(keyword_file, "r", encoding="utf-8") as f:
            self.keywords = json.load(f)

    def classify_text(self, text, target_language="TR"):
        results = {}
        for category, langs in self.keywords.items():
            keywords = langs.get(target_language, [])
            found = [kw for kw in keywords if re.search(r"\b" + re.escape(kw) + r"\b", text, re.IGNORECASE)]
            if found:
                results[category] = found
        return results