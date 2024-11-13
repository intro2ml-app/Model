from openai import OpenAI

# Tạo lớp `RetrievalGrader`
class RetrievalGrader:
    def __init__(self):
        # Khởi tạo OpenAI client với API key và model
        self.client = OpenAI(
            base_url="https://api.groq.com/openai/v1",
            api_key='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',
        )

        # Sử dụng model phù hợp
        self.model = "gemma2-9b-it"

    def grade_document(self, document, question):
        prompt = f"""
        You are a grader assessing relevance of a retrieved document to a user question.
        If the document related to the question and can answer the question, grade it as relevant.
        Give a binary score 'yes' or 'no' to indicate whether the document is relevant to the question.

        Retrieved document: \n\n{document}\n\nUser question: {question}
        """

        # Gửi prompt đến OpenAI API và nhận phản hồi
        response = self.client.chat.completions.create(
            messages=[
                {"role": "user", "content": prompt},
            ],
            model=self.model,
        )

        # Lấy kết quả từ response
        return response.choices[0].message.content.strip()
    

def grade_document(document, question):
    retrieval_grader = RetrievalGrader()
    return retrieval_grader.grade_document(document, question)

if __name__ == "__main__":
    # Tạo instance của `RetrievalGrader`
    retrieval_grader = RetrievalGrader()

    # đánh giá kết quả truy suất đầu tiên từ vectodb
    document = """
    GS. Trần Thế Truyền nhấn mạnh rằng AI không chỉ là bước tiến công nghệ mà còn là cơ hội lớn cho nhân loại trong việc giải quyết các thách thức toàn cầu. Ông cũng chỉ ra rằng Việt Nam đang có nhiều lợi thế để trở thành quốc gia tiên phong trong lĩnh vực AI, nhờ vào nguồn nhân lực trẻ và dồi dào, hệ sinh thái giáo dục phát triển, cùng với sự quan tâm từ xã hội.

    Trong buổi phỏng vấn, GS. Trần Thế Truyền đã khuyến khích thế hệ trẻ thể hiện sự dũng cảm và suy nghĩ sáng tạo. Việc tham gia vào lĩnh vực AI không chỉ đơn thuần là học hỏi công nghệ, mà còn là trách nhiệm đối với những hệ quả mà công nghệ này mang lại cho xã hội và môi trường.
    """
    print(document)

    question="GS. Trần Thế Truyền đã làm gì trong buổi phỏng vấn?"

    score = retrieval_grader.grade_document(document, question=question)
    print("Relevance score:", score)