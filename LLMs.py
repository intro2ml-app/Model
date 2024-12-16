from dotenv import load_dotenv
from utils import parse_model
import os
from LLMBaseModel import LLMBaseModel

load_dotenv()

class LLMs:
    def __init__(self):
        self.clients = {
            "OPENAI": LLMBaseModel(
                api_key=os.environ.get("OPENAI_API_KEY")
            ),
            "GROQ": LLMBaseModel(
                api_key=os.environ.get("GROQ_API_KEY"),
                base_url="https://api.groq.com/openai/v1"
            ),
            "GITHUB": LLMBaseModel(
                api_key=os.environ.get("GITHUB_API_KEY"),
                base_url="https://models.inference.ai.azure.com"
            ),
            "GLHF": LLMBaseModel(
                api_key=os.environ.get("GLHF_API_KEY"),
                base_url="https://glhf.chat/api/openai/v1"
            ),
            "SAMBANOVA": LLMBaseModel(
                api_key=os.environ.get("SAMBANOVA_API_KEY"),
                base_url="https://api.sambanova.ai/v1",
            ),
            "USGPT": None,
            "USGPT_RAG": None,
        }

    def get_chat_completion_multi(self, messages, model="gpt-4o-mini", temperature=None, top_p=None, max_tokens=None, stream=False) -> str:
        models = parse_model(model)
        respone = "I'm sorry, I couldn't find an answer to your question."
        
        for model in models:
            model_name, client_name = ":".join(model.split(":")[:-1]), model.split(":")[-1]
            client = self.clients.get(client_name)

            print(f"-------------------------")
            print(f"conversation: {messages}")
            print(f"Model: {model}")
            print(f"-------------------------")

            if not client:
                raise ValueError(f"Unsupported client: {client_name}")

            try:
                response = client.get_completion(
                    model=model_name,
                    messages=messages,
                    temperature=temperature,
                    top_p=top_p,
                    max_tokens=max_tokens,
                    stream=stream
                )
                return response
            except Exception as e:
                print(e)
                print(f"Retrying with another hosting...")
                continue
        return {"choices": [{"text": "I'm sorry, I couldn't find an answer to your question."}]}
    
    def get_chat_completion_single(self, message, model="gpt-4o-mini", temperature=None, top_p=None, max_tokens=None, system_message="You are a helpful assistant", stream=False):
        messages = [{"role": "system", "content": system_message}, {"role": "user", "content": message}]
        models = parse_model(model)

        for model in models:
            model_name, client_name = ":".join(model.split(":")[:-1]), model.split(":")[-1]
            client = self.clients.get(client_name)
            print(f"-------------------------")
            print(f"conversation: {messages}")
            print(f"Model: {model}")
            print(f"-------------------------")
            if not client:
                raise ValueError(f"Unsupported client: {client_name}")

            try:
                response = client.get_completion(
                    model=model_name,
                    messages=messages,
                    temperature=temperature,
                    top_p=top_p,
                    max_tokens=max_tokens,
                    stream=stream
                )
                return response
            except Exception as e:
                print(f"Error: {e}")
                print(f"Retrying with another hosting...")
                continue

        return {"choices": [{"text": "I'm sorry, I couldn't find an answer to your question."}]}

if __name__ == "__main__":
    import json
    import time
    lst = []
    async def main():
        llms = LLMs()
        json_data = open("models.json").read()
        json_data = json.loads(json_data)
        test_models = [key for key in json_data.keys()]
        for model in test_models:
            # print(f"Testing model: {model}")
            # print("System: You are a helpful assistant")
            # print("User: Hello, what is your name?")
            begin = time.time()
            response = llms.get_chat_completion_multi(
                messages=[
                    {"role": "system", "content": "You are a helpful assistant"},
                    {"role": "user", "content": "how to solve quadratic equation"}
                ],
                model=model
            )
            end = time.time()
            run_time = end - begin
            print(f"Time: {run_time}")
            lst.append((model, run_time))
            # print(f"Model respone: {response}")
            print("\n")

        # sort the list
        
        print("\n\n\nSorted list====================")
        lst = sorted(lst, key=lambda x: x[1])
        for item in lst:
            print(f"Model: {item[0]} - Time: {item[1]}")
    

    import asyncio
    asyncio.run(main())  # This will run the asynchronous main function
