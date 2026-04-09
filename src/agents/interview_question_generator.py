import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import json
from src.engine.llm_service import LLMService

class InterviewQuestionGenerator:
    def __init__(self, llm_service: LLMService = None):
        self.llm_service = llm_service or LLMService()
        self.prompt_path = "src/prompts/interview_question_generator_pt.txt"

    def _load_prompt(self):
        if not os.path.exists(self.prompt_path):
            raise FileNotFoundError(f"Prompt file not found at {self.prompt_path}")
        with open(self.prompt_path, "r", encoding="utf-8") as f:
            return f.read()

    def generate_questions(self, target_position: str, strengths: str, weaknesses: str, db_path: str):
        """
        Tạo bộ câu hỏi phỏng vấn dựa trên vị trí ứng tuyển, điểm mạnh/yếu và database câu hỏi nội bộ.
        """
        # 1. Load Question Database
        if not os.path.exists(db_path):
            return f"Error: Database file not found at {db_path}"
            
        with open(db_path, "r", encoding="utf-8") as f:
            db_content = json.load(f)
            # Lọc câu hỏi thông minh dựa trên vị trí ứng tuyển
            filtered_questions = []
            matching_role_found = False
            
            for role in db_content.get("roles", []):
                # Kiểm tra xem tên role trong DB có khớp với vị trí ứng tuyển không (không phân biệt hoa thường)
                if target_position.lower() in role.get("ten_role", "").lower():
                    matching_role_found = True
                    for q in role.get("questions", []):
                        filtered_questions.append({
                            "question": q.get("cau_hoi"),
                            "type": q.get("loai"),
                            "role": role.get("ten_role")
                        })
                else:
                    # Vẫn lấy các câu hỏi culture_fit từ các role khác vì thường mang tính tổ chức
                    for q in role.get("questions", []):
                        if q.get("loai") == "culture_fit":
                            filtered_questions.append({
                                "question": q.get("cau_hoi"),
                                "type": q.get("loai"),
                                "role": role.get("ten_role")
                            })
            
            # Nếu không tìm thấy role nào khớp, lấy toàn bộ câu hỏi (fallback)
            if not matching_role_found:
                filtered_questions = []
                for role in db_content.get("roles", []):
                    for q in role.get("questions", []):
                        filtered_questions.append({
                            "question": q.get("cau_hoi"),
                            "type": q.get("loai"),
                            "role": role.get("ten_role")
                        })
            
            # Giới hạn số lượng câu hỏi gửi vào LLM để tránh loãng và tiết kiệm token
            # Sắp xếp để câu hỏi của role phù hợp lên đầu
            db_string = json.dumps(filtered_questions[:30], ensure_ascii=False, indent=2)

        # 2. Load Prompt Template
        template = self._load_prompt()
        
        # 3. Format Prompt
        prompt = template.format(
            target_position=target_position,
            strengths=strengths,
            weaknesses=weaknesses,
            question_db=db_string
        )
        
        # 4. Call LLM
        response = self.llm_service.get_completion(prompt)
        return response

if __name__ == "__main__":
    gen = InterviewQuestionGenerator(llm_service=LLMService())

    sample_target_position = "Giảng viên Khoa học Máy tính"
    sample_strengths = "Kỹ năng Python tốt, có kinh nghiệm NLP 3 năm."
    sample_weaknesses = "Kỹ năng giao tiếp chưa tự tin, thiếu kinh nghiệm deploy hệ thống lớn."
    print(gen.generate_questions(
        target_position=sample_target_position,
        strengths=sample_strengths,
        weaknesses=sample_weaknesses,
        db_path="data/interview_question_db.json"
    ))
