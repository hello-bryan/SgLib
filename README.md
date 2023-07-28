# SgLib

## install
`pip install git+https://github.com/hello-bryan/SgLib.git`

## usages
```python
from typing import List
from selenium.webdriver.remote.webelement import WebElement

from seunggeun.sg_crawl import SgCrawler

sg_crawler = SgCrawler('', True)
sg_crawler.get(url='https://www.naver.com')
divs: List[WebElement] = sg_crawler.find_elements_by_selector('div')

for div in divs:
    print(div.text)
```
