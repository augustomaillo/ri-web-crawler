import threading

class ThreadingController:
    def __init__(self, max_threads : int) -> None:
        self._max_threads = max_threads
        self._thread_pool = []

    def setup_callback(self, callback) -> None:
        assert callable(callback), "Callback must be callable"
        self._callback = callback
        self._thread_pool = [
            threading.Thread(target=self._callback, args=[i]) for i in range(self._max_threads)
            ]
    
    def run(self) -> None:
        for thread in self._thread_pool:
            thread.start()

    def join(self) -> None:
        for thread in self._thread_pool:
            thread.join()
        

            
