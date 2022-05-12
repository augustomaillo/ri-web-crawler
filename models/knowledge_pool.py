from threading import Lock
from collections import deque


class KnowledgePool:
    def __init__(self) -> None:
        self._pool = set()
        self._host_pool = dict()
        self.lock = Lock()

    def insert_page(self, page : str) -> None:
        """ Insere uma pagina no pool de conhecimento """
        self.lock.acquire()
        self._pool.add(page)
        self.lock.release()

    def check_page(self, page : str) -> bool:
        """ Checa se uma pagina ja esta no pool de conhecimento """
        return page in self._pool
    
    def insert_host(self, host : str, priority : int) -> None:
        """ Insere o host no pool de conhecimento """
        if not host in self._host_pool:
            self.lock.acquire()

            self._host_pool[host] = {
                'priority': priority, # prioridade de crawling do host
                'url_queue': deque(), # fila de urls a serem crawled
                'allowed': 0, # timestamp de quando o host pode ser crawled
                'delay': -1, # tempo de espera para o host ser crawled
                'robots': None, # robots.txt do host (reppy.robots.Robots)
                'gathered': 0 # indica quantas paginas do host ja foram baixadas
            }
            self.lock.release()

    def check_host(self, host : str) -> bool:
        """ Checa se um host ja esta no pool de conhecimento """
        return host in self._host_pool
    
    def add_page_to_host(self, host : str, url : str) -> None:
        """ Associa uma url a um host """
        if len(self._host_pool[host]['url_queue']) < 256:
            self.lock.acquire()
            self._host_pool[host]['url_queue'].append(url)
            self.lock.release()

    def host_url_num(self, host : str) -> int:
        """ Retorna o numero de url associadas a um host"""
        return len(self._host_pool[host]['url_queue'])

    def get_host_url(self, host : str) -> str:
        """ Retorna a url da fila de urls a serem crawled do host """
        self.lock.acquire()
        url = self._host_pool[host]['url_queue'].popleft()
        self.lock.release()
        return url

    def host_allowed_time(self, host : str) -> int:
        """ Retorna o timestamp de quando o host pode ser crawled """
        return self._host_pool[host]['allowed']

    def host_delay(self, host : str) -> int:
        """ Retorna o tempo de espera para o host ser crawled """
        return self._host_pool[host]['delay']

    def update_host_priority(self, host : str, priority : int) -> None:
        """ Atualiza a prioridade de crawling do host """
        self.lock.acquire()
        self._host_pool[host]['priority'] = priority
        self.lock.release()

    def update_host_delay(self, host : str, delay : int) -> None:
        """ Atualiza o tempo de espera para o host ser crawled """
        self.lock.acquire()
        self._host_pool[host]['delay'] = delay
        self.lock.release()

    def update_host_allowed(self, host : str, allowed : int) -> None:
        """ Atualiza o timestamp de quando o host pode ser crawled """
        self.lock.acquire()
        self._host_pool[host]['allowed'] = allowed
        self.lock.release()

    def increase_gathered(self, host : str) -> None:
        """ Incrementa o numero de paginas baixadas do host """
        self.lock.acquire()
        self._host_pool[host]['gathered'] += 1
        self.lock.release()
    
    def get_gathered(self, host : str) -> int:
        """ Retorna o numero de paginas baixadas do host """
        return self._host_pool[host]['gathered']

    def clear_host_queue(self, host : str) -> None:
        """ Limpa a fila de urls a serem crawled do host """
        self.lock.acquire()
        self._host_pool[host]['url_queue'] = deque()
        self.lock.release()

    def update_robots(self, host : str, robots : str) -> None:
        """ Atualiza o robots.txt do host """
        self.lock.acquire()
        self._host_pool[host]['robots'] = robots
        self.lock.release()
    
    def robots(self, host : str) -> None:
        """ Retorna o robots.txt do host """
        return self._host_pool[host]['robots']