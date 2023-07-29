from selenium import webdriver
from ._inner.base_crawler import BaseCrawler


class SgFirefoxCrawler(BaseCrawler):
    def load_driver(self):
        self.driver = webdriver.Firefox()
