import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-s', '--seeds', help='Seeds file', required=True)
parser.add_argument('-n', '--number', help='Web pages to crawl', required=True)
parser.add_argument('-d', '--debug', help='Debug mode', action='store_true', required=False)
args = parser.parse_args()

from models.crawling_handler import CrawlingHandler
from models.page_handler import PageHandler
from models.queue_handler import QueueHandler
from models.threading_controller import ThreadingController
from url_normalize import url_normalize
from models.knowledge_pool import KnowledgePool
from urllib.parse import urlparse, urlunparse


if __name__ == "__main__":
    with open(args.seeds,'r') as f:
        seeds = f.read().splitlines()
    print(seeds)
    threads = 10

    main_queue = QueueHandler()
    knowledge_pool = KnowledgePool()
    for url in seeds:
        url = url_normalize(url)
        url_parsed = urlparse(url)

        knowledge_pool.insert_host(url_parsed.netloc, 0)
        knowledge_pool.add_page_to_host(url_parsed.netloc, url)

        main_queue.insert_host(url_parsed.netloc, 0)


    crawling_handler = CrawlingHandler(main_queue, knowledge_pool, threads)

    # crawling_handler.run(1)

    tc = ThreadingController(max_threads=threads)
    tc.setup_callback(crawling_handler.run)
    tc.run()
    tc.join()

    print(len(crawling_handler.corpus._corpus))
    import json
    print(crawling_handler.corpus._corpus)
    
    j = [json.loads(s) for s in crawling_handler.corpus._corpus]
    with open('corpus.test', 'w') as f:
        json.dump(j, f, indent=4, ensure_ascii=False)
    # print(crawling_handler._queue)