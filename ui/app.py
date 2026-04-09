import streamlit as st
import json
import os
import sys
import time
from pathlib import Path
from dotenv import load_dotenv

# Thêm project root vào sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.engine.llm_service import LLMService
from src.agents.cv_analyzer import CVAnalyzer
from src.agents.jd_analyzer import JDAnalyzer
from src.agents.candidate_deep_analyzer import CandidateDeepAnalyzer
from src.agents.interview_question_generator import InterviewQuestionGenerator
from src.utils import calculate_matching_score_v2 # Đã update lên v2 theo thay đổi của bạn

load_dotenv()

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="Smart CV-JD Matcher",
    page_icon="🎯",
    layout="wide",
)

# --- CUSTOM CSS FOR PREMIUM LOOK ---
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        height: 3em;
        background-color: #1e3a8a;
        color: white;
        font-weight: bold;
        border: none;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #3b82f6;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.5);
    }
    .candidate-card {
        background-color: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 20px;
        border-left: 5px solid #1e3a8a;
    }
    .score-badge {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
        color: white;
        padding: 5px 15px;
        border-radius: 20px;
        font-weight: bold;
        float: right;
    }
    .log-container {
        background-color: #1a1a1a;
        color: #00ff00;
        padding: 15px;
        border-radius: 10px;
        font-family: 'Courier New', Courier, monospace;
        font-size: 14px;
        height: 300px;
        overflow-y: auto;
        border: 1px solid #333;
    }
    </style>
    """, unsafe_allow_html=True)

# --- SESSION STATE ---
if 'processed_results' not in st.session_state:
    st.session_state.processed_results = None
if 'logs' not in st.session_state:
    st.session_state.logs = []

def add_log(message, placeholder):
    timestamp = time.strftime("%H:%M:%S")
    log_entry = f"[{timestamp}] {message}"
    st.session_state.logs.append(log_entry)
    # Giới hạn số lượng log hiển thị
    if len(st.session_state.logs) > 50:
        st.session_state.logs.pop(0)
    
    # Cập nhật placeholder
    log_content = "\\n".join(st.session_state.logs)
    placeholder.markdown(f'<div class="log-container">{log_content}</div>', unsafe_allow_html=True)

# --- INITIALIZE AGENTS ---
@st.cache_resource
def get_agents():
    llm = LLMService(temperature=0.1)
    return (
        CVAnalyzer(llm_service=llm),
        JDAnalyzer(llm_service=llm),
        CandidateDeepAnalyzer(llm_service=llm),
        InterviewQuestionGenerator(llm_service=llm)
    )

cv_agent, jd_agent, deep_agent, question_agent = get_agents()

# --- SIDEBAR ---
with st.sidebar:
    st.image("https://img.icons8.com/clouds/100/000000/resume.png", width=100)
    st.title("Settings")
    top_n = st.slider("Select Top-N for Deep Analysis", 1, 10, 3)
    db_path = st.text_input("Interview DB Path", "data/interview_question_db.json")
    if st.button("Clear Logs & Results"):
        st.session_state.processed_results = None
        st.session_state.logs = []
        st.rerun()
    st.divider()
    st.info("💡 Project hỗ trợ nhà tuyển dụng lọc CV và chuẩn bị phỏng vấn tự động.")

# --- MAIN UI ---
st.title("🎯 Smart CV-JD Matching System")
st.markdown("### Giải pháp tuyển dụng AI hỗ trợ Hackathon")

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📋 Bước 1: Job Description (JD)")
    # accept_multiple_files=False để chỉ cho phép 1 JD
    jd_file = st.file_uploader("Upload duy nhất 1 JD (.txt)", type=["txt"], accept_multiple_files=False)
    if jd_file:
        jd_text = jd_file.read().decode("utf-8")
        st.text_area("Nội dung JD preview", jd_text, height=150)

with col2:
    st.subheader("📄 Bước 2: Curricula Vitae (CVs)")
    cv_files = st.file_uploader("Upload danh sách CVs (.txt)", type=["txt"], accept_multiple_files=True)
    if cv_files:
        st.write(f"Đã chọn {len(cv_files)} hồ sơ ứng viên.")

# --- PROCESSING ---
if st.button("🚀 Bắt đầu Matching & Ranking"):
    if not jd_file or not cv_files:
        st.error("Vui lòng tải lên đúng 1 JD và ít nhất một CV!")
    else:
        st.session_state.logs = [] # Reset logs
        st.subheader("⚙️ Processing Pipeline Logs")
        log_placeholder = st.empty()
        
        try:
            # 1. Analyze JD
            add_log("Starting Step 1: Analyzing Job Description...", log_placeholder)
            jd_analysis = jd_agent.analyze(jd_text)
            add_log(f"JD Analyzed: {jd_analysis.get('job_title')}", log_placeholder)
            
            # 2. Analyze all CVs
            add_log(f"Starting Step 2: Analyzing {len(cv_files)} CVs...", log_placeholder)
            all_candidates = []
            progress_bar = st.progress(0)
            
            for idx, cv_file in enumerate(cv_files):
                add_log(f"Analyzing CV ({idx+1}/{len(cv_files)}): {cv_file.name}", log_placeholder)
                cv_text = cv_file.read().decode("utf-8")
                cv_analysis = cv_agent.analyze(cv_text)
                
                # Tính điểm bằng v2 đã update logic robust hơn
                score = calculate_matching_score_v2(cv_analysis, jd_analysis)
                add_log(f"  -> {cv_analysis.get('full_name', cv_file.name)}: Score {score}%", log_placeholder)
                
                all_candidates.append({
                    "name": cv_analysis.get("full_name", cv_file.name),
                    "analysis": cv_analysis,
                    "score": score,
                    "file_name": cv_file.name
                })
                progress_bar.progress((idx + 1) / len(cv_files))
            
            # 3. Rank entries
            add_log("Step 3: Ranking candidates...", log_placeholder)
            all_candidates.sort(key=lambda x: x["score"], reverse=True)
            
            # 4. Deep Analysis for Top-N
            add_log(f"Step 4: Deep Analysis for Top {top_n} candidates...", log_placeholder)
            results = []
            for i, candidate in enumerate(all_candidates[:top_n]):
                add_log(f"Detailed Analysis for: {candidate['name']}", log_placeholder)
                deep_res = deep_agent.analyze(candidate["analysis"], jd_analysis)
                
                add_log(f"Generating optimized questions for: {candidate['name']}", log_placeholder)
                questions = question_agent.generate_questions(
                    target_position=jd_analysis.get("job_title", "Position"),
                    strengths=deep_res.get("strengths", ""),
                    weaknesses=deep_res.get("weaknesses", ""),
                    db_path=db_path
                )
                
                results.append({
                    **candidate,
                    "deep_analysis": deep_res,
                    "questions": questions
                })
            
            st.session_state.processed_results = {
                "top_results": results,
                "all_ranks": all_candidates,
                "jd": jd_analysis
            }
            add_log("✅ Pipeline completed successfully!", log_placeholder)
            st.rerun() # Refresh to show results
            
        except Exception as e:
            add_log(f"❌ Error occurred: {str(e)}", log_placeholder)
            st.error(f"Đã xảy ra lỗi: {e}")

# --- DISPLAY RESULTS ---
if st.session_state.processed_results:
    res = st.session_state.processed_results
    
    st.divider()
    st.subheader(f"📊 Kết quả xếp hạng cho vị trí: {res['jd'].get('job_title')}")
    
    # Dashboard summary
    m1, m2, m3 = st.columns(3)
    m1.metric("Tổng số ứng viên", len(res['all_ranks']))
    m2.metric("Điểm cao nhất", f"{res['all_ranks'][0]['score']}%")
    m3.metric("Số lượng Top-N đã chọn", len(res['top_results']))

    # Tabs for different views
    tab1, tab2 = st.tabs(["🏆 Top-N Chi tiết", "📂 Bảng xếp hạng tổng quát"])
    
    with tab1:
        for idx, candidate in enumerate(res['top_results']):
            with st.container():
                st.markdown(f"""
                <div class="candidate-card">
                    <span class="score-badge">Score: {candidate['score']}%</span>
                    <h3>#{idx+1} {candidate['name']}</h3>
                    <p><b>Summary:</b> {candidate['analysis'].get('summary', 'No summary available.')}</p>
                </div>
                """, unsafe_allow_html=True)
                
                col_a, col_b = st.columns(2)
                with col_a:
                    st.success("🟢 **Điểm mạnh**")
                    st.write(candidate['deep_analysis'].get('strengths', 'Đang cập nhật...'))
                with col_b:
                    st.warning("🟡 **Điểm yếu / Khoảng cách**")
                    st.write(candidate['deep_analysis'].get('weaknesses', 'Đang cập nhật...'))
                
                with st.expander("📝 Xem bộ câu hỏi phỏng vấn đề xuất"):
                    if isinstance(candidate['questions'], dict) and "questions" in candidate['questions']:
                        for q in candidate['questions']['questions']:
                            st.write(f"❓ **{q.get('content')}**")
                            st.caption(f"*Mục tiêu:* {q.get('goal')}")
                            st.divider()
                    else:
                        st.write(candidate['questions'])
                st.write("")

    with tab2:
        # Chuẩn bị dữ liệu bảng
        table_data = []
        for c in res['all_ranks']:
            table_data.append({
                "Hạng": res['all_ranks'].index(c) + 1,
                "Ứng viên": c['name'],
                "Matching Score": f"{c['score']}%",
                "Kinh nghiệm (năm)": c['analysis'].get('years_of_experience', 0),
                "Học vấn": c['analysis'].get('education', 'N/A')
            })
        st.table(table_data)

st.divider()
st.caption("Developed by team Hackathon | Optimized by Google Gemini Model")
