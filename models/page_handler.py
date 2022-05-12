from curses import raw
import requests
import bs4
import datetime
from url_normalize import url_normalize
from urllib.parse import urlparse, urlunparse
import json
from models.knowledge_pool import KnowledgePool
import io
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module='bs4')

class PageHandler:
    def __init__(self, url : str, known_hosts : KnowledgePool, sess) -> None:
        self._parsed_url = urlparse(url)
        self._known_hosts = known_hosts
        self._discovered_urls = set()
        self._sess = sess
        self._user_agent = 'Firefox/47.0'
        self._host = self._parsed_url.netloc

    def obtain(self) -> str:
        robots = self._known_hosts.robots(self._host)
        if robots is not None and not robots.allowed(
            urlunparse(self._parsed_url),
            self._user_agent
            ):
            return None
        try:
            response = self._sess.get(
                urlunparse(self._parsed_url),
                headers={
                    'User-Agent': self._user_agent,
                    'Accept': 'text/html',
                },
                stream=True,
                timeout=3)
            assert response.headers['Content-Type'].startswith('text/html')
            response.encoding = 'utf-8'
        except Exception as e:
            return None
        if response.status_code != 200:
            return None
        try:
            text = response.text
            encoding = response.encoding
            raw_bytes = io.BytesIO(bytes(text, encoding=encoding))
            html = bs4.BeautifulSoup(text, "html.parser")
            snippet = " ".join(html.body.get_text().split()[:20])
            snippet = snippet.encode(encoding).decode('utf-8')
            title = html.title.string.encode(encoding).decode('utf-8')
        except:
            return None

        if False:
            print(f"{{",
                f"  URL: {urlunparse(self._parsed_url)},",
                f"  Title: {title},",
                f"  Text: {snippet},",
                f"  Timestamp: {datetime.datetime.now().timestamp()},",
                f"}}",
                sep='\n'
            )

        self._get_links(html)
        return url_normalize(urlunparse(self._parsed_url)), raw_bytes, response.headers.items()

    def _get_links(self, html) -> list:
        for a in html.find_all('a', href=True):
            url = a['href'].replace(' ', '')
            if url.startswith('/'):
                url = self._parsed_url.scheme + '://' + self._host + url
            elif url.startswith('#') or url == '' or url.startswith('mailto') or url.startswith('tel'):
                continue
            try:
                url = url_normalize(url)
            except:
                continue
            self._discovered_urls.add(url)

    @property
    def discovered_urls(self) -> set:
        return self._discovered_urls

