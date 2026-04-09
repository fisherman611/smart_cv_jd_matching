# SPEC — AI Product Hackathon

**Nhóm:** Smart CV-JD Matching Team
**Track:** ☐ VinFast · ☐ Vinmec · ☑ VinUni-VinSchool · ☐ XanhSM · ☐ Open
**Problem statement (1 câu):** Nhà tuyển dụng mất hàng giờ đọc CV và chuẩn bị phỏng vấn thủ công — AI tự động phân tích CV, matching với JD, xếp hạng ứng viên và tạo câu hỏi phỏng vấn tùy chỉnh

---

## 1. AI Product Canvas

|   | Value | Trust | Feasibility |
|---|-------|-------|-------------|
| **Câu hỏi** | User nào? Pain gì? AI giải gì? | Khi AI sai thì sao? User sửa bằng cách nào? | Cost/latency bao nhiêu? Risk chính? |
| **Trả lời** | HR/Recruiter mất 2-3 giờ/vị trí để đọc 50+ CV, matching thủ công, chuẩn bị câu hỏi phỏng vấn — AI tự động phân tích CV, tính matching score (keyword + semantic), xếp hạng top-N, phân tích sâu điểm mạnh/yếu, và tạo bộ câu hỏi phỏng vấn tùy chỉnh từ database nội bộ | AI matching sai → user xem chi tiết phân tích (skills, experience, summary), điều chỉnh top-N selection, hoặc chỉnh sửa câu hỏi phỏng vấn trước khi sử dụng | ~$0.05-0.10/CV (NVIDIA API), latency 3-5s/CV, 10-15s cho deep analysis. Risk: hallucinate skills không có trong CV, bias trong matching algorithm, câu hỏi phỏng vấn không phù hợp văn hóa công ty |

**Automation hay augmentation?** ☐ Automation · ☑ Augmentation
Justify: Augmentation — AI đề xuất top-N candidates với matching score, HR review và quyết định cuối cùng. Câu hỏi phỏng vấn được generate nhưng HR có thể chỉnh sửa trước khi sử dụng. Cost of reject thấp vì chỉ cần skip candidate hoặc edit questions.

**Learning signal:**

1. User correction đi vào đâu? Hiện tại chưa có feedback loop. Trong tương lai: HR chọn/bỏ candidate → log vào database để fine-tune matching weights
2. Product thu signal gì để biết tốt lên hay tệ đi? Tracking: % candidates được chọn phỏng vấn từ top-N, % câu hỏi được giữ nguyên vs chỉnh sửa, thời gian HR dành cho review (giảm từ 2-3h xuống <30 phút)
3. Data thuộc loại nào? ☑ Domain-specific · ☑ Human-judgment · ☐ User-specific · ☐ Real-time · ☐ Khác: ___
   Có marginal value không? Có — CV và JD của công ty chứa domain knowledge (technical skills, role requirements) mà general LLM chưa tối ưu. Interview question database nội bộ phản ánh văn hóa và tiêu chuẩn riêng của công ty.

---

## 2. User Stories — 4 paths

Mỗi feature chính = 1 bảng. AI trả lời xong → chuyện gì xảy ra?

### Feature: CV-JD Matching & Ranking

**Trigger:** HR upload JD và batch CVs → AI phân tích từng CV → tính matching score (required skills 70% + preferred skills 20% + semantic similarity 10%) → xếp hạng candidates

| Path | Câu hỏi thiết kế | Mô tả |
|------|-------------------|-------|
| Happy — AI đúng, tự tin | User thấy gì? Flow kết thúc ra sao? | Top-3 candidates có matching score 70-85%, HR review summary và technical skills, thấy phù hợp, chọn để phỏng vấn |
| Low-confidence — AI không chắc | System báo "không chắc" bằng cách nào? User quyết thế nào? | Matching score 40-60%, UI hiển thị warning "Moderate Match", HR xem chi tiết gap analysis (missing skills, experience mismatch), quyết định có tiếp tục hay không |
| Failure — AI sai | User biết AI sai bằng cách nào? Recover ra sao? | AI cho điểm cao (75%) nhưng HR đọc CV thấy candidate thiếu required skill quan trọng → HR bỏ qua candidate này, chọn người khác trong danh sách ranked |
| Correction — user sửa | User sửa bằng cách nào? Data đó đi vào đâu? | HR điều chỉnh top-N slider (từ 3 lên 5) để xem thêm candidates, hoặc manually add candidate bị bỏ sót → hiện tại chưa log feedback, future: lưu vào training data |

### Feature: Deep Analysis & Interview Question Generation

**Trigger:** HR chọn top-N candidates → AI phân tích sâu điểm mạnh/yếu so với JD → generate câu hỏi phỏng vấn từ database nội bộ

| Path | Câu hỏi thiết kế | Mô tả |
|------|-------------------|-------|
| Happy — AI đúng, tự tin | User thấy gì? Flow kết thúc ra sao? | AI tạo 5 câu hỏi phỏng vấn: 2 câu về strengths (technical depth), 2 câu về weaknesses (gap probing), 1 câu culture fit. HR thấy phù hợp, copy vào interview script |
| Low-confidence — AI không chắc | System báo "không chắc" bằng cách nào? User quyết thế nào? | AI không tìm thấy câu hỏi phù hợp trong database → generate generic questions + note "Customize recommended". HR tự chỉnh sửa hoặc thêm câu hỏi mới |
| Failure — AI sai | User biết AI sai bằng cách nào? Recover ra sao? | Câu hỏi quá generic hoặc không liên quan đến weaknesses → HR thấy ngay khi review, xóa câu hỏi không phù hợp, giữ lại câu hay |
| Correction — user sửa | User sửa bằng cách nào? Data đó đi vào đâu? | HR edit câu hỏi trực tiếp trong UI hoặc thêm câu hỏi mới → hiện tại chưa save back to database, future: enriched question bank |

---

## 3. Eval metrics + threshold

**Optimize precision hay recall?** ☑ Precision · ☐ Recall
Tại sao? Trong tuyển dụng, false positive (chọn sai người) tốn cost phỏng vấn và onboarding. False negative (bỏ sót người tốt) ít nguy hiểm hơn vì HR vẫn có thể review manually. Ưu tiên precision để đảm bảo top-N candidates chất lượng cao.
Nếu sai ngược lại thì chuyện gì xảy ra? Nếu optimize recall → nhiều candidates không phù hợp vào top-N → HR mất thời gian review, giảm trust vào hệ thống → bỏ dùng

| Metric | Threshold | Red flag (dừng khi) |
|--------|-----------|---------------------|
| Matching accuracy (% top-3 có ≥1 người được chọn phỏng vấn) | ≥70% | <50% trong 2 tuần |
| Question relevance (% câu hỏi được giữ nguyên/chỉnh sửa nhẹ) | ≥60% | <40% trong 1 tuần |
| Time saved (giảm từ 2-3h xuống <30 phút/vị trí) | ≥75% reduction | <50% reduction |
| User satisfaction (HR rating 1-5 sau mỗi session) | ≥3.5/5 | <2.5/5 trong 1 tháng |

---

## 4. Top 3 failure modes

*Liệt kê cách product có thể fail — không phải list features.*
*"Failure mode nào user KHÔNG BIẾT bị sai? Đó là cái nguy hiểm nhất."*

| # | Trigger | Hậu quả | Mitigation |
|---|---------|---------|------------|
| 1 | CV chứa buzzwords nhiều nhưng thiếu experience thực tế (keyword stuffing) | AI cho matching score cao (75-80%) nhưng candidate không đủ năng lực → waste interview time | Thêm experience validation: check years_of_experience vs skill complexity, semantic analysis của project descriptions, không chỉ dựa keyword |
| 2 | JD và CV dùng terminology khác nhau cho cùng skill (VD: "ML" vs "Machine Learning", "AI" vs "Artificial Intelligence") | AI tính matching score thấp hơn thực tế → bỏ sót candidate tốt | Đã implement: skill normalization + synonym mapping trong utils.py (_SKILL_SYNONYMS), nhưng cần expand dictionary liên tục |
| 3 | AI hallucinate skills hoặc experience không có trong CV gốc | HR tin vào analysis sai → chọn candidate không phù hợp, phát hiện muộn trong phỏng vấn | Structured output với Pydantic validation, fallback parsing, và UI hiển thị raw CV text để HR cross-check. Future: add confidence score cho từng extracted field |

---

## 5. ROI 3 kịch bản

|   | Conservative | Realistic | Optimistic |
|---|-------------|-----------|------------|
| **Assumption** | 5 vị trí/tháng, 30 CVs/vị trí, 60% HR hài lòng | 15 vị trí/tháng, 40 CVs/vị trí, 75% HR hài lòng | 30 vị trí/tháng, 50 CVs/vị trí, 85% HR hài lòng |
| **Cost** | 150 CVs × $0.08 = $12/tháng (API) | 600 CVs × $0.08 = $48/tháng | 1500 CVs × $0.08 = $120/tháng |
| **Benefit** | Tiết kiệm 1.5h/vị trí × 5 = 7.5h/tháng (~$150 @ $20/h) | Tiết kiệm 2h/vị trí × 15 = 30h/tháng (~$600) | Tiết kiệm 2.5h/vị trí × 30 = 75h/tháng (~$1500) |
| **Net** | $150 - $12 = $138/tháng | $600 - $48 = $552/tháng | $1500 - $120 = $1380/tháng |

**Kill criteria:** 
- Cost > benefit trong 3 tháng liên tục
- User satisfaction <2.5/5 trong 2 tháng
- Matching accuracy <50% (HR không chọn ai trong top-3) trong 1 tháng
- Có alternative solution tốt hơn (VD: ATS built-in AI với cost thấp hơn)

---

## 6. Mini AI spec (1 trang)

**Product Overview:**
Smart CV-JD Matching là hệ thống AI hỗ trợ nhà tuyển dụng (HR/Recruiter) tự động hóa quy trình screening CV và chuẩn bị phỏng vấn. Thay vì đọc thủ công 50+ CVs và mất 2-3 giờ/vị trí, HR chỉ cần upload JD và batch CVs, hệ thống sẽ:
1. Phân tích CV và JD thành structured data (skills, experience, education)
2. Tính matching score dựa trên required skills (70%) + preferred skills (20%) + semantic similarity (10%)
3. Xếp hạng candidates và đề xuất top-N
4. Phân tích sâu điểm mạnh/yếu của từng candidate so với JD
5. Generate bộ câu hỏi phỏng vấn tùy chỉnh từ database nội bộ

**Target Users:**
- Primary: HR/Recruiters tại các công ty công nghệ, trường đại học (VinUni-VinSchool track)
- Secondary: Hiring managers cần quickly screen technical candidates

**AI Approach: Augmentation**
- AI đề xuất top-N candidates với matching score và analysis, nhưng HR có quyền quyết định cuối cùng
- Câu hỏi phỏng vấn được generate tự động nhưng HR có thể edit/add/remove
- Cost of reject thấp: HR chỉ cần skip candidate hoặc chỉnh sửa questions

**Quality Strategy: Precision over Recall**
- Ưu tiên precision để đảm bảo top-N candidates chất lượng cao, tránh waste interview time
- False negative (bỏ sót người tốt) ít nguy hiểm hơn vì HR vẫn có thể review manually
- Target: ≥70% matching accuracy (top-3 có ≥1 người được chọn phỏng vấn)

**Technical Architecture:**
- LLM Service: NVIDIA API (OpenAI-compatible) với structured output (Pydantic validation)
- 4 AI Agents:
  - CVAnalyzer: Extract structured data từ CV text
  - JDAnalyzer: Extract requirements từ JD text
  - CandidateDeepAnalyzer: So sánh CV vs JD, tìm strengths/weaknesses
  - InterviewQuestionGenerator: Generate câu hỏi từ database + context
- Matching Algorithm: Hybrid approach
  - Keyword matching: Skill normalization + synonym mapping + fuzzy coverage (Jaccard + SequenceMatcher)
  - Semantic matching: Hash embedding (local, no API cost) cho summary similarity
  - Weighted blending: Required skills 70%, Preferred skills 20%, Semantic 10%

**Key Risks & Mitigations:**
1. Keyword stuffing → Add experience validation, semantic analysis
2. Terminology mismatch → Skill synonym dictionary (expandable)
3. Hallucination → Structured output + Pydantic validation + UI shows raw CV for cross-check
4. Bias → Future: Blind mode (hide name, gender indicators), fairness metrics

**Data Flywheel (Future):**
- HR selections → Log chosen candidates → Fine-tune matching weights
- Edited questions → Enrich question database → Improve generation quality
- Domain-specific data (company's CV/JD patterns) → Marginal value over general LLM

**Cost & Latency:**
- ~$0.05-0.10/CV (NVIDIA API)
- 3-5s/CV analysis, 10-15s deep analysis + question generation
- Target: Process 50 CVs in <5 minutes

**Success Metrics:**
- Time saved: 75% reduction (từ 2-3h xuống <30 phút)
- Matching accuracy: ≥70%
- Question relevance: ≥60%
- User satisfaction: ≥3.5/5

**Deployment:**
- Streamlit UI cho demo/internal use
- Future: FastAPI backend + React frontend cho production
