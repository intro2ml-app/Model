from sentence_transformers import SentenceTransformer
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
import os

load_dotenv()

class EmbeddingDatabase:
    def __init__(self, model_name, conn_string, collection_name):
        self.model_name = model_name
        self.conn_string = conn_string
        self.collection_name = collection_name
        self.model = self.__load_embedding_model(model_name)
        self.conn, self.cur = self.__get_db_connection()
    
    def __load_embedding_model(self, model_name):
        """Loads the SentenceTransformer embedding model."""
        return SentenceTransformer(model_name)

    def __get_db_connection(self):
        """Establishes a connection to PostgreSQL and returns the connection and cursor."""
        conn = psycopg2.connect(self.conn_string)
        cur = conn.cursor()
        return conn, cur

    def encode_text(self, text):
        """Encodes text into embeddings using the SentenceTransformer model."""
        return self.model.encode(text)

    def create_embeddings_table(self):
        """Creates a table to store text chunks and their embeddings."""
        self.cur.execute(f"""
            CREATE TABLE IF NOT EXISTS {self.collection_name} (
                id SERIAL PRIMARY KEY,
                source TEXT,
                title TEXT,
                text_chunk TEXT,
                embedding VECTOR(768),  -- Adjust dimension based on model
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
        values = [(source, title, chunk, embedding.tolist(), parsed_date) 
                 for chunk, embedding in zip(text_chunks, embeddings)]
        insert_query = f"""
            INSERT INTO {self.collection_name} (source, title, text_chunk, embedding, source_date) 
            VALUES %s;
        """
        execute_values(self.cur, insert_query, values)
        self.conn.commit()

    def query_similar_texts(self, query_text, top_n=5):
        """Retrieves the most similar text chunks based on cosine similarity."""
        query_embedding = self.model.encode([query_text])[0]
        query_embedding_vector = f'[{",".join(map(str, query_embedding))}]'

        self.cur.execute(f"""
            SELECT id, text_chunk, embedding <=> %s::vector AS similarity
            FROM {self.collection_name}
            ORDER BY similarity ASC
            LIMIT %s;
        """, (query_embedding_vector, top_n))
        
        results = self.cur.fetchall()
        return [{"id": row[0], "text_chunk": row[1], "similarity": row[2]} for row in results]

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

    def table_exists(self, table_name=None):
        """
        Checks if a table exists in the database.
        
        Args:
            table_name (str): Name of the table to check. Defaults to the collection_name attribute.
            
        Returns:
            bool: True if the table exists, False otherwise.
        """
        table_name = table_name or self.collection_name
        self.cur.execute("""
            SELECT EXISTS (
                SELECT 1 
                FROM information_schema.tables 
                WHERE table_name = %s
            );
        """, (table_name,))
        return self.cur.fetchone()[0]

    def blog_exists(self, title):
        """
        Checks if a blog with the given title exists in the collection.

        Args:
            title (str): The title of the blog to check.

        Returns:
            bool: True if the blog exists, False otherwise.
        """
        self.cur.execute(f"""
            SELECT EXISTS (
                SELECT 1 
                FROM {self.collection_name}
                WHERE title = %s
            );
        """, (title,))
        return self.cur.fetchone()[0]

    def delete_blog(self, title):
        """
        Deletes a blog with the given title from the collection.

        Args:
            title (str): The title of the blog to delete.

        Returns:
            str: Success message if the blog is deleted, or an error message if not found.
        """
        if self.blog_exists(title):
            self.cur.execute(f"""
                DELETE FROM {self.collection_name}
                WHERE title = %s;
            """, (title,))
            self.conn.commit()
            return f"Blog with title '{title}' has been successfully deleted."
        else:
            return f"Blog with title '{title}' does not exist."

if __name__ == "__main__":
    # Load environment variables
    embedding_model_name = os.getenv('EMBEDDING_MODEL')
    connection_string = os.getenv('CONNECTION_STRING')
    
    # Initialize components
    webparser = WebParser()
    textsplitter = TextSplitter()
    embedding_db = EmbeddingDatabase(embedding_model_name, connection_string, "text_embeddings")
    
    # Optional: Reset the table
    embedding_db.delete_embeddings_table()
    embedding_db.create_embeddings_table()

    # crawler = HCMUSLinkCrawler()
    # news_links = crawler.crawl(10)

    # if news_links != []:
    #     with open('links.txt', 'r') as file:
    #         text = file.read()
    #         parsed_links = text.split('\n')

    #     for url in news_links:
    #         if url in parsed_links:
    #             continue
    #         else:
    #             print(f"Adding URL: {url}")
    #             parsed_links.append(url)

    #     with open('links.txt', 'w') as file:
    #         file.write('\n'.join(parsed_links))
    
    # for url in parsed_links:
    #     print(f"Processing URL: {url}")
    #     page_content = webparser.parse_webpage(url)
    #     print(f"Parsing content: {page_content.get('title')}")
    #     text_chunks = textsplitter.get_text_chunks(page_content['content'])

    #     embeddings_text = embedding_db.model.encode(text_chunks)
    #     embedding_db.store_embeddings(text_chunks, embeddings_text, 
    #                                 source=url, title=page_content.get('title', ''),
    #                                 source_date=page_content.get('date'))
    #     print("\n")
    

    folder_path = "../Data"
    # Embedding all txt files in the folder
    txt_files = find_txt_files(folder_path)
    for file_path in txt_files:
        print(f"Processing file: {file_path}")
        with open(file_path, "r", encoding="utf-8") as file:
            text = file.read()
            text_chunks = textsplitter.get_text_chunks(text)
            embeddings_text = embedding_db.model.encode(text_chunks)
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
            embeddings_text = embedding_db.model.encode(text_chunks)
            embedding_db.store_embeddings(text_chunks, embeddings_text, source=file, title="Đề cương tóm tắt của môn " + data["course_name"], source_date=None)
        print("\n")

    # Close connection
    embedding_db.close_connection()
