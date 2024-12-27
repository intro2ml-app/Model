from sentence_transformers import SentenceTransformer
import psycopg2
from psycopg2 import sql
from psycopg2 import pool
import os
from dotenv import load_dotenv
import logging
from time import time

load_dotenv()

class Retriever:
    def __init__(self, model_name, conn_string, collection_name):
        """Initializes the retriever with embedding model, connection string, and table name."""
        self.model_name = model_name
        self.conn_string = conn_string
        self.collection_name = collection_name
        self.model = self.__load_embedding_model(model_name)
        self.conn_pool = self.__get_db_connection_pool()  # Use connection pool
        self.logger = self.__setup_logger()
    
    def __load_embedding_model(self, model_name):
        """Loads the SentenceTransformer embedding model."""
        return SentenceTransformer(model_name)
    
    def __get_db_connection_pool(self):
        """Establishes a connection pool to PostgreSQL."""
        try:
            return psycopg2.pool.SimpleConnectionPool(1, 20, self.conn_string)  # Pool with 1-20 connections
        except Exception as e:
            self.logger.error(f"Error creating connection pool: {e}")
            raise
    
    def __setup_logger(self):
        """Sets up the logger for error handling and tracking."""
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger

    def query_similar_texts(self, query_text, top_n=5):
        """
        Retrieves the most similar text chunks based on cosine similarity.
        """
        start_time = time()
        query_embedding = self.model.encode([query_text])[0]
        query_embedding_vector = f'[{",".join(map(str, query_embedding))}]'

        try:
            # Use connection pool for a more efficient DB interaction
            conn = self.conn_pool.getconn()
            with conn.cursor() as cur:
                cur.execute(sql.SQL("""
                    SELECT id, text_chunk, embedding <=> %s::vector AS similarity
                    FROM {table_name}
                    ORDER BY similarity ASC
                    LIMIT %s;
                """).format(table_name=sql.Identifier(self.collection_name)),
                (query_embedding_vector, top_n))

                results = cur.fetchmany(top_n)  # Fetch only top_n results to minimize memory use
                self.conn_pool.putconn(conn)  # Return connection to pool

            if not results:
                self.logger.info("No similar results found.")
                return []
            
            results = [{"id": row[0], "text_chunk": row[1], "similarity": row[2]} for row in results]
            self.logger.info(f"Query completed in {time() - start_time:.2f} seconds.")
            return sorted(results, key=lambda x: x['similarity'])

        except Exception as e:
            self.logger.error(f"Error querying the database: {e}")
            return []

    def close_connection(self):
        """Closes the connection pool."""
        self.conn_pool.closeall()

if __name__ == "__main__":
    # Load environment variables
    embedding_model_name = os.getenv('EMBEDDING_MODEL')
    connection_string = os.getenv('CONNECTION_STRING')
    
    # Initialize retriever
    retriever = Retriever(embedding_model_name, connection_string, "text_embeddings")

    # Query similar texts
    query_text = " Giải cá nhân Giải Nhất thủ khoa trong kì thi sinh viên Olympic sinh học 2024"
    results = retriever.query_similar_texts(query_text, top_n=5)

    # Print sorted results by similarity
    for result in results:
        print(f"ID: {result['id']}, Text: {result['text_chunk']}, Similarity: {result['similarity']}")

    # Close connection
    retriever.close_connection()
