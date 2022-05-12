from heapq import heapify, heappush, heappop
from threading import Lock

class QueueHandler:
    def __init__(self) -> None:
        self._heap = []
        heapify(self._heap)
        self.lock = Lock()
        self._get_others = True

    def insert_host(self, host : str, priority : int) -> None:
        if len(self._heap) >= 5e2:
            self._get_others = False
            return
        if self._get_others or len(self._heap) <= 5e2//2:
            self._get_others = True
            self.lock.acquire()
            if self._get_others:
                heappush(self._heap, (priority, host))
            self.lock.release()
        
    def next_host(self) -> str:
        self.lock.acquire()
        if len(self._heap) == 0:
            host, priority = None, None
        else:
            priority, host = heappop(self._heap)
        self.lock.release()
        return host,priority

    def __len__(self) -> int:
        return len(self._heap)

    def __str__(self) -> str:
        return str(self._heap)