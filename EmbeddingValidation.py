import os
from Embedding import EmbeddingDatabase

if __name__ == "__main__":
    # Load environment variables
    embedding_model_name = os.getenv('EMBEDDING_MODEL')
    connection_string = os.getenv('CONNECTION_STRING')
    
    # Initialize components
    embedding_db = EmbeddingDatabase(embedding_model_name, connection_string, "text_embeddings")

    # Query similar texts
    query_text = "Trưởng Bộ môn Khoa học máy tính là ai?"
    results = embedding_db.query_similar_texts(query_text, top_n=5)
    results.sort(key=lambda x: x['similarity'], reverse=True)
    for i in range(3):
        print(f"ID: {results[i]['id']}, Similarity: {results[i]['similarity']}")
        print(f"Text: {results[i]['text_chunk']}")
        print("\n")
    
    # Close connection
    embedding_db.close_connection()