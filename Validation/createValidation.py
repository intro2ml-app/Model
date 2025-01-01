import os
import json
import random
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

ValidationFolder = "../Data/validation"

def getTextFiles(folder):
    # Get all text files in the folder and its subfolders
    files = []
    for root, _, filenames in os.walk(folder):
        for file in filenames:
            if file.endswith(".txt"):
                files.append(os.path.join(root, file))
    return files

def createQuestion(text):
    client = OpenAI(api_key = os.getenv("OPENAI_API_KEY"))
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": """Bạn là trợ lý ảo. Hãy giúp tôi tạo ra tầm 10 câu hỏi từ thông tin được cung cấp. Hãy trả về theo json.
            Output mong muốn:
            {
                "input": "Câu hỏi 1",
                "output": "Câu trả lời 1"
            }
            """
            },
            {
                "role": "user",
                "content": text
            }
        ]
    )
    return completion.choices[0].message.content

def createValidationFile():
    files = getTextFiles("../Data")
    for file in files:
        file_name = file.split(".")[-2].split("/")[-1].split("\\")[-1]
        if file_name in ["bo-mon-hcmus", "giangvien-hcmus", "khoa-hcmus", "web", "invalid_chars"]:
            continue
        print(file_name)
        with open("../Data/" + file, encoding='utf-8') as f:
            text = f.read()
            text = text.replace("\n", " ")
            questions_str = createQuestion(text)
            questions_str = questions_str[questions_str.find("["):questions_str.rfind("]")+ 1]
            print(questions_str)
            questions = json.loads(questions_str)
            with open(f"../Data/validation2/{file_name}.json", "w", encoding='utf-8') as f:
                json.dump(questions, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    # createValidationFile()
    question_list = []
    for file in os.listdir(ValidationFolder):
        with open(os.path.join(ValidationFolder, file), encoding='utf-8') as f:
            data = json.load(f)
            for i in data:
                question_list.append(i)
    
    # random select 200 questions and dump to a json file
    random.shuffle(question_list)
    question_list = question_list[:100]
    with open("validation.json", "w", encoding='utf-8') as f:
        json.dump(question_list, f, ensure_ascii=False, indent=4)