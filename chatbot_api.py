# To run, use the command below:
# uvicorn chatbot_api:app --reload

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, field_validator
from LLMs import LLMs
from typing import Optional, Union, List
import os
from fastapi.responses import StreamingResponse

llms = LLMs()

app = FastAPI()

# Define the structure for the messages list
class Message(BaseModel):
    role: str
    content: str

class UserQuery(BaseModel):
    query: Union[str, List[Message]]  # query can be either a string or a list of Message objects
    model: Optional[str] = "gpt-4o-mini"  # Optional, default to "gpt-4o-mini"
    temperature: Optional[float] = None  # Optional, default to None
    top_p: Optional[float] = None        # Optional, default to None
    max_tokens: Optional[int] = None     # Optional, default to None
    stream: Optional[bool] = False       # Optional, default to False

    @field_validator('query')
    def check_query_format(cls, v):
        # If `query` is a string, it will be accepted as is
        if isinstance(v, str):
            return v
        # If `query` is a list, each item must be a dict with 'role' and 'content'
        if isinstance(v, list):
            # Ensure each element in the list has 'role' and 'content' fields
            for item in v:
                if not isinstance(item, dict) or 'role' not in item or 'content' not in item:
                    raise ValueError("Each item in the list must be a dict with 'role' and 'content'.")
            return v
        raise ValueError("Query must be either a string or a list of objects with 'role' and 'content'.")

# Helper function for type conversion and validation
def validate_and_convert(param, default=None, param_type=float):
    if param is None:
        return default
    try:
        # Ensure the conversion is handled properly
        return param_type(param)
    except (ValueError, TypeError):
        raise HTTPException(status_code=400, detail=f"Invalid {param_type.__name__} value: {param}")

# API endpoint to handle user queries
@app.post("/query")
async def get_response(user_query: UserQuery):
    # Extract the query from the request
    query = user_query.query
    model = user_query.model
    system_message = user_query.system_message if hasattr(user_query, "system_message") else "You are a helpful assistant"
    
    # Validate and convert the parameters (temperature, top_p, max_tokens)
    temperature = validate_and_convert(user_query.temperature, default=None, param_type=float)
    top_p = validate_and_convert(user_query.top_p, default=None, param_type=float)
    max_tokens = validate_and_convert(user_query.max_tokens, default=None, param_type=int)
    stream = validate_and_convert(user_query.stream, default=False, param_type=bool)

    if isinstance(query, str):
        query = [{"role": "system", "content": system_message}, {"role": "user", "content": query}]
    
    if not stream:
        try:
            response = llms.get_chat_completion(
                query, model, temperature, top_p, max_tokens, stream=False
            )
            return {"response": response.choices[0].message.content}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    else: # stream=True
        try:
            # Stream response generator
            async def llm_stream():
                response = llms.get_chat_completion(
                    messages=query,
                    model=model,
                    temperature=temperature,
                    top_p=top_p,
                    max_tokens=max_tokens,
                    stream=True
                )
                for chunk in response:
                    try:
                        if not chunk.choices or not chunk.choices[0] or not chunk.choices[0].delta or not chunk.choices[0].delta.content:
                            continue
                        
                        message = chunk.choices[0].delta.content
                        if message:
                            yield message
                    except Exception as e:
                        print(f"Error: {e}")
                        if response.choices[0].text:
                            yield response.choices[0].text
            return StreamingResponse(llm_stream(), media_type="text/plain")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    
    
@app.post("/name")
async def get_response(user_query: UserQuery):
    # Extract the query from the request
    query = user_query.query
    system_message = """You are a helpful assistant, please help to name the conversation and return in the user query language and return the name only. 
    For example: 
    query: Tell me a joke
    response: Joke request and response
    """

    # Ensure `query` is a valid string
    if not isinstance(query, str) or not query.strip():
        raise HTTPException(status_code=400, detail="Invalid query. Query must be a non-empty string.")

    # Construct the payload for the LLM
    chat_payload = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": query}
    ]

    try:
        # Get the response from the LLM
        response = llms.get_chat_completion(chat_payload, model="gpt-4o-mini")

        # Validate response structure
        if not response or not response.choices or not response.choices[0].message:
            raise HTTPException(status_code=500, detail="Invalid response format from LLM.")
        
        # Return the content of the response
        return {"response": response.choices[0].message.content}

    except Exception as e:
        # Log the error (optional) and return an HTTP error
        raise HTTPException(status_code=500, detail="An error occurred while processing the request.")