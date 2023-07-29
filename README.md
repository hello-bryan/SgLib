# SgLib

## install
`pip install git+https://github.com/hello-bryan/SgLib.git`

## uninstall
`pip uninstall sg-lib`


## usages
### chrome driver 로 선언
```python
from seunggeun.chrome_crawler import SgChromeCrawler
sg_crawler = SgChromeCrawler(visible=True)
```
### FireFox driver 로 선언
```python
from seunggeun.firefox_crawler import SgFirefoxCrawler
sg_crawler = SgFirefoxCrawler()
```

### 사용
```python
try:
    sg_crawler.get('https://www.google.com')

    # 검색어 입력
    search_box = sg_crawler.find_element_by_selector('textarea[name="q"]')
    if search_box:
        search_box.send_keys("Hello, Selenium!")

        # Enter 키 입력 (검색 수행)
        search_box.send_keys(sg_crawler.Keys.RETURN)
except Exception as ex:
    print(str(ex))
finally:
    del sg_crawler
```
