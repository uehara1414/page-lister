from queue import PriorityQueue
from urllib.parse import urljoin

import requests

from .exceptions import NotHtmlError
from .crawl_unit import CrawlUnit


class ExtremeCrawler:
    """クローリング全体を司るクラスです。

    コンストラクタで初期設定を行い、crawl() で実際のクローリングを行います。結果はcrawl()
    自体がジェネレータとなっているので、検証された結果が逐次返されるほか、
    crawl()終了後に get_links(content_filter=["imgage", "html", "css"]) といった形で

    """

    def __init__(self, domain: str, index: str='/', max_depth: int=1024):
        """

        :param domain: 探索を行うドメイン名。このドメイン以下のコンテンツのみを収集します。
        :param index: 探索を行う開始地点のパス
        :param max_depth: 探索を行う最大の深さ
        """
        self.domain = domain
        self.max_depth = max_depth

        self.crawl_queue = PriorityQueue()
        self.crawled_url_set = set()
        self.none_html_url_set = set()

        if not index.startswith('http'):
            self.index = urljoin(domain, index)
        else:
            self.index = index

    def crawl(self, content_filter=None):

        if content_filter is None:
            content_filter = ['text/html']
        elif not isinstance(content_filter, str):
            content_filter = [content_filter]

        self.crawl_queue.put(CrawlUnit(self.domain, self.index, 0))
        while not self.crawl_queue.empty():
            crawl_unit = self.crawl_queue.get_nowait()

            if self._is_already_crawled(crawl_unit.url):
                continue

            if crawl_unit.depth == self.max_depth:
                self.crawled_url_set.add(crawl_unit.url)
                yield crawl_unit.url
                continue

            try:
                crawl_unit.crawl()
            except (requests.ConnectionError, TimeoutError):
                print('Connection error has occurred. Retry to access {} later.'.format(crawl_unit.url))
                self.crawl_queue.put(CrawlUnit(self.domain, crawl_unit.url, crawl_unit.depth))

            self.crawled_url_set.add(crawl_unit.url)

            for url in self._filter_crawled_urls(crawl_unit.get_link_set()):
                self.crawl_queue.put(CrawlUnit(self.domain, url, crawl_unit.depth+1))

            for content_type in crawl_unit.content_type:
                if content_type in content_filter:
                    if crawl_unit.get_url_if_valid():
                        yield crawl_unit.get_url_if_valid()

    def _is_already_crawled(self, url):
        return url in self.crawled_url_set

    def _filter_crawled_urls(self, url_set: set):
        return filter(lambda x: x in self.crawled_url_set, url_set)
