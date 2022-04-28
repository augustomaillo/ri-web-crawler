from queue import Full
from models.queue_handler import QueueHandler
from models.page_handler import PageHandler
from models.corpus_handler import CorpusHandler
from models.knowledge_pool import KnowledgePool
from urllib.parse import urlparse
from time import time

class CrawlingHandler:
    def __init__(self, queue : QueueHandler, knowledge_pool: KnowledgePool, threads:int) -> None:
        self._queue = queue
        self._is_crawling = [0] * threads

        self.corpus = CorpusHandler(20)
        self._knowledge_pool = knowledge_pool
        self.s = time()
    
    def run(self, n) -> None:
        while len(self.corpus) < 20:
            host = self._queue.next_host()
            host_counter = 0
            while host is not None and host_counter < 32 and self._knowledge_pool.host_url_num(host):
                url = self._knowledge_pool.get_host_url(host)
                from requests import Session
                sess = Session()
                if url is not None:
                    self._is_crawling[n] = 1
                    # print(url)
                    page = PageHandler(url=url, known_hosts=self._knowledge_pool, sess=sess)
                    res = page.obtain()
                    if res is None:
                        continue
                    try:
                        self.corpus.insert(res)
                    except Full:
                        print('Corpus full filled', time()-self.s)
                        break
                    print('+'*20)
                    print('Corpus: ', len(self.corpus))
                    self._add_to_queue(page.discovered_urls, 0)

                self._is_crawling[n] = 0

            # if sum(self._is_crawling) == 0:
            #     # print('All done')
            #     break
        print('end of thread %d' % n)

    def _add_to_queue(self, discovered_urls, parent_priority) -> None:
        for url in discovered_urls:
            url_parsed = urlparse(url)
            if not self._knowledge_pool.check_host(url_parsed.netloc):
                self._knowledge_pool.insert_host(url_parsed.netloc, parent_priority+1)
                prev_urls = 0
            else:
                prev_urls = self._knowledge_pool.host_url_num(url_parsed.netloc)
            if not self._knowledge_pool.check(url):
                self._knowledge_pool.insert(url)
                self._knowledge_pool.add_page_to_host(url_parsed.netloc, url)

            if not prev_urls:
                self._queue.insert_host(url_parsed.netloc, parent_priority+1)