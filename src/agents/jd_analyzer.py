import os
from src.engine.llm_service import LLMService

class JDAnalyzer:
    def __init__(self, llm_service: LLMService = None):
        self.llm_service = llm_service or LLMService()
        self.prompt_path = "src/prompts/jd_analysis_pt.txt"

    def _load_prompt(self):
        # Tạo file prompt mặc định nếu chưa có
        if not os.path.exists(self.prompt_path):
            return "Hãy phân tích bản mô tả công việc (JD) sau và trích xuất các yêu cầu chính: {jd_content}"
        with open(self.prompt_path, "r", encoding="utf-8") as f:
            return f.read()

    def analyze(self, jd_text: str):
        """
        Phân tích JD thô để lấy ra các yêu cầu về kỹ năng, kinh nghiệm.
        """
        template = self._load_prompt()
        prompt = template.format(jd_content=jd_text)
        response = self.llm_service.get_completion(prompt)
        return response

if __name__ == "__main__":
    analyzer = JDAnalyzer()
    # print(analyzer.analyze("Nội dung JD giả lập..."))
