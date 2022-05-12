import argparse
from time import time

parser = argparse.ArgumentParser()
parser.add_argument('-s', '--seeds', help='Seeds file', required=True)
parser.add_argument('-n', '--number', help='Web pages to crawl', required=True, type=int)
parser.add_argument('-d', '--debug', help='Debug mode', action='store_true', required=False)
args = parser.parse_args()

from models.crawling_handler import CrawlingHandler
from models.page_handler import PageHandler
from models.queue_handler import QueueHandler
from models.threading_controller import ThreadingController
from url_normalize import url_normalize
from models.knowledge_pool import KnowledgePool
from urllib.parse import urlparse, urlunparse

# seeds_advanced = set()
# from warcio.archiveiterator import ArchiveIterator
# with open('corpus_2019006450/pack_082.gz', 'rb') as stream:
#     for record in ArchiveIterator(stream):
#         if record.rec_type == 'response':
#             seeds_advanced.add(record.rec_headers.get_header('WARC-Target-URI'))
# print('advanced seeds', len(seeds_advanced))
# import numpy as np
# seeds_advanced = np.random.choice(list(seeds_advanced), 5)
# print(seeds_advanced)

seeds_advanced = [
    'https://www.alergiaaoleitedevaca.com.br/guia-aplv/alergias-alimentares-ultimos-anos',
    'https://www.ambev.com.br/startups/',
    'https://www.alergoimunoservidor.com.br/product-page/estudantes-iamspe',
    'http://www.acsp.com.br/servicos/s/clube-de-descontos-acsp',
    'https://veja.abril.com.br/cultura/4-livros-que-fazem-literatura-de-primeira-com-humor-afiado/'
]

if __name__ == "__main__":
    with open(args.seeds,'r') as f:
        seeds = f.read().splitlines()
    print(seeds)
    threads = 10
    goal = args.number

    main_queue = QueueHandler()
    knowledge_pool = KnowledgePool()

    tc = ThreadingController(max_threads=threads)
    crawling_handler = CrawlingHandler(main_queue, knowledge_pool, threads, goal)
    crawling_handler._add_to_queue(list(seeds_advanced),0)

    status = [0 for i in range(threads)]
    def aux_func(n):
        status[n] = 1
        crawling_handler.run(n)
        status[n] = 0
    tc.setup_callback(aux_func)
    tc.run()
    from time import time, sleep
    def prettyprint(n):
        s = time()
        while crawling_handler.corpus.size < goal or sum(status) > 0:
            print(f' Corpus:  {crawling_handler.corpus.size}/{goal} - Elapsed: {time()-s:.4f} - {len(main_queue):03d} | Status: {sum(status)}', end='\r')
            sleep(0.16)
        print()
    a = ThreadingController(max_threads=1)
    a.setup_callback(prettyprint)
    a.run()
    # aux_func(0)
    tc.join()
    a.join()
    print('All joined')
    crawling_handler.finish()
    print(status)
    print(crawling_handler.corpus.size)

    import json
    # j = [json.loads(s) for s in crawling_handler.corpus._corpus]
    # with open('corpus.test', 'w') as f:
    #     json.dump(j, f, indent=4, ensure_ascii=False)
    # print(crawling_handler._queue)