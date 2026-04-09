import json
import logging
import os
import re
import sys
from pathlib import Path
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field

# Thêm project root vào sys.path để tránh lỗi ModuleNotFoundError khi chạy trực tiếp
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.engine.llm_service import LLMService

logger = logging.getLogger(__name__)

class DeepAnalysisResult(BaseModel):
    model_config = ConfigDict(extra="ignore")
    strengths: str = Field(default="", description="Điểm mạnh của ứng viên so với JD")
    weaknesses: str = Field(default="", description="Điểm yếu hoặc khoảng cách của ứng viên so với JD")

class CandidateDeepAnalyzer:
    def __init__(self, llm_service: Optional[LLMService] = None):
        self.llm_service = llm_service or LLMService()
        self.prompt_path = Path(__file__).resolve().parents[1] / "prompts" / "candidate_deep_analysis_pt.txt"

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
        if not text:
            raise ValueError("LLM response is empty")
        cleaned = text.strip()
        for m in re.finditer(r"```(?:json)?\s*([\s\S]*?)\s*```", cleaned):
            block = m.group(1)
            parsed = self._try_parse_json_object(block)
            if parsed is not None:
                return parsed
        parsed = self._try_parse_json_object(cleaned)
        if parsed is not None:
            return parsed
        raise ValueError("Could not parse JSON object from LLM response")

    def analyze(self, cv_analysis: dict, jd_analysis: dict) -> dict[str, Any]:
        """
        Đối chiếu CV và JD để đưa ra phân tích sâu về điểm mạnh và điểm yếu.
        """
        # 1. Load prompt template
        template = self._load_prompt()
        
        # 2. Format prompt
        prompt = template.format(
            cv_analysis=json.dumps(cv_analysis, ensure_ascii=False, indent=2),
            jd_analysis=json.dumps(jd_analysis, ensure_ascii=False, indent=2)
        )
        
        # 3. Ưu tiên structured output
        try:
            parsed = self.llm_service.get_completion_with_structured_output(
                prompt=prompt,
                response_model=DeepAnalysisResult,
            )
            return DeepAnalysisResult.model_validate(parsed).model_dump()
        except Exception as e:
            logger.warning("Structured Deep Analysis failed (%s); using fallback", e)

        # 4. Fallback
        raw_response = self.llm_service.get_completion(prompt)
        parsed_json = self._extract_json_object(raw_response or "")
        validated = DeepAnalysisResult.model_validate(parsed_json)
        return validated.model_dump()

if __name__ == "__main__":
    analyzer = CandidateDeepAnalyzer()
    # Test shortcut logic here if needed
