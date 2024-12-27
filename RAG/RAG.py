from pydantic import BaseModel
from Retriever import Retriever
from RetrievalGrader import RetrievalGrader
from openai import OpenAI
import os

# Fetch environment variables
embedding_model_name = os.getenv('EMBEDDING_MODEL')
connection_string = os.getenv('CONNECTION_STRING')
groq_api_key = os.getenv('GROQ_API_KEY')

class RAGModel:
    def __init__(self):
        self.llmsModel = OpenAI(
            api_key=groq_api_key,
        )
        self.retrieval_grader = RetrievalGrader()
        self.template_query = """
            Bạn là một trợ lý hữu ích đang giúp tôi trả lời các câu hỏi và yêu cầu cho người dùng.
            Hãy đưa ra câu trả lời với độ dài vừa phải — không quá ngắn, không quá dài — và điều chỉnh theo từng câu hỏi.
            Cố gắng trả lời trực tiếp nếu có thể.
            Nếu bạn không biết câu trả lời, hãy sử dụng các công cụ có sẵn để hỗ trợ người dùng. Nếu các công cụ không thể giúp, bạn có thể đơn giản trả lời, "Tôi không biết."
        """
        self.message_history = [{"role": "system", "content": self.template_query}]


    def retrieve_and_score(self, user_query_text):
        retriever = Retriever(embedding_model_name, connection_string, "text_embeddings")
        results = retriever.query_similar_texts(user_query_text, top_n=5)
        score = self.retrieval_grader.grade_document(results, question=user_query_text)
        return results, score

    def create_prompt(self, results, user_query_text):
        template_query_retrieval = """
            Hãy tham khảo vào thông tin sau để trả lời câu hỏi của người dùng nếu cần thiết:
            1) {document_1}
            2) {document_2}
            3) {document_3}
            Câu hỏi của người dùng: {question}
        """
        prompt = template_query_retrieval.format(
            document_1=results[0]['text_chunk'],
            document_2=results[1]['text_chunk'],
            document_3=results[2]['text_chunk'],
            question=user_query_text
        )
        return prompt

    def generate_response(self, message_history):
        response = self.llmsModel.chat.completions.create(
            model="gpt-4o-mini",
            messages=message_history,
            stream=True,
        )
        full_response = ""
        for chunk in response:
            content = getattr(chunk.choices[0].delta, "content", None)
            if content is not None:
                full_response += content
        return full_response

rag_model = RAGModel()

# Pydantic model to define the request body structure
class UserQuery(BaseModel):
    query: str

# API endpoint to handle user queries
def get_response(user_query: UserQuery):
    user_query_text = user_query.query

    if user_query_text.lower() == "exit":
        return {"message": "Exiting chatbot..."}

    results, score = rag_model.retrieve_and_score(user_query_text)

    if score == "yes":
        prompt = rag_model.create_prompt(results, user_query_text)
        rag_model.message_history.append({"role": "user", "content": prompt})
    else:
        rag_model.message_history.append({"role": "user", "content": user_query_text})

    full_response = rag_model.generate_response(rag_model.message_history)
    rag_model.message_history.append({"role": "assistant", "content": full_response})

    print(rag_model.message_history)

    return {"response": full_response}
