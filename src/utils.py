import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)

def calculate_matching_score(cv_data: Dict[str, Any], jd_data: Dict[str, Any]) -> float:
    """
    Tính toán điểm matching giữa CV và JD dựa trên từ khóa (Keywords Matching).
    
    Logic:
    - So khớp kỹ năng kỹ thuật (Technical Skills).
    - So khớp kỹ năng mềm (Soft Skills) - nếu JD có đề cập.
    - Điểm cộng cho Preferred Skills.
    """
    try:
        cv_tech_skills = set(s.lower().strip() for s in cv_data.get("technical_skills", []))
        jd_req_skills = set(s.lower().strip() for s in jd_data.get("required_skills", []))
        jd_pref_skills = set(s.lower().strip() for s in jd_data.get("preferred_skills", []))
        
        if not jd_req_skills:
            return 0.0
            
        # 1. Điểm kỹ năng bắt buộc (Trọng số 70%)
        matches_req = cv_tech_skills.intersection(jd_req_skills)
        score_req = len(matches_req) / len(jd_req_skills) if jd_req_skills else 0
        
        # 2. Điểm kỹ năng ưu tiên (Trọng số 30%)
        # Nếu không có kỹ năng ưu tiên trong JD, ta coi như ứng viên đạt tối đa phần này nếu có skill bắt buộc tốt
        if jd_pref_skills:
            matches_pref = cv_tech_skills.intersection(jd_pref_skills)
            score_pref = len(matches_pref) / len(jd_pref_skills)
        else:
            score_pref = score_req # Fallback
            
        final_score = (score_req * 0.7) + (score_pref * 0.3)
        
        # Làm tròn 2 chữ số thập phân
        return round(final_score * 100, 2)
        
    except Exception as e:
        logger.error(f"Lỗi khi tính điểm matching: {e}")
        return 0.0

def rank_candidates(candidates: List[Dict[str, Any]], jd_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Xếp hạng danh sách ứng viên dựa trên điểm matching với JD.
    Đầu vào: 
    - candidates: Danh sách dict, mỗi dict chứa cv_analysis và thông tin ứng viên.
    - jd_data: Kết quả phân tích JD.
    """
    ranked_list = []
    
    for candidate in candidates:
        cv_analysis = candidate.get("cv_analysis", {})
        score = calculate_matching_score(cv_analysis, jd_data)
        
        # Gắn thêm điểm số vào object ứng viên
        candidate_with_score = candidate.copy()
        candidate_with_score["matching_score"] = score
        ranked_list.append(candidate_with_score)
        
    # Sắp xếp giảm dần theo điểm số
    ranked_list.sort(key=lambda x: x["matching_score"], reverse=True)
    
    return ranked_list

if __name__ == "__main__":
    # Test nhanh logic matching
    mock_cv = {
        "technical_skills": ["Python", "SQL", "Machine Learning", "Docker"]
    }
    mock_jd = {
        "required_skills": ["Python", "SQL", "Deep Learning"],
        "preferred_skills": ["Docker", "Kubernetes"]
    }
    
    score = calculate_matching_score(mock_cv, mock_jd)
    print(f"Test Matching Score: {score}%")
