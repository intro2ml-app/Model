from LLMBaseModel import LLMBaseModel
from dotenv import load_dotenv
import os
import requests

load_dotenv()

from typing import List

class Message:
    def __init__(self, content):
        self.content = content

class Choice:
    def __init__(self, message):
        self.message = Message(**message)

class Response:
    def __init__(self, choices):
        self.choices = [Choice(**choice) for choice in choices]

class USGPT(LLMBaseModel):
    def __init__(self, api_key):
        super().__init__(api_key=api_key)
        self.url = os.getenv("USGPT_URL")
        
    def get_completion(self, messages, model="gpt-4o-mini", temperature=None, top_p=None, max_tokens=None, stream=False):
        # Formulate the request payload
        payload = {
            "query": messages[-1]["content"]
        }
        print(f"USGPT payload: {payload}")
        print(f"USGPT URL: {self.url}/query")
        try:
            # Send POST request to the specified URL
            response = requests.post(f"{self.url}/query", json=payload)
            print(f"USGPT response: {response}")
            response.raise_for_status()  # Raise an error for HTTP errors
            
            # Parse the JSON response
            response_data = response.json()
            
            # Extract the part of the response after "Output:"
            if "response" in response_data:
                output_start = response_data["response"].find("### Output:") + len("### Output:")
                extracted_output = response_data["response"][output_start:].strip()
                output = {
                    "choices": [
                        {
                            "message": {
                                "content": extracted_output
                            }
                        }
                    ]
                }
                output = Response(**output)
                print(f"USGPT output: {output}")
                return output
            else:
                return {"error": "No 'response' key in the response data"}
        except requests.exceptions.RequestException as e:
            # Handle errors related to the request
            return {"error": f"Request failed: {str(e)}"}
        except Exception as e:
            # Handle any other exceptions
            return {"error": f"An error occurred: {str(e)}"}