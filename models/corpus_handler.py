from queue import Full
from threading import Lock


class CorpusHandler:
    def __init__(self, limit) -> None:
        self._corpus = set()
        self.lock = Lock()
        self._limit = limit

    def insert(self, page : str) -> None:
        self.lock.acquire()
        if len(self._corpus) == self._limit:
            self.lock.release()
            raise Full
        self._corpus.add(page)
        self.lock.release()

    def __len__(self) -> int:
        return len(self._corpus)