from models.queue_handler import QueueHandler
from models.page_handler import PageHandler


class CrawlingHandler:
    def __init__(self, queue : QueueHandler, threads:int) -> None:
        self._queue = queue
        self._is_crawling = [0] * threads
    
    def run(self, n) -> None:
        while True:
            url = self._queue.next_page()
            if url is not None:
                self._is_crawling[n] = 1
                print(url)
                page = PageHandler(url=url)
                page.obtain()
                print('+'*20)
            self._is_crawling[n] = 0
            if sum(self._is_crawling) == 0:
                # print('All done')
                break
        print('end of thread %d' % n)