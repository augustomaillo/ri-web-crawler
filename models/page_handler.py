import requests
import bs4
import datetime
from url_normalize import url_normalize
from urllib.parse import urlparse
import json

class PageHandler:
    def __init__(self, url : str, known_hosts) -> None:
        self._url = url
        self._parsed_url = urlparse(url)
        self._known_hosts = known_hosts

    def _check_robots(self) -> bool:
        if self._parsed_url.netloc in self._known_hosts:
            allowed_time = self._known_hosts[self._parsed_url.netloc]['allowed']
            return datetime.datetime.now().timestamp() >= allowed_time
        else:
            # todo: add to known hosts and get delay (if any)
            self._known_hosts[self._parsed_url.netloc] = {'allowed': 0, 'delay': 0}
            return True

    def obtain(self) -> str:
        if self._check_robots():
            self._known_hosts[self._parsed_url.netloc]['allowed'] = {
                'allowed': datetime.datetime.now().timestamp() + self._known_hosts[self._parsed_url.netloc]['delay']
                }
            response = requests.get(self._url, headers={
                'User-Agent': 'im-not-a-robot',
                'Accept': 'text/html',
                })
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
        else: 
            # fazer url voltar a fila
            pass


    
