import psycopg2
from openai import OpenAI
import os

class Retriever:
    def __init__(self, conn_string, collection_name):
        self.conn_string = conn_string
        self.collection_name = collection_name
        self.conn, self.cur = self.__get_db_connection()
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def __get_db_connection(self):
        """Establishes a connection to PostgreSQL and returns the connection and cursor."""
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

    def query_similar_texts(self, query_text, top_n=5):
        """Retrieves the most similar text chunks based on cosine similarity and includes the title."""
        query_embedding = self.encode_text([query_text])[0]
        query_embedding_vector = f'[{",".join(map(str, query_embedding))}]'

        self.cur.execute(f"""
            SELECT id, title, text_chunk, embedding <=> %s::vector AS similarity
            FROM {self.collection_name}
            ORDER BY similarity ASC
            LIMIT %s;
        """, (query_embedding_vector, top_n))

        results = self.cur.fetchall()
        return [{"id": row[0], "title": row[1], "text_chunk": row[2], "similarity": row[3]} for row in results]

    def get_text_chunks_by_title(self, title):
        """Queries all text chunks by title and merges them together, ordered by ID."""
        self.cur.execute(f"""
            SELECT text_chunk
            FROM {self.collection_name}
            WHERE title = %s
            ORDER BY id ASC;
        """, (title,))

        # Fetch all the results (text chunks)
        rows = self.cur.fetchall()

        # Merge the text chunks into a single string
        merged_text = " ".join([row[0] for row in rows])

        return merged_text

    def close_connection(self):
        """Closes the database connection."""
        if self.cur:
            self.cur.close()
        if self.conn:
            self.conn.close()
