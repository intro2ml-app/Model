import requests
from bs4 import BeautifulSoup, Tag
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

class HCMUSLinkCrawler():
    '''
    Crawl Link from HCMUS website
    '''
    def __init__(self) -> None:
        self.BASE_URLS = [
            'https://hcmus.edu.vn/thong-tin-danh-cho-nguoi-hoc/',
            'https://hcmus.edu.vn/nhip-song-sinh-vien/'
        ]
        self.__news_urls = set(self.BASE_URLS)
        self.__session = requests.Session()
        self.__session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.__high_split_index = 72  # Web header
        self.__low_split_index = 34   # Web footer
        self.news_links = set()

    def __crawl_http(self) -> list[requests.Response]:
        def fetch_url(url):
            return self.__session.get(url)
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            return list(executor.map(fetch_url, self.__news_urls))

    def __parse_html(self, responses: list[requests.Response]) -> list[BeautifulSoup]:
        return [
            BeautifulSoup(response.content, 'html.parser')
            for response in responses
        ]

    def __filter_html_tag(self, soups: list[BeautifulSoup]) -> list[list[Tag]]:
        return [
            soup.find_all('a', href=True)
            for soup in soups
        ]

    def __get_date(self, soup: BeautifulSoup) -> str:
        date_tag = soup.find("meta", attrs={"property": "article:published_time"})
        return date_tag["content"] if date_tag else "No date found"

    def __filter_date(self, soup, date: str) -> None:
        # date example: 04/05/2024
        date = datetime.strptime(date, '%d/%m/%Y').replace(tzinfo=None)  # Make it naive
        date_str = self.__get_date(soup)
        if date_str == "No date found":
            return False
        try:
            date_obj = datetime.fromisoformat(date_str).replace(tzinfo=None)  # Make it naive
            return date_obj >= date
        except ValueError:
            return False  # In case the date format is incorrect

    def __filter_news(self, list_of_tags: list[list[Tag]], filter_date = None) -> None:
        group_filters = {'/author', '/category/', '/page/'}
        
        for tags in list_of_tags:
            for tag in tags[self.__high_split_index : len(tags) - self.__low_split_index]:
                href = tag['href']
                if href in ('', '#'):
                    continue

                if '/page/' in href:
                    self.__news_urls.add(href)
                elif not any(filter in href for filter in group_filters):
                    response = self.__session.get(href)
                    soup = BeautifulSoup(response.content, 'html.parser')
                    if filter_date is not None:
                        if self.__filter_date(soup, filter_date):
                            self.news_links.add(href)
                    else:
                        self.news_links.add(href)
    def crawl(self, max_page: int = 25) -> list[str]:
        for _ in range(max_page):
            responses = self.__crawl_http()
            self.__news_urls.clear()
            self.__news_urls.update(self.BASE_URLS)
            
            soups = self.__parse_html(responses)
            list_of_tags = self.__filter_html_tag(soups)
            self.__filter_news(list_of_tags, '01/01/2024')

        return list(self.news_links)

if __name__ == "__main__":
    crawler = HCMUSLinkCrawler()
    news_links = crawler.crawl(5)
    for link in news_links:
        print(link)
