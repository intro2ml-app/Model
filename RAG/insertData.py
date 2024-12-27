from TextSplitter import TextSplitter
import os
from dotenv import load_dotenv
from Embedding import EmbeddingDatabase

load_dotenv()

class EmbeddingData:
    def __init__(self, embedding_model_name, connection_string):
        self.embedding_db = EmbeddingDatabase(embedding_model_name, connection_string, "text_embeddings")

    def close_connection(self):
        self.embedding_db.close_connection()

# inherit class
class EmbeddingTextFile(EmbeddingData):
    def __init__(self, embedding_model_name, connection_string, file_path):
        super().__init__(embedding_model_name, connection_string)
        self.file_path = file_path

    def process_text_file(self, file_path):
        """Reads text from a file and stores embeddings in the database."""
        with open(self.file_path, "r") as file:
            text = file.read()

            title = os.path.basename(file_path)
            # url is first line
            source = text.strip('\n')[0]
            data = text.strip('\n')[1]
            text_chunks = TextSplitter.split_text(data)
            embeddings = self.embedding_db.model.encode(text_chunks)
            self.embedding_db.store_embeddings(text_chunks, embeddings, source=source, title=title, source_date=None)

    def remove_text_file(self, file_path):
        """Deletes the text file from the system."""
        
if __name__ == "__main__":
    # Load environment variables
    embedding_model_name = os.getenv('EMBEDDING_MODEL')
    connection_string = os.getenv('CONNECTION_STRING')

    # Initialize components
    


    # Close connection
    # embedding_db.close_connection()
