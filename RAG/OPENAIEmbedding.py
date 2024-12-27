import psycopg2
from psycopg2.extras import execute_values
from TextSplitter import TextSplitter
from WebParser import WebParser
from datetime import datetime
import os
from dotenv import load_dotenv
from LinkCrawler import HCMUSLinkCrawler
from utils import saveJson, checkJsonExisted, find_txt_files
from links import parsed_links
import json
from openai import OpenAI


class EmbeddingDatabase:
    def __init__(self, conn_string, collection_name):
        self.conn_string = conn_string
        self.collection_name = collection_name
        self.conn, self.cur = self.__get_db_connection()
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def __get_db_connection(self):
        """Establishes a connection to PostgreSQL and returns the connection and cursor."""
        print(f"Connecting to database: {self.conn_string}")
        conn = psycopg2.connect(self.conn_string)
        cur = conn.cursor()
        return conn, cur

    def encode_text(self, texts):
        """Encodes text into embeddings using the OpenAI API."""
        results = []
        try:
            for text in texts:
                response = self.client.embeddings.create(
                    model="text-embedding-3-small",  # Adjust model as needed
                    input=text
                )
                results.append(response.data[0].embedding)
            return results
        except Exception as e:
            print(f"Error during embedding generation: {e}")
            return []

    def create_embeddings_table(self):
        """Creates a table to store text chunks and their embeddings."""
        self.cur.execute(f"""
            CREATE TABLE IF NOT EXISTS {self.collection_name} (
                id SERIAL PRIMARY KEY,
                source TEXT,
                title TEXT,
                text_chunk TEXT,
                embedding VECTOR(1536),  -- OpenAI small model returns 1536 dimensions
                source_date DATE
            );
        """)
        self.conn.commit()

    def delete_embeddings_table(self):
        """Deletes the embeddings table if it exists."""
        self.cur.execute(f"DROP TABLE IF EXISTS {self.collection_name};")
        self.conn.commit()
        print(f"{self.collection_name} table deleted successfully.")

    def store_embeddings(self, text_chunks, embeddings, source="", title="", source_date=None):
        """Stores embeddings in the database using batch insert."""
        parsed_date = self.__parse_date(source_date)
        values = [(source, title, chunk, embedding, parsed_date) 
                 for chunk, embedding in zip(text_chunks, embeddings)]
        insert_query = f"""
            INSERT INTO {self.collection_name} (source, title, text_chunk, embedding, source_date) 
            VALUES %s;
        """
        execute_values(self.cur, insert_query, values)
        self.conn.commit()
        
        # json_data = [
        #     {
        #         "source": source,
        #         "title": title,
        #         "text_chunk": chunk,
        #         "embedding": embedding,
        #         "source_date": parsed_date
        #     }
        #     for chunk, embedding in zip(text_chunks, embeddings)
        # ]
        # json_file = "vectordb.json"
        # try:
        #     if os.path.exists(json_file):
        #         with open(json_file, "r", encoding="utf-8") as file:
        #             existing_data = json.load(file)
        #         existing_data.extend(json_data)
        #     else:
        #         existing_data = json_data

        #     with open(json_file, "w", encoding="utf-8") as file:
        #         json.dump(existing_data, file, ensure_ascii=False, indent=4)
        # except Exception as e:
        #     print(f"Error writing to JSON file: {e}")

    def __parse_date(self, date_str):
        """Parses date string into the format required for storage."""
        if date_str:
            try:
                return datetime.strptime(date_str, '%d/%m/%Y').strftime('%Y-%m-%d')
            except ValueError:
                pass
        return None

    def close_connection(self):
        """Closes the database connection."""
        if self.cur:
            self.cur.close()
        if self.conn:
            self.conn.close()
            

if __name__ == "__main__":
    # Load environment variables
    load_dotenv()
    connection_string = os.getenv('CONNECTION_STRING_2')
    print(f"Connection string: {connection_string}")
    # Initialize components
    webparser = WebParser()
    textsplitter = TextSplitter(chunk_size=500)
    embedding_db = EmbeddingDatabase(connection_string, "text_embeddings")
    
    # Optional: Reset the table
    embedding_db.delete_embeddings_table()
    embedding_db.create_embeddings_table()

    # crawler = HCMUSLinkCrawler()
    # news_links = crawler.crawl(2)
    news_links = []

    # if news_links != []:
    with open('links.txt', 'r') as file:
        text = file.read()
        parsed_links = text.split('\n')

    for url in news_links:
        if url in parsed_links:
            continue
        else:
            print(f"Adding URL: {url}")
            parsed_links.append(url)

    with open('links.txt', 'w') as file:
        file.write('\n'.join(parsed_links))
    
    for url in parsed_links:
        print(f"Processing URL: {url}")
        page_content = webparser.parse_webpage(url)
        print(f"Parsing content: {page_content.get('title')}")
        text_chunks = textsplitter.get_text_chunks(page_content['content'])

        embeddings_text = embedding_db.encode_text(text_chunks)
        embedding_db.store_embeddings(text_chunks, embeddings_text, 
                                    source=url, title=page_content.get('title', ''),
                                    source_date=page_content.get('date'))
        print("\n")
    

    folder_path = "../Data"
    # Embedding all txt files in the folder
    txt_files = find_txt_files(folder_path)
    for file_path in txt_files:
        print(f"Processing file: {file_path}")
        with open(file_path, "r", encoding="utf-8") as file:
            text = file.read()
            text_chunks = textsplitter.get_text_chunks(text)
            embeddings_text = embedding_db.encode_text(text_chunks)
            embedding_db.store_embeddings(text_chunks, embeddings_text, source=file_path, title=os.path.basename(file_path))
        print("\n")

    # Embedding all json files in the folder
    folder = "../Data/Decuongmonhoc"
    json_files = [f for f in os.listdir(folder) if f.endswith('.json')]
    for file in json_files:
        print(f"Processing file: {file}")
        with open(os.path.join(folder, file), 'r', encoding="utf-8") as f:
            data = json.load(f)
            text_chunks = textsplitter.get_text_chunks(data['content'])
            embeddings_text = embedding_db.encode_text(text_chunks)
            embedding_db.store_embeddings(text_chunks, embeddings_text, source=file, title="\u0110ề c\u01b0\u01a1ng t\u00f3m t\u1eaft c\u1ee7a m\u00f4n " + data["course_name"], source_date=None)
        print("\n")

    # Close connection
    embedding_db.close_connection()
