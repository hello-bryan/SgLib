import os
import time
import random
from typing import List
import platform
import urllib.request
import zipfile

import requests
import selenium.webdriver.common.keys
from selenium import webdriver
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.action_chains import ActionChains

from bs4 import BeautifulSoup

DRIVER_DEFAULT_PATH = 'driver'
CHROME_DRIVER_DOWNLOAD_PAGE = 'https://chromedriver.chromium.org/downloads'


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


class SgCrawler:
    def __init__(self, chrome_driver_path='', visible=False, init_url='https://google.com'):
        self.Keys = selenium.webdriver.common.keys.Keys
        driver_path_list = []
        if chrome_driver_path == '':
            driver_path_list = self.prepare_chrome_driver()
        else:
            driver_path_list.append(chrome_driver_path)

        options = webdriver.ChromeOptions()
        if visible is False:
            options.add_argument('headless')
        options.add_argument("--log-level=3")
        for driver_path in driver_path_list:
            try:
                service = Service(executable_path=driver_path)
                self.driver = webdriver.Chrome(service=service, options=options)
                self.driver.get(init_url)
                break
            except Exception as e:
                print(e)

    def __del__(self):
        self.driver.quit()

    def prepare_chrome_driver(self):
        driver_path_list = []
        page = requests.get(CHROME_DRIVER_DOWNLOAD_PAGE)
        soup = BeautifulSoup(page.content, 'html.parser')
        version_link_list = []
        for a in soup.select("a"):
            span = a.find('span')
            if span:
                if a.attrs['href'].find('https://chromedriver.storage.googleapis.com/index.html') > -1:
                    version_link_list.append(a.text.split(' ')[1])
                    if len(version_link_list) > 2:
                        # 상위 3개 버전만 다운로드
                        break

        for version in version_link_list:
            dir = os.path.join(DRIVER_DEFAULT_PATH, version)
            os.makedirs(dir, exist_ok=True)
            target_name = self.get_file_name_by_system()
            zip_file_url = f"https://chromedriver.storage.googleapis.com/{version}/{target_name}"
            zip_file_path = os.path.join(dir, target_name)
            exe_path = os.path.join(dir, 'chromedriver.exe')
            if not os.path.exists(exe_path):
                urllib.request.urlretrieve(zip_file_url, zip_file_path)
                with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
                    zip_ref.extractall(dir)
                    driver_path_list.append(os.path.join(dir, 'chromedriver.exe'))
            else:
                driver_path_list.append(exe_path)
        return driver_path_list

    def sleep(self, min_sec: int, max_sec: int):
        sleep_time = random.randrange(min_sec, max_sec)
        time.sleep(sleep_time)

    @staticmethod
    def get_file_name_by_system():
        if platform.system() == 'Windows':
            return 'chromedriver_win32.zip'
        elif platform.system() == 'Darwin':
            if platform.machine().startswith('arm64'):
                return 'chromedriver_mac_arm64.zip'
            else:
                return 'chromedriver_mac64.zip'
        else:
            raise Exception('지원되지 않는 OS입니다. 필요한 경우 소스를 수정하십시오.\n현재 지원중인 os : Windows, Mac')

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
