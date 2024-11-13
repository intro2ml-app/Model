from openai import OpenAI

class QuestionRewriter:
    def __init__(self):
        """
        Initialize the QuestionRewriter with an API client and model name.
        """
        self.client = OpenAI(
            base_url="https://api.groq.com/openai/v1",
            api_key='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',
        )
        self.model = "gemma2-9b-it"

    def rewrite_question(self, question):
        """
        Rewrite the question to improve its clarity and suitability for web search or retrieval.

        Args:
            question (str): The original question from the user.

        Returns:
            str: A rewritten question that optimizes for retrieval or search.
        """
        # Define the system prompt
        system_prompt = """
        Bạn là một người viết lại câu hỏi để tối ưu hóa cho tìm kiếm web.
        Hãy xem xét ý định đằng sau câu hỏi và diễn đạt lại để tăng tính rõ ràng và phù hợp.
        Vui lòng đưa ra câu hỏi bằng tiếng Việt và chỉ viết câu hỏi, không cần giải thích.
        """

        # Create the full prompt combining the system instruction and user question
        prompt = f"{system_prompt}\n\nĐây là câu hỏi:\n\n{question}\n\nViết lại câu hỏi."

        # Send the prompt to the OpenAI API and get the rewritten question
        response = self.client.chat.completions.create(
            messages=[
                {"role": "user", "content": prompt},
            ],
            model=self.model,
        )

        # Extract and return the rewritten question from the response
        return response.choices[0].message.content.strip()
    
def rewrite_question(question):
    question_rewriter = QuestionRewriter()
    return question_rewriter.rewrite_question(question)

if __name__ == "__main__":
    question = "Thông tin về hội thao 2024"
    rewritten_question = rewrite_question(question)
    print(rewritten_question)