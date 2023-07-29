import os
import platform
import urllib.request
import zipfile

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service

from ._inner.base_crawler import BaseCrawler

import ssl
ssl._create_default_https_context = ssl._create_unverified_context

DRIVER_DEFAULT_PATH = 'driver'
CHROME_DRIVER_DOWNLOAD_PAGE = 'https://chromedriver.chromium.org/downloads'


class SgChromeCrawler(BaseCrawler):
    def __init__(self, chrome_driver_path='', visible=False, init_url='https://google.com'):
        self.chrome_driver_path = chrome_driver_path
        self.visible = visible
        self.init_url = init_url
        super().__init__()

    def load_driver(self):
        driver_path_list = []
        if self.chrome_driver_path == '':
            driver_path_list = self.__prepare_chrome_driver()
        else:
            driver_path_list.append(self.chrome_driver_path)

        options = webdriver.ChromeOptions()
        if self.visible is False:
            options.add_argument('headless')
        options.add_argument("--log-level=3")
        for driver_path in driver_path_list:
            try:
                service = Service(executable_path=driver_path)
                self.driver = webdriver.Chrome(service=service, options=options)
                self.driver.get(self.init_url)
                break
            except Exception as e:
                print(e)

    def __prepare_chrome_driver(self):
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
            target_name = self.__get_file_name_by_system()
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

    @staticmethod
    def __get_file_name_by_system():
        if platform.system() == 'Windows':
            return 'chromedriver_win32.zip'
        elif platform.system() == 'Darwin':
            if platform.machine().startswith('arm64'):
                return 'chromedriver_mac_arm64.zip'
            else:
                return 'chromedriver_mac64.zip'
        else:
            raise Exception('지원되지 않는 OS입니다. 필요한 경우 소스를 수정하십시오.\n현재 지원중인 os : Windows, Mac')
