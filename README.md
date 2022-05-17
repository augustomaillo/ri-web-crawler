# Python Web Crawler

This repo contains a python web crawler implementation, for Information Retrieval subject at Federal University of Minas Gerais.

The built implementation ensures crawling politeness and time efficiency by using threading parallelism.

## How it works

The crawler explore seeds pages in order to find outlinks and, in the future, explore the outlinks found. 

HTML pages were saved in batches of 1,000 in WARC files.

To choose a page to crawl, all threads shares a common Heap Queue, where the nodes weights are the depth of the page regarding seeds. For this reason, pages "closer" to seeds are picked first.

## How to use

The main file expects a seed file (any text file containing one host per line) and a goal number for pages do crawl. Besides that, the script accepts an optional arg to define wheter to run in debug mode, supplying extra information.
Example:

```
python3 main.py -s my-seed-file.txt -n 1000 
```

## Further improvements
* Avoid busy waiting on mutual exclusion
* Allow thread number settable by command line
* Write in many WARC files at same time for efficiency

## Contact
Name: Augusto Maillo Q. de Figueiredo
Email: augusto.maillo@gmail.com
