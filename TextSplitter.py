from langchain.text_splitter import RecursiveCharacterTextSplitter
from WebParser import WebParser

class TextSplitter:
    def __init__(self, chunk_size=1000, chunk_overlap=300):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len
        )

    def get_text_chunks(self, text):
        """Splits text into manageable chunks."""
        return self.text_splitter.split_text(text)

if __name__ == "__main__":
    url = 'https://hcmus.edu.vn/thong-bao-chuong-trinh-talkshow-ky-nang-ung-dung-ai-trong-hoc-tap-hieu-qua/'
    webparser = WebParser()
    data = webparser.parse_webpage(url)

    text_splitter = TextSplitter()
    chunks = text_splitter.get_text_chunks(data['content'])
    
    print(chunks)
    print(f"Number of chunks: {len(chunks)}")
