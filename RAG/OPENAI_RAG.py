from pydantic import BaseModel
import os
from RAG.OPENAIRetriever import Retriever
from LLMBaseModel import LLMBaseModel

# Fetch environment variables
embedding_model_name = os.getenv('EMBEDDING_MODEL')
connection_string = os.getenv('CONNECTION_STRING')
openai_api_key = os.getenv('OPENAI_API_KEY')

# Pydantic model to define the request body structure
class UserQuery(BaseModel):
    query: str

class RAGModel(LLMBaseModel):
    def __init__(self, api_key):
        super().__init__(
            api_key=api_key
        )
        self.template_query = """
            Bạn là một trợ lý hữu ích đang giúp tôi trả lời các câu hỏi và yêu cầu cho người dùng.
            Hãy đưa ra câu trả lời với độ dài vừa phải — không quá ngắn, không quá dài — và điều chỉnh theo từng câu hỏi.
            Cố gắng tự trả lời trực tiếp nếu có thể. Chỉ đưa ra câu trả lời liên quan và chính xác.
            Nếu bạn không biết câu trả lời, hãy trả lời "Tôi không biết."
        """
        self.message_history = [{"role": "system", "content": self.template_query}]
        self.retriever = Retriever(connection_string, "text_embeddings")


    def retrieve_top_document(self, user_query_text, top_n=5, top_k=5):
        top_documents = []
        results = self.retriever.query_similar_texts(user_query_text, top_n=top_n)
        results.sort(key=lambda x: x['similarity'], reverse=True)
        top_title = []
        for result in results:
            if result['title'] not in top_title:
                top_title.append((result['title'], 0))
            else:
                for i in range(len(top_title)):
                    if top_title[i][0] == result['title']:
                        top_title[i] = (result['title'], top_title[i][1] + 1)
        top_title.sort(key=lambda x: x[1], reverse=True)
        top_title = [title[0] for title in top_title]
        top_title = list(dict.fromkeys(top_title))
        
        print(f"Top title!!!")
        for title in top_title:
            print(f"Title: {title}")
            document = self.retriever.get_text_chunks_by_title(title=title)
            top_documents.append(document)
            
        return top_documents[:min(top_k+1, len(top_documents))]


    def create_prompt(self, results, user_query_text):
        template_query_retrieval = """
            Hãy tham khảo vào thông tin sau để trả lời câu hỏi của người dùng nếu nội dung liên quan:
            {document}
            Câu hỏi của người dùng: {question}
        """
        document=""
        for i in range(len(results)):
            result = results[i]
            document += f"{i + 1}) {result}\n\n"
            
        prompt = template_query_retrieval.format(
            document=document,
            question=user_query_text
        )
        return prompt

    # def generate_response(self, message_history):
    #     response = self.llmsModel.chat.completions.create(
    #         model="gpt-4o-mini",
    #         messages=message_history,
    #         # stream=True
    #     )
    #     # full_response = ""
    #     # for chunk in response:
    #     #     content = getattr(chunk.choices[0].delta, "content", None)
    #     #     if content is not None:
    #     #         full_response += content
    #     full_response = response.choices[0].message.content
    #     return full_response
    
    def get_completion(self, messages, model="gpt-4o-mini", temperature=None, top_p=None, max_tokens=None, stream=False):
        user_query_text = messages[-1]['content']
        results = self.retrieve_top_document(user_query_text, top_n=3, top_k = 1)
        prompt = self.create_prompt(results, messages)
        self.message_history.append({"role": "user", "content": prompt})
        respone = self.llmsModel.chat.completions.create(
            model="gpt-4o-mini",
            messages=self.message_history,
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_tokens,
            stream=stream
        )
        return respone


# API endpoint to handle user queries
# def get_response(rag_model, user_query: UserQuery):
#     user_query_text = user_query.query

#     if user_query_text.lower() == "exit":
#         return {"message": "Exiting chatbot..."}

#     results = rag_model.retrieve_top_document(user_query_text, top_n=3, top_k = 1)
#     prompt = rag_model.create_prompt(results, user_query_text)
#     rag_model.message_history.append({"role": "user", "content": prompt})
#     full_response = rag_model.generate_response(rag_model.message_history)
#     rag_model.message_history.append({"role": "assistant", "content": full_response})
#     return {"response": full_response}

# if __name__ == "__main__":
#     rag_model = RAGModel()
#     user_query = UserQuery(query="Trong Cuộc thi học thuật thách thức vào năm 2024, ai là người vô địch?")
#     response = get_response(rag_model, user_query)
#     print(rag_model.message_history)    