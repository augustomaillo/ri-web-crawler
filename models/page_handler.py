import requests
import bs4
import datetime
from url_normalize import url_normalize
import json

class PageHandler:
    def __init__(self, url : str) -> None:
        self._url = url

    def obtain(self) -> str:

        response = requests.get(self._url, headers={'User-Agent': 'im-not-a-robot'})
        html = bs4.BeautifulSoup(response.text, "html.parser")
        encoding = response.encoding.lower()
        snippet = " ".join(html.body.get_text().split()[:20])
        snippet = snippet.encode(encoding).decode('utf-8')

        # for a in html.find_all('a', href=True):
        #     print(a['href'])
        output = {
            "URL:": self._url,
            "Title": html.title.string.encode(encoding).decode('utf-8'),
            "Text" : snippet,
            "Timestamp": datetime.datetime.now().timestamp()
        }
        print(json.dumps(output, indent=4, ensure_ascii=False))
        return response.text

    
