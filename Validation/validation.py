import os
import json
import requests
from openai import OpenAI
import sys
from time import sleep

def log(message):
    # write to log file
    with open("log_USGPT_RAG.txt", "a", encoding='utf-8') as f:
        f.write(message + "\n")

def getValidationData():
    validation_file = "validation.json"
    with open(validation_file, encoding='utf-8') as f:
        data = json.load(f)
    return data

def makeRequestToLLM(query, model="USGPT"):
    url = "http://127.0.0.1:8000"
    payload = {
        "query": query,
        "model": model
    }
    
    # Number of attempts
    attempts = 3
    for attempt in range(1, attempts + 1):
        try:
            # Send POST request to the specified URL
            response = requests.post(f"{url}/query", json=payload)
            response.raise_for_status()  # Raise an error for HTTP errors
            
            # Parse the JSON response
            response_data = response.json()
            return response_data
        except requests.exceptions.RequestException as e:
            # Handle errors related to the request
            log(f"Attempt {attempt} failed: {str(e)}")
            if attempt == attempts:
                return {"error": f"Request failed after {attempts} attempts: {str(e)}. Make sure the server is running and the URL is correct."}
        except Exception as e:
            # Handle any other exceptions
            log(f"Attempt {attempt} failed: {str(e)}")
            if attempt == attempts:
                return {"error": f"An error occurred after {attempts} attempts: {str(e)}. Make sure the server is running and the URL is correct."}
        sleep(4)
    # In case all attempts fail, exit the program
    sys.exit("Exiting after 3 failed attempts")

client = OpenAI()

def compareResults(QA, output):
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": """Bạn là trợ lý ảo. Hãy giúp tôi đánh giá mô hình thông qua câu trả lời. Hãy trả về theo json. Hãy đánh giá về mặt ngữ nghĩa, chỉ cần có ý giống nhau là được, không cần đủ.
            Ví dụ: 
            Input: Thí sinh tham gia Cuộc thi học thuật Thách Thức cần đáp ứng yêu cầu gì về trình độ?
            Output: Thí sinh không cần đáp ứng yêu cầu về trình độ chuyên môn, điều kiện duy nhất là phải là sinh viên của một trường đại học.
            Response: Thí sinh tham gia Cuộc thi học thuật Thách Thức cần là học sinh, sinh viên yêu thích và đam mê Công nghệ thông tin, đang học tại các trường Đại học, Cao đẳng, hoặc Trung học Phổ thông trên cả nước. Các thí sinh sẽ đăng ký dự thi theo nhóm và lập thành đội thi, với mỗi đội gồm 5 thành viên. Ngoài ra, tên riêng của đội thi phải viết và đọc được, không trùng lặp và gây nhầm lẫn với tên các đội khác.
            
            Trả lời:
            {
                "correct": true,
                "explain": "Câu trả lời của mô hình chính xác"
            }
            """},
            {
                "role": "user",
                "content": f"""
                    "Question": {QA['input']},
                    "Answer": {QA['output']},
                    "LLM output": {output}
                """
            }
        ]
    )
    return completion.choices[0].message.content


def preprocessJson(output):
    output = output[output.find("{"):output.rfind("}")+1]
    return output

if __name__ == "__main__":
    data = getValidationData()
    correct = 0
    for i in data:
        log(f"Input: {i['input']}")
        log(f"Output: {i['output']}")
        respond = makeRequestToLLM(i['input'], model="USGPT-RAG")
        log(f"Response: {respond['response']}")
        output = compareResults(i, respond['response'])
        output = preprocessJson(output)
        log(output)
        output = json.loads(output)
        
        if output["correct"] == True:
            correct += 1
            log(f"Correct: ✅ {36 + correct}/100 ✅")
            log("\n------------------------------------------------\n")
        else:
            log(f"Correct: ❌ {36 + correct}/100 ❌")
            log("\n------------------------------------------------\n")
        sleep(2)