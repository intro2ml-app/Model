from Retriever import Retriever
from RetrievalGrader import RetrievalGrader
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()



if __name__ == "__main__":
    embedding_model_name = os.getenv('EMBEDDING_MODEL') # 768
    connection_string = os.getenv('CONNECTION_STRING')
    groq_api_key = os.getenv('GROQ_API_KEY')

    print("Starting chatbot...")
    llmsModel = OpenAI(
        base_url="https://api.groq.com/openai/v1",
        api_key=groq_api_key,
    )

    retrieval_grader = RetrievalGrader()

    message_history = []

    template_query = """
        Bạn là một trợ lý hữu ích đang giúp tôi trả lời các câu hỏi và yêu cầu cho người dùng.
        Hãy đưa ra câu trả lời với độ dài vừa phải — không quá ngắn, không quá dài — và điều chỉnh theo từng câu hỏi.
        Cố gắng trả lời trực tiếp nếu có thể.
        Nếu bạn không biết câu trả lời, hãy sử dụng các công cụ có sẵn để hỗ trợ người dùng. Nếu các công cụ không thể giúp, bạn có thể đơn giản trả lời, "Tôi không biết."       
        """ 
    message_history.append({"role": "system", "content": template_query})

    while True:
        user_query = input("Enter your query: ")

        if user_query.lower() == "exit":
            print("Exiting chatbot...")
            break

        print("\nAssistant: ", end="", flush=True)
        
        retriever = Retriever(embedding_model_name, connection_string, "text_embeddings")
        # Query similar texts
        results = retriever.query_similar_texts(user_query, top_n=5)
        score = retrieval_grader.grade_document(results, question=user_query)

        if score == "yes":
            print("Relevant documents found.")
            template_query = """
                Hãy tham khảo vào thông tin sau để trả lời câu hỏi của người dùng:
                1) {document_1}
                2) {document_2}
                3) {document_3}
                Câu hỏi của người dùng: {question}
            """
            prompt = template_query.format(
                document_1=results[0]['text_chunk'],
                document_2=results[1]['text_chunk'],
                document_3=results[2]['text_chunk'],
                question=user_query
            )
            message_history.append({"role": "user", "content": prompt})
            response = llmsModel.chat.completions.create(
                model="llama3-70b-8192",
                messages=message_history,
                stream=True,
            )
        else:
            message_history.append({"role": "user", "content": user_query})
            response = llmsModel.chat.completions.create(
                model="llama3-70b-8192",
                messages=message_history,
                stream=True,
            )

        full_response = ""
        for chunk in response:
            content = getattr(chunk.choices[0].delta, "content", None) 
            if content is not None: 
                print(content, end="", flush=True)
                full_response += content
        print('\n')

        message_history.append({"role": "assistant", "content": full_response})