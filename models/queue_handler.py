from heapq import heapify, heappush, heappop
from threading import Lock

class QueueHandler:
    def __init__(self) -> None:
        self._heap = []
        heapify(self._heap)
        self.lock = Lock()

    def insert_page(self, page : str, priority : int) -> None:
        self.lock.acquire()
        heappush(self._heap, (priority, page))
        self.lock.release()
    
    def next_page(self) -> str:
        self.lock.acquire()
        if len(self._heap) == 0:
            page = None
        else:
            page = heappop(self._heap)[1]
        self.lock.release()
        return page

    def __len__(self) -> int:
        return len(self._heap)