import os
from dotenv import load_dotenv
from src.engine.llm_service import LLMService
from src.agents.cv_analyzer import CVAnalyzer
from src.agents.jd_analyzer import JDAnalyzer
from src.agents.interview_question_selector import InterviewQuestionSelector

load_dotenv()

def match_cv_jd(cv_analysis, jd_analysis):
    """
    Hàm matching giữa kết quả phân tích CV và JD.
    Có thể dùng Cosine Similarity hoặc LLM để chấm điểm.
    """
    print("--- 🔄 Matching CV with JD ---")
    # Tạm thời trả về mock score
    return 0.85

def main():
    print("🚀 Smart CV-JD Matching Pipeline Starting...")
    
    # 0. Khởi tạo LLM Service và các Agents
    llm = LLMService(temperature=0.2)
    cv_agent = CVAnalyzer(llm_service=llm)
    jd_agent = JDAnalyzer(llm_service=llm)
    question_agent = InterviewQuestionSelector(llm_service=llm)
    
    # 1. Load Data (Ví dụ)
    # cv_text = "Họ tên: Nguyễn Văn A. Kinh nghiệm: 5 năm Python..."
    # jd_text = "Yêu cầu: Có kinh nghiệm xây dựng hệ thống với Python..."
    
    # 2. Analyze CV & JD
    print("Step 1: Analyzing CV & JD...")
    # cv_json = cv_agent.analyze(cv_text)
    # jd_json = jd_agent.analyze(jd_text)
    
    # 3. Matching
    print("Step 2: Matching Top-N candidates...")
    # score = match_cv_jd(cv_json, jd_json)
    
    # 4. Question Selection
    print("Step 3: Selecting interview questions...")
    # questions = question_agent.select_questions(cv_json, "data/database/questions.json")
    
    print("✅ Pipeline work-flow completed (Check logs for details).")

if __name__ == "__main__":
    main()
