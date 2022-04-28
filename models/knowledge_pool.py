from threading import Lock
from collections import deque


class KnowledgePool:
    def __init__(self) -> None:
        self._pool = set()
        self._host_pool = dict()
        self.lock = Lock()

    def insert(self, page : str) -> None:
        self.lock.acquire()
        self._pool.add(page)
        self.lock.release()

    def check(self, page : str) -> bool:
        self.lock.acquire()
        res = page in self._pool
        self.lock.release()
        return res
    
    def insert_host(self, host : str, priority : int) -> None:
        self.lock.acquire()
        if not host in self._host_pool:
            self._host_pool[host] = {
                'priority': priority,
                'url_queue': deque(),
                'allowed': 0,
                'delay': -1,
            }
        self.lock.release()

    def check_host(self, host : str) -> bool:
        self.lock.acquire()
        res = host in self._host_pool
        self.lock.release()
        return res
    
    def add_page_to_host(self, host : str, url : str) -> None:
        self.lock.acquire()
        self._host_pool[host]['url_queue'].append(url)
        self.lock.release()

    def host_url_num(self, host : str) -> int:
        self.lock.acquire()
        res = len(self._host_pool[host]['url_queue'])
        self.lock.release()
        return res

    def get_host_url(self, host : str) -> str:
        self.lock.acquire()
        url = self._host_pool[host]['url_queue'].popleft()
        self.lock.release()
        return url

    def host_allowed_time(self, host : str) -> int:
        res = self._host_pool[host]['allowed']
        return res

    def host_delay(self, host : str) -> int:
        res = self._host_pool[host]['delay']
        return res

    def update_host_priority(self, host : str, priority : int) -> None:
        self.lock.acquire()
        self._host_pool[host]['priority'] = priority
        self.lock.release()

    def update_host_delay(self, host : str, delay : int) -> None:
        self.lock.acquire()
        self._host_pool[host]['delay'] = delay
        self.lock.release()

    def update_host_allowed(self, host : str, allowed : int) -> None:
        self.lock.acquire()
        self._host_pool[host]['allowed'] = allowed
        self.lock.release()