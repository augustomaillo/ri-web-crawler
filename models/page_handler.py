import requests
import bs4
import datetime
from url_normalize import url_normalize
from urllib.parse import urlparse, urlunparse
import json
from models.knowledge_pool import KnowledgePool

class PageHandler:
    def __init__(self, url : str, known_hosts : KnowledgePool, sess) -> None:
        self._parsed_url = urlparse(url)
        self._known_hosts = known_hosts
        self._discovered_urls = set()
        self._sess = sess

    def _check_robots(self) -> bool:
        if self._known_hosts.host_delay(self._parsed_url.netloc) < 0:
            # todo : delay certo
            self._known_hosts.update_host_delay(self._parsed_url.netloc, 0)
        
        allowed_time = self._known_hosts.host_allowed_time(self._parsed_url.netloc)
        return datetime.datetime.now().timestamp() >= allowed_time

    def obtain(self) -> str:
        while self._check_robots():
            self._known_hosts.update_host_allowed(
                self._parsed_url.netloc,
                datetime.datetime.now().timestamp() + self._known_hosts.host_delay(self._parsed_url.netloc)
            )
            try:
                print(self._parsed_url)
                response = self._sess.get(
                    urlunparse(self._parsed_url),
                    headers={
                        'User-Agent': 'im-not-a-robot',
                        'Accept': 'text/html',
                    },
                    timeout=1)
            except Exception as e:
                return None
            if response.status_code != 200:
                return None

            html = bs4.BeautifulSoup(response.text, "html.parser")
            encoding = response.encoding
            print(encoding)
            if html.body is None or html.title is None:
                return None
            snippet = " ".join(html.body.get_text().split()[:20])
            print(snippet)
            try:
                snippet = snippet.encode(encoding).decode('utf-8')
            except:
                return None
            output = {
                "URL:": urlunparse(self._parsed_url),
                "Title": html.title.string.encode(encoding).decode('utf-8'),
                "Text" : snippet,
                "Timestamp": datetime.datetime.now().timestamp()
            }

            print(urlunparse(self._parsed_url), '\n',
                json.dumps(output, indent=4, ensure_ascii=False))
            self._get_links(html)
            return json.dumps(output, indent=4, ensure_ascii=False)

    def _get_links(self, html) -> list:
        for a in html.find_all('a', href=True):
            url = a['href'].replace(' ', '')
            if url.startswith('/'):
                url = self._parsed_url.scheme + '://' + self._parsed_url.netloc + url
            elif url.startswith('#') or url == '' or url.startswith('mailto') or url.startswith('tel'):
                continue
            url = url_normalize(url)
            self._discovered_urls.add(url)

    @property
    def discovered_urls(self) -> set:
        return self._discovered_urls
    

