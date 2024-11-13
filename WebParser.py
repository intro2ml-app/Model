from bs4 import BeautifulSoup
import requests

class WebParser:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }

    def __fetch_webpage(self, url: str):
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            return response.content
        else:
            print(f"Failed to retrieve page at {url}, status code: {response.status_code}")
            return None

    def __preprocess_content(self, content: str):
        content = content.replace('\n', ' ')
        content = content.replace('\t', ' ')
        content = content.split('     Post Views')[0]
        return content
    
    def parse_webpage(self, url: str):
        page_content = self.__fetch_webpage(url)
        if not page_content:
            return None

        soup = BeautifulSoup(page_content, 'html.parser')
        
        # Extract content
        content_element = soup.select_one("div.cmsmasters_post_content.entry-content")
        content = content_element.text.strip() if content_element else "Content not found"
        content = self.__preprocess_content(content) if content else "Content not found"

        # Extract date
        date_element = soup.find('abbr', class_='published')
        date = date_element.text.strip() if date_element else "Date not found"

        # Extract title
        title_element = soup.select_one("h2.cmsmasters_post_title.entry-title")
        title = title_element.text.strip() if title_element else "Title not found"

        # Store the result
        result = ({
            'content': content,
            'date': date,
            'source': url,
            'title': title
        })
        return result

if __name__ == "__main__":
    urls = [
        'https://hcmus.edu.vn/thong-bao-chuong-trinh-talkshow-ky-nang-ung-dung-ai-trong-hoc-tap-hieu-qua/',
        'https://hcmus.edu.vn/no-luc-va-dam-me-hanh-trinh-den-thanh-cong-cua-giao-su-nguyen-trong-toan/',
        'https://hcmus.edu.vn/truong-dai-hoc-khoa-hoc-tu-nhien-dhqg-hcm-mo-nganh-moi-tang-chi-tieu-tuyen-sinh/'
    ]
    
    parser = WebParser()
    for url in urls:
        data = parser.parse_webpage(url)
        print(data)
        print()
