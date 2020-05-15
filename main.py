import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings


def main():
    #target_board = ['Gossiping', 'Stock']
    target_item = ['hottest']
    process = CrawlerProcess(get_project_settings())
    for board in target_item:
        process.crawl('swg_Crawler_paral_item', item=item)
        process.start()

if __name__ == '__main__':
    main()
