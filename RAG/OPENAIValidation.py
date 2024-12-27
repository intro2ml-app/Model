import os
from OPENAIRetriever import Retriever

if __name__ == "__main__":
    # Load environment variables
    connection_string = os.getenv('CONNECTION_STRING')
    
    # Initialize components
    retriever = Retriever(connection_string, "text_embeddings")
    
    # Query similar texts
    query_text = "Trưởng Bộ môn Khoa học máy tính là ai?"
    results = retriever.query_similar_texts(query_text, top_n=5)
    results.sort(key=lambda x: x['similarity'], reverse=True)
    print(results)
    print("\n-----------------------------\n")
    for i in range(3):
        print(f"ID: {results[i]['id']}, Similarity: {results[i]['similarity']}")
        print(f"Text: {results[i]['text_chunk']}")
        print("\n")
    
    
    print("\n-----------------------------\n")
    title = results[0]['title']
    a = retriever.get_text_chunks_by_title(title=title)
    print(a)
    
    # Close connection
    retriever.close_connection()