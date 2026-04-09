import os
from src.engine.llm_service import LLMService

class CVAnalyzer:
    def __init__(self, llm_service: LLMService = None):
        self.llm_service = llm_service or LLMService()
        self.prompt_path = "src/prompts/cv_analysis_pt.txt"

    def _load_prompt(self):
        if not os.path.exists(self.prompt_path):
            return "Bạn là một chuyên gia tuyển dụng. Hãy phân tích CV sau: {cv_content}"
        with open(self.prompt_path, "r", encoding="utf-8") as f:
            return f.read()

    def analyze(self, cv_text: str):
        """
        Phân tích nội dung CV thô thành dữ liệu cấu trúc (JSON).
        """
        # 1. Load prompt template
        template = self._load_prompt()
        
        # 2. Format prompt
        prompt = template.format(cv_content=cv_text)
        
        # 3. Call LLM
        response = self.llm_service.get_completion(prompt)
        
        # TODO: Parse response JSON if needed
        return response

if __name__ == "__main__":
    # Test shortcut
    analyzer = CVAnalyzer()
    # print(analyzer.analyze("Nội dung CV giả lập..."))
