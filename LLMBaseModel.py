from openai import OpenAI

class LLMBaseModel:
    def __init__(self, api_key, base_url="https://api.openai.com/v1"):
        self.llmsModel = OpenAI(
            base_url=base_url,
            api_key=api_key,
        )
        
    def get_completion(self, messages, model="gpt-4o-mini", temperature=None, top_p=None, max_tokens=None, stream=False):
        # Prepare the arguments to pass to the API call, excluding None values
        params = {
            "model": model,
            "messages": messages,
            "stream": stream
        }

        # Add parameters only if they are not None
        if temperature is not None:
            params["temperature"] = temperature
        if top_p is not None:
            params["top_p"] = top_p
        if max_tokens is not None:
            params["max_tokens"] = max_tokens
        
        # Call the API with the filtered parameters
        return self.llmsModel.chat.completions.create(**params)
