import time
import random
from typing import List

import selenium.webdriver.common.keys
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.action_chains import ActionChains


class Retry(object):
    def __init__(self, wait_sec):
        self.wait_sec = wait_sec

    def __call__(self, func):
        decorator_self = self

        def wrappee(*args, **kwargs):
            cur = 0
            while True:
                try:
                    element = func(*args, **kwargs)
                    if element:
                        return element
                    else:
                        raise Exception('none')
                except Exception as e:
                    if cur >= decorator_self.wait_sec:
                        return None
                    cur += 1
                    time.sleep(1)
        return wrappee


class Sleep(object):
    def __init__(self, min_sec: int, max_sec: int):
        self.min_sec = min_sec
        self.max_sec = max_sec

    def __call__(self, func):
        decorator_self = self
        def wrappee(*args, **kwargs):
            sleep_time = random.randrange(decorator_self.min_sec, decorator_self.max_sec)
            time.sleep(sleep_time)
            return func(*args, **kwargs)
        return wrappee


class BaseCrawler:
    def __init__(self):
        self.Keys = selenium.webdriver.common.keys.Keys
        self.driver: WebDriver = None
        self.load_driver()

    def load_driver(self):
        raise Exception('Not Implement method : def load_driver()')

    def __del__(self):
        self.driver.quit()

    def close(self):
        self.driver.close()

    def sleep(self, min_sec: int, max_sec: int):
        sleep_time = random.randrange(min_sec, max_sec)
        time.sleep(sleep_time)

    def get(self, url):
        self.driver.get(url)

    @Retry(10)
    def find_element_by_selector(self, selector, parent=None) -> WebElement:
        if parent:
            return parent.find_element(by=By.CSS_SELECTOR, value=selector)
        else:
            return self.driver.find_element(by=By.CSS_SELECTOR, value=selector)

    def find_element(self, by: By, value: str, parent=None) -> WebElement:
        try:
            if parent:
                return parent.find_element(by=by, value=value)
            else:
                return self.driver.find_element(by=by, value=value)
        except Exception:
            return None

    @Retry(10)
    def find_elements_by_selector(self, selector, parent=None) -> List[WebElement]:
        if parent:
            return parent.find_elements(by=By.CSS_SELECTOR, value=selector)
        else:
            return self.driver.find_elements(by=By.CSS_SELECTOR, value=selector)

    def exists_elements(self, selector, parent=None):
        el = None
        if parent:
            el = parent.find_elements(by=By.CSS_SELECTOR, value=selector)
        else:
            el = self.driver.find_elements(by=By.CSS_SELECTOR, value=selector)
        return el is not None and len(el) > 0

    def remove_element(self, selector, parent=None):
        elements = self.find_elements_by_selector(selector, parent)
        for i in range(len(elements)):
            self.driver.execute_script("arguments[0].remove()", elements[len(elements)-(i+1)])

    def move_to_element(self, element: WebElement):
        actions = ActionChains(self.driver)
        actions.move_to_element(element).perform()

    @staticmethod
    def try_click(element: WebElement):
        try:
            element.click()
        except StaleElementReferenceException:
            pass
