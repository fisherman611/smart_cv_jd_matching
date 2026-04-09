import json
import logging
import os
import re
import sys
from pathlib import Path
from typing import Any, List, Optional

from pydantic import BaseModel, ConfigDict, Field

# Thêm project root vào sys.path để tránh lỗi ModuleNotFoundError khi chạy trực tiếp
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.engine.llm_service import LLMService

logger = logging.getLogger(__name__)

class Question(BaseModel):
    content: str = Field(description="Nội dung câu hỏi phỏng vấn")
    goal: str = Field(description="Mục tiêu của câu hỏi")
    related_to: str = Field(description="Điểm mạnh hoặc điểm yếu liên quan")

class InterviewQuestions(BaseModel):
    model_config = ConfigDict(extra="ignore")
    questions: List[Question] = Field(default_factory=list)

class InterviewQuestionGenerator:
    def __init__(self, llm_service: Optional[LLMService] = None):
        self.llm_service = llm_service or LLMService()
        self.prompt_path = Path(__file__).resolve().parents[1] / "prompts" / "interview_question_generator_pt.txt"

    def _load_prompt(self):
        if not self.prompt_path.exists():
            raise FileNotFoundError(f"Prompt file not found at {self.prompt_path}")
        with open(self.prompt_path, "r", encoding="utf-8") as f:
            return f.read()

    def _try_parse_json_object(self, fragment: str) -> Optional[dict[str, Any]]:
        fragment = fragment.strip()
        if not fragment:
            return None
        try:
            out = json.loads(fragment)
            if isinstance(out, dict):
                return out
        except json.JSONDecodeError:
            pass
        start = fragment.find("{")
        end = fragment.rfind("}")
        if start != -1 and end != -1 and end > start:
            try:
                out = json.loads(fragment[start : end + 1])
                if isinstance(out, dict):
                    return out
            except json.JSONDecodeError:
                pass
        return None

    def _extract_json_object(self, text: str) -> dict[str, Any]:
        """
        Cố gắng bóc tách JSON object từ response text (kể cả khi bị bọc markdown).
        """
        if not text:
            raise ValueError("LLM response is empty")

        cleaned = text.strip()

        # Mỗi fence ``` ... ``` thử parse riêng
        for m in re.finditer(r"```(?:json)?\s*([\s\S]*?)\s*```", cleaned):
            block = m.group(1)
            parsed = self._try_parse_json_object(block)
            if parsed is not None:
                return parsed

        parsed = self._try_parse_json_object(cleaned)
        if parsed is not None:
            return parsed

        raise ValueError("Could not parse JSON object from LLM response")

    def _model_to_dict(self, model_obj: BaseModel) -> dict[str, Any]:
        if hasattr(model_obj, "model_dump"):
            return model_obj.model_dump()
        return model_obj.dict()

    def generate_questions(self, target_position: str, strengths: str, weaknesses: str, db_path: str) -> dict[str, Any]:
        """
        Tạo bộ câu hỏi phỏng vấn dựa trên vị trí ứng tuyển, điểm mạnh/yếu và database câu hỏi nội bộ.
        """
        # 1. Load Question Database
        if not os.path.exists(db_path):
            raise FileNotFoundError(f"Database file not found at {db_path}")
            
        with open(db_path, "r", encoding="utf-8") as f:
            db_content = json.load(f)
            
            # Lọc câu hỏi thông minh
            filtered_questions = []
            matching_role_found = False
            
            for role in db_content.get("roles", []):
                if target_position.lower() in role.get("ten_role", "").lower():
                    matching_role_found = True
                    for q in role.get("questions", []):
                        filtered_questions.append({
                            "question": q.get("cau_hoi"),
                            "type": q.get("loai"),
                            "role": role.get("ten_role")
                        })
                else:
                    for q in role.get("questions", []):
                        if q.get("loai") == "culture_fit":
                            filtered_questions.append({
                                "question": q.get("cau_hoi"),
                                "type": q.get("loai"),
                                "role": role.get("ten_role")
                            })
            
            if not matching_role_found:
                for role in db_content.get("roles", []):
                    for q in role.get("questions", []):
                        filtered_questions.append({
                            "question": q.get("cau_hoi"),
                            "type": q.get("loai"),
                            "role": role.get("ten_role")
                        })
            
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
        
        # 4. Ưu tiên structured output để đảm bảo đúng schema.
        try:
            parsed = self.llm_service.get_completion_with_structured_output(
                prompt=prompt,
                response_model=InterviewQuestions,
            )
            return InterviewQuestions.model_validate(parsed).model_dump()
        except Exception as e:
            logger.warning(
                "Structured generation output failed (%s); using text completion fallback",
                e,
            )

        # 5. Fallback: gọi completion thường
        raw_response = self.llm_service.get_completion(prompt)
        parsed_json = self._extract_json_object(raw_response or "")
        validated = InterviewQuestions.model_validate(parsed_json)
        return self._model_to_dict(validated)

if __name__ == "__main__":
    # Test shortcut
    gen = InterviewQuestionGenerator()
    sample_target_position = "Giảng viên Khoa học Máy tính"
    sample_strengths = "Kỹ năng Python tốt, có kinh nghiệm NLP 3 năm."
    sample_weaknesses = "Kỹ năng giao tiếp chưa tự tin, thiếu kinh nghiệm deploy hệ thống lớn."
    # print(gen.generate_questions(
    #     target_position=sample_target_position,
    #     strengths=sample_strengths,
    #     weaknesses=sample_weaknesses,
    #     db_path="data/interview_question_db.json"
    # ))
