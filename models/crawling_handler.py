from queue import Full
from models.queue_handler import QueueHandler
from models.page_handler import PageHandler
from models.corpus_handler import CorpusHandler
from models.knowledge_pool import KnowledgePool
from urllib.parse import urlparse
from url_normalize import url_normalize

from time import time, sleep
from requests import Session
from reppy.robots import Robots
from threading import Lock

td = False
class CrawlingHandler:
    def __init__(self, queue : QueueHandler, knowledge_pool: KnowledgePool, threads:int, goal : int) -> None:
        """
        Gerenciador principal de todo o processo de crawling
        Fornece uma interface para as threads inserirem e lerem as informacoes necessarias

        :param queue: Objeto que gerencia a fila principal
        :param knowledge_pool: Objeto que gerencia o que o crawler ja conhece
        :param threads: Numero de threads que o crawler devera usar
        :param goal: Numero de paginas que o crawler devera conhecer
        """
        self._queue = queue
        self._goal = goal
        self.corpus = CorpusHandler(goal)
        self._knowledge_pool = knowledge_pool
        self.s = time()
        self._finished = False
        self._host_limit_at_once = 64
        self._host_limit = 256
        self._lock = Lock()
    
    def run(self, n) -> None:
        """ 
        Método a ser executado em paralelo, controla todo o processo que uma thread deve executar

        :param n: Numero da thread que devera executar
        """
        while not self._finished and self.corpus.size < self._goal:
            host, priority = self._queue.next_host()
            host_counter = 0
            while host is not None \
                    and host_counter < self._host_limit_at_once \
                    and self._knowledge_pool.host_url_num(host) \
                    and self._knowledge_pool.get_gathered(host) < self._host_limit \
                    and not self._finished:
                if td: print(f'thread {n} is getting url')
                url = self._knowledge_pool.get_host_url(host)
                sess = Session()
                if url is not None and not self._finished:
                    page = PageHandler(url=url, known_hosts=self._knowledge_pool, sess=sess)
                    s = time()
                    if td: print(f'thread {n} is downloading url {url}')
                    res = page.obtain()
                    if res is None or self._finished:
                        continue
                    
                    s = time()
                    if td: print(f'thread {n} is inserting url')
                    space_available = self.corpus.insert(res)
                    if td: print(f'thread {n} is updating gathered')
                    self._knowledge_pool.increase_gathered(host)
                    if self._finished:
                        return
                    if not space_available:
                        self._finished = True
                        return
                    host_counter+=1
                    if td: print(f'thread {n} is adding to queue - {len(page.discovered_urls)} - {url}', self._finished)
                    self._add_to_queue(list(page.discovered_urls)[:256], priority)
                    if td: print(f'thread {n} is no more adding to queue')
                    delay = self._knowledge_pool.host_delay(host)
                    if delay > 3 or self._finished:
                        break
                    elif delay > 0:
                        if td: print(f'thread {n} is sleeping for {delay}\n', self._finished)
                        sleep(delay)

                    if td: print(f'thread {n} wakeup', self._finished)
                    if self._finished: return
                    if td: print(f'thread {n} will get another url - {self.corpus.size}/total')
            if host_counter >= self._host_limit_at_once:
                if td: print(f'thread {n} is reinserting host to queue')
                self._queue.insert_host(host, priority+1)
            
        self._finished = True

    def _add_to_queue(self, discovered_urls, parent_priority) -> None:
        """ 
        Insere as urls encontradas na fila principal

        :param discovered_urls: URLs encontradas na pagina
        :param parent_priority: Prioridade da pagina pai
        """
        for url in discovered_urls:
            if self._finished: return
            url_parsed = urlparse(url)
            host = url_parsed.netloc

            if not self._knowledge_pool.check_host(host) and not self._finished: 
                # nao conheco o host
                self._knowledge_pool.insert_host(host, parent_priority+1)
                host_robots = self._fetch_robots(host)
                self._knowledge_pool.update_robots(host, host_robots)
                # print('UPDATING DELAY OF HOST ', host, '\n\n')
                if host_robots is None or host_robots.agent('Firefox/47.0').delay is None:
                    self._knowledge_pool.update_host_delay(host, 0.1)
                else:
                    self._knowledge_pool.update_host_delay(
                        host, 
                        host_robots.agent('Firefox/47.0').delay
                    )
                # print('DELAY IS', self._knowledge_pool.host_delay(host), '\n\n')
                prev_urls = 0
            else:
                # conheco o host
                if self._knowledge_pool.get_gathered(host) == self._host_limit:
                    # atingi o limite do host
                    continue
                prev_urls = self._knowledge_pool.host_url_num(host)
            if not self._knowledge_pool.check_page(url):
                self._knowledge_pool.insert_page(url)
                self._knowledge_pool.add_page_to_host(host, url)

            if not prev_urls:
                # se o host não havia urls para serem lidas, adiciono o host a fila agora
                self._queue.insert_host(host, parent_priority+1)

    @staticmethod
    def _fetch_robots(host) -> None:
        """ Adquire, se existirem, as informacoes do robots.txt do host """
        try:
            robots = Robots.fetch(url_normalize(host) + 'robots.txt', timeout=2)
            return robots
        except:
            return None

    def finish(self) -> None:
        """
        Finaliza o processo de crawling
        """
        self.corpus.finish()
