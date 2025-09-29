import requests
from bs4 import BeautifulSoup
from datetime import datetime

class WebScraper:
    def collect_data(self, region="Turkey"):
        url = "https://www.hurriyet.com.tr/"
        resp = requests.get(url)
        soup = BeautifulSoup(resp.text, "html.parser")
        headlines = [h.get_text() for h in soup.select("h3")][:10]
        data = []
        for headline in headlines:
            data.append({
                "text": headline,
                "platform": "news",
                "timestamp": datetime.now().isoformat(),
                "location": "Turkey",
                "language": "TR"
            })
        return data
    