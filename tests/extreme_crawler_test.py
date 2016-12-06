import unittest
import requests
from extremecrawler import ExtremeCrawler
from nose.plugins.attrib import attr


class ExtremeCrawlerTest(unittest.TestCase):

    def test_constructor(self):
        self.assertTrue(isinstance(ExtremeCrawler("http://www.google.co.jp/"), ExtremeCrawler))

    def test_constructor2(self):
        self.assertTrue(isinstance(ExtremeCrawler("http://www.google.co.jp/", index="/"), ExtremeCrawler))

    def test_constructor3(self):
        self.assertTrue(ExtremeCrawler("http://www.google.co.jp/", index="/", max_depth=1), ExtremeCrawler)

    @attr('slow')
    def test_crawl(self):
        crawler = ExtremeCrawler("http://www.google.co.jp/", index="/", max_depth=1)
        self.assertTrue(isinstance(crawler, ExtremeCrawler))
        crawler.crawl()

    @attr('slow')
    def test_links_are_unique(self):
        crawler = ExtremeCrawler("http://www.google.co.jp/", index="/", max_depth=1)
        links = list(crawler.crawl())
        self.assertEqual(len(links), len(set(links)))

    @attr('slow')
    def test_crawl_with_content_filter(self):
        crawler = ExtremeCrawler("http://socket.io/docs/", index="/", max_depth=1)
        urls = list(crawler.crawl(content_filter="text/html"))
        for url in urls:
            res = requests.head(url)
            self.assertTrue("text/html" in res.headers["Content-Type"])

    @attr('slow')
    def test_crawl_with_multi_content_filter(self):
        crawler = ExtremeCrawler("http://electron.atom.io/", index="/", max_depth=1)
        urls = list(crawler.crawl(content_filter=["image", "text/html"]))
        for url in urls:
            res = requests.head(url)
            self.assertTrue("text/html" in res.headers["Content-Type"] or "image" in res.headers["Content-Type"])

    @attr('slow')
    def test_is_already_crawled(self):
        crawler = ExtremeCrawler("http://socket.io/docs/", index="/", max_depth=1)
        urls = list(crawler.crawl())
        for url in urls:
            self.assertTrue(crawler._is_already_crawled(url))

    def test_filter_crawled_urls(self):
        crawler = ExtremeCrawler("http://www.google.co.jp/", index="/", max_depth=1)
        crawler.crawl()
        crawler.crawled_url_set = {"http://www.google.co.jp/"}
        filtered = set(crawler._filter_crawled_urls({"http://www.google.co.jp/", "https://github.com/"}))
        self.assertEqual(filtered, {"https://github.com/"})

    def test_return_only_images_if_image_filter_option_is_given(self):
        crawler = ExtremeCrawler("http://www.google.co.jp/", index="/", max_depth=1)
        for url in crawler.crawl(content_filter=['image']):
            self.assertTrue('image' in requests.head(url).headers['Content-Type'])
