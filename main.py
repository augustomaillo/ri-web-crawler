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

if __name__ == "__main__":
    with open(args.seeds,'r') as f:
        seeds = f.read().splitlines()
    print(seeds)
    threads = 5

    main_queue = QueueHandler()
    for url in seeds:
        main_queue.insert_page(url, 0)
    crawling_handler = CrawlingHandler(main_queue, threads)
    
    tc = ThreadingController(max_threads=threads)
    tc.setup_callback(crawling_handler.run)
    tc.run()
    tc.join()
