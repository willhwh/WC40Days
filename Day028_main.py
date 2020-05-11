import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings


def main():
    target_urls = [
        'https://www.ptt.cc/bbs/AnimalForest/M.1588918852.A.3B1.html',
        'https://www.ptt.cc/bbs/AnimalForest/M.1589206513.A.E70.html',
        'https://www.ptt.cc/bbs/AnimalForest/M.1589204339.A.F5A.html'
    ]
    process = CrawlerProcess(get_project_settings())
    process.crawl('d27_Crawler', start_urls=target_urls, filename='d28.json')
    process.start()

if __name__ == '__main__':
    main()
