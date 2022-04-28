from heapq import heapify, heappush, heappop
from threading import Lock

class QueueHandler:
    def __init__(self) -> None:
        self._heap = []
        heapify(self._heap)
        self.lock = Lock()

    def insert_host(self, host : str, priority : int) -> None:
        self.lock.acquire()
        heappush(self._heap, (priority, host))
        self.lock.release()
    
    def next_host(self) -> str:
        self.lock.acquire()
        if len(self._heap) == 0:
            host = None
        else:
            host = heappop(self._heap)[1]
        self.lock.release()
        return host

    def __len__(self) -> int:
        return len(self._heap)

    def __str__(self) -> str:
        return str(self._heap)