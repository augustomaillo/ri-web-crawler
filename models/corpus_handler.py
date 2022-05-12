from queue import Full
from threading import Lock
import random
from warcio.warcwriter import WARCWriter
from warcio.statusandheaders import StatusAndHeaders

class CorpusHandler:
    def __init__(self, limit) -> None:
        self._corpus_size = 0
        self.lock = Lock()
        self.write_lock = Lock()
        self._limit = limit
        self._pendent = []
        
        self._saved = 0
        self._file_num = 81
        self._file =  open(f'corpus_continue/pack_{self._file_num:03d}.gz', 'wb')
        self._writer_object = WARCWriter(self._file, gzip=True)

    def insert(self, page : str) -> None:
        self.lock.acquire()
        if self._corpus_size == self._limit:
            self.lock.release()
            return False
        self._corpus_size +=1
        self._save_page(page)
        self._saved +=1
        if self._saved == 1e3 and self._corpus_size < self._limit:
            self.finish()
            self._file_num += 1
            self._file = open(f'corpus_continue/pack_{self._file_num:03d}.gz', 'wb')
            self._writer_object = WARCWriter(self._file, gzip=True)
            self._saved = 0
        self.lock.release()
        return True

    def __len__(self) -> int:
        return self._corpus_size

    def _save_page(self, page ) -> None:
        url, content, headers = page
        record = self._writer_object.create_warc_record(
            url,
            'response',
            payload=content,
            http_headers=StatusAndHeaders('200 OK', headers, protocol='HTTP/1.1')
        )
        self._writer_object.write_record(record)
        content.close()

    def finish(self) -> None:
        self._file.close()

    @property
    def size(self) -> int:
        return self._corpus_size