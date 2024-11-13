# To run, use the command below:
# uvicorn chatbot_api:app --reload

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from Retriever import Retriever
from RetrievalGrader import RetrievalGrader
from openai import OpenAI
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Initialize FastAPI app
app = FastAPI()

# Pydantic model to define the request body structure
class UserQuery(BaseModel):
    query: str

# Fetch environment variables
embedding_model_name = os.getenv('EMBEDDING_MODEL')
connection_string = os.getenv('CONNECTION_STRING')
groq_api_key = os.getenv('GROQ_API_KEY')

# Initialize OpenAI client
llmsModel = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=groq_api_key,
)

retrieval_grader = RetrievalGrader()

# Template for system behavior
template_query = """
    Bạn là một trợ lý hữu ích đang giúp tôi trả lời các câu hỏi và yêu cầu cho người dùng.
    Hãy đưa ra câu trả lời với độ dài vừa phải — không quá ngắn, không quá dài — và điều chỉnh theo từng câu hỏi.
    Cố gắng trả lời trực tiếp nếu có thể.
    Nếu bạn không biết câu trả lời, hãy sử dụng các công cụ có sẵn để hỗ trợ người dùng. Nếu các công cụ không thể giúp, bạn có thể đơn giản trả lời, "Tôi không biết."
"""
message_history = [{"role": "system", "content": template_query}]

# API endpoint to handle user queries
@app.post("/query")
async def get_response(user_query: UserQuery):
    # Extract the query from the request
    user_query_text = user_query.query

    if user_query_text.lower() == "exit":
        return {"message": "Exiting chatbot..."}  # Handle exit scenario

    # Create the retriever object
    retriever = Retriever(embedding_model_name, connection_string, "text_embeddings")
    
    # Query similar texts using the retriever
    results = retriever.query_similar_texts(user_query_text, top_n=5)
    
    # Grade the results to check for relevance
    score = retrieval_grader.grade_document(results, question=user_query_text)

    # If relevant documents are found, format the prompt
    if score == "yes":
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
        message_history.append({"role": "user", "content": prompt})
    else:
        # If no relevant documents are found, use the direct query
        message_history.append({"role": "user", "content": user_query_text})

    # Generate response from the language model
    response = llmsModel.chat.completions.create(
        model="llama3-70b-8192",
        messages=message_history,
        stream=True,
    )

    # Gather full response from the model
    full_response = ""
    for chunk in response:
        content = getattr(chunk.choices[0].delta, "content", None)
        if content is not None:
            full_response += content

    # Add assistant's response to message history
    message_history.append({"role": "assistant", "content": full_response})

    print(message_history)

    # Return the full response to the user
    return {"response": full_response}

