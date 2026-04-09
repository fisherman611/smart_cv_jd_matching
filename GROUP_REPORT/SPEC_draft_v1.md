# SPEC — AI Product Hackathon

**Nhóm:** ___  
**Track:** ☐ VinFast · ☐ Vinmec · ☐ VinUni-VinSchool · ☐ XanhSM · ☑ Open  
**Problem statement (1 câu):** *Recruiter mất nhiều thời gian đọc CV và khó đánh giá mức độ phù hợp với JD; hiện lọc theo keyword dễ sai và thiếu giải thích; AI giúp hiểu semantic CV/JD, xếp hạng minh bạch và sinh câu hỏi phỏng vấn.*

---

## 1. AI Product Canvas


|             | Value                                                                                                                                                              | Trust                                                                                                                                                                                          | Feasibility                                                                                                                                                                                                                                              |
| ----------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Câu hỏi** | User nào? Pain gì? AI giải gì?                                                                                                                                     | Khi AI sai thì sao? User sửa bằng cách nào?                                                                                                                                                    | Cost/latency bao nhiêu? Risk chính?                                                                                                                                                                                                                      |
| **Trả lời** | *Recruiter/HR phải đọc nhiều CV và match với JD → tốn thời gian, lọc keyword sai lệch; AI parse CV + hiểu JD + match/rank + giải thích + gợi ý câu hỏi phỏng vấn.* | *AI match sai / lý do giải thích không đúng → user xem reasoning + skill gaps, chỉnh sửa/override score, đánh dấu “fit/not fit”, thêm/loại skills; hệ thống ghi nhận correction để cải thiện.* | *POC Option A/B (khuyến nghị A: prompt-based + embeddings); latency mục tiêu < 10–20s cho 1 batch nhỏ CV; risk: hallucination khi extract CV/JD, bias/keyword overfit, parsing PDF lỗi; giảm rủi ro bằng schema output + critic agent + fallback rules.* |


**Automation hay augmentation?** ☐ Automation · ☑ Augmentation  
Justify: *Augmentation — AI đề xuất shortlist/score/reasoning, recruiter quyết định cuối; reject/override rẻ và tạo learning signal.*

**Learning signal:**

1. User correction đi vào đâu? *Log sự kiện: chỉnh score, accept/reject candidate, edit skills/must-have, đánh dấu reason “không đúng”, chọn câu hỏi phỏng vấn nào dùng.*
2. Product thu signal gì để biết tốt lên hay tệ đi? *Tỉ lệ accept shortlist, thời gian lọc giảm, tỉ lệ “reasoning helpful”, tỉ lệ override score, tỉ lệ candidate qua vòng phỏng vấn (proxy), feedback chất lượng câu hỏi.*
3. Data thuộc loại nào? ☐ User-specific · ☐ Domain-specific · ☐ Real-time · ☐ Human-judgment · ☐ Khác: ___
  Có marginal value không? (Model đã biết cái này chưa?) *Có — judgment của recruiter theo từng role/domain và tiêu chuẩn nội bộ thường không có trong dữ liệu công khai.*

---

## 2. User Stories — 4 paths

Mỗi feature chính = 1 bảng. AI trả lời xong → chuyện gì xảy ra?

### Feature: *CV–JD matching & ranking + explainability*

**Trigger:** *Recruiter upload JD + upload nhiều CV → system parse → match/rank → hiển thị shortlist + reasoning + gaps.*


| Path                           | Câu hỏi thiết kế                                           | Mô tả                                                                                                                                                                                              |
| ------------------------------ | ---------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Happy — AI đúng, tự tin        | User thấy gì? Flow kết thúc ra sao?                        | *Dashboard hiển thị Top N ứng viên kèm score, strengths, skill gaps; recruiter nhanh chóng shortlist và xuất kết quả.*                                                                             |
| Low-confidence — AI không chắc | System báo "không chắc" bằng cách nào? User quyết thế nào? | *Score kèm “low confidence” (vd: thiếu evidence trong CV, parsing uncertain); UI yêu cầu xác nhận: “thiếu skill X có đúng không?”; recruiter bổ sung/override.*                                    |
| Failure — AI sai               | User biết AI sai bằng cách nào? Recover ra sao?            | *Ứng viên bị xếp hạng cao vì keyword nhưng thiếu context; critic/consistency check gắn cờ “inconsistent reasoning”; recruiter mở candidate detail, thấy mismatch và hạ score/loại khỏi shortlist.* |
| Correction — user sửa          | User sửa bằng cách nào? Data đó đi vào đâu?                | *Recruiter chỉnh must-have/nice-to-have, sửa skill extraction, override score, đánh dấu “fit/not fit” + lý do; hệ thống lưu correction logs để tune weights/prompt và đánh giá chất lượng.*        |


### Feature: *Interview question generation (text)*

**Trigger:** *Recruiter chọn 1 ứng viên trong shortlist → system dùng JD + CV + skill gaps để sinh câu hỏi phỏng vấn.*


| Path                           | Câu hỏi thiết kế                                           | Mô tả                                                                                                                                                          |
| ------------------------------ | ---------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Happy — AI đúng, tự tin        | User thấy gì? Flow kết thúc ra sao?                        | *Sinh 3–5 câu technical + 2 behavioral, có mapping tới gaps/requirements; recruiter chọn câu hỏi và dùng trong buổi phỏng vấn.*                                |
| Low-confidence — AI không chắc | System báo "không chắc" bằng cách nào? User quyết thế nào? | *Một số câu hỏi có tag “need context” (vd: CV thiếu chi tiết dự án); system gợi ý câu hỏi làm rõ; recruiter chỉnh prompt nhanh hoặc chọn template.*            |
| Failure — AI sai               | User biết AI sai bằng cách nào? Recover ra sao?            | *Câu hỏi quá chung chung / không liên quan JD; UI cho phép “regenerate with constraints” (role level, tech focus) và chặn câu hỏi không phù hợp (guardrails).* |
| Correction — user sửa          | User sửa bằng cách nào? Data đó đi vào đâu?                | *Recruiter edit câu hỏi, pin câu hỏi tốt, đánh giá 1–5; logs dùng để cải thiện prompt và rubric đánh giá relevance.*                                           |


---

## 3. Eval metrics + threshold

**Optimize precision hay recall?** ☐ Precision · ☐ Recall  
Tại sao? *Ưu tiên precision cho shortlist: false positive làm recruiter tốn thời gian phỏng vấn/đánh giá sai; vẫn cần recall đủ để không bỏ lỡ ứng viên tốt, nhưng có thể tăng dần sau.*  
Nếu sai ngược lại thì chuyện gì xảy ra? *Nếu quá ưu tiên recall → shortlist dài, recruiter vẫn phải đọc nhiều; nếu quá ưu tiên precision → bỏ lỡ ứng viên phù hợp, giảm trust và adoption.*


| Metric                                                  | Threshold    | Red flag (dừng khi)                  |
| ------------------------------------------------------- | ------------ | ------------------------------------ |
| *Precision@K (K=10) theo đánh giá recruiter “fit”*      | *≥ 0.7*      | *< 0.5 trong 2 phiên demo liên tiếp* |
| *Avg time-to-shortlist (so với baseline)*               | *giảm ≥ 50%* | *giảm < 20%*                         |
| *Explanation helpful rate (% recruiter chọn “helpful”)* | *≥ 70%*      | *< 40%*                              |
| *Override rate (% chỉnh score vì “reasoning sai”)*      | *≤ 25%*      | *> 40%*                              |


---

## 4. Top 3 failure modes

*Liệt kê cách product có thể fail — không phải list features.*  
*"Failure mode nào user KHÔNG BIẾT bị sai? Đó là cái nguy hiểm nhất."*


| #   | Trigger                                                                                     | Hậu quả                                                          | Mitigation                                                                                                                         |
| --- | ------------------------------------------------------------------------------------------- | ---------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| 1   | *CV PDF parse lỗi (mất dòng, sai layout) → skill/experience bị thiếu mà user không nhận ra* | *Ứng viên phù hợp bị xếp thấp; trust giảm khi phát hiện muộn*    | *Hiển thị “extraction confidence”, highlight evidence spans, cho phép upload text/alternative parse, fallback OCR/another parser.* |
| 2   | *Keyword overfit: match cao vì từ khóa nhưng thiếu context thực tế*                         | *Shortlist sai, tốn thời gian phỏng vấn*                         | *Weighted scoring + rule checks (must-have), critic agent kiểm tra consistency giữa score và evidence; yêu cầu dẫn chứng từ CV.*   |
| 3   | *Bias theo trường/địa điểm/keyword nhạy cảm hoặc suy luận seniority sai*                    | *Đánh giá không công bằng, rủi ro đạo đức và sản phẩm bị reject* | *Bias detection prompt, loại bỏ/ẩn thuộc tính nhạy cảm khỏi scoring, audit logs, allow reviewer override + explain constraints.*   |


---

## 5. ROI 3 kịch bản


|                | Conservative                                            | Realistic                                          | Optimistic                                                        |
| -------------- | ------------------------------------------------------- | -------------------------------------------------- | ----------------------------------------------------------------- |
| **Assumption** | *10 JD/ngày, 20 CV/JD, 50% recruiter dùng thường xuyên* | *30 JD/ngày, 40 CV/JD, 70% dùng thường xuyên*      | *100 JD/ngày, 60 CV/JD, 85% dùng thường xuyên*                    |
| **Cost**       | *API/compute ~$10/ngày (POC, batch nhỏ)*                | *~$50/ngày*                                        | *~$150/ngày*                                                      |
| **Benefit**    | *Giảm 30–60 phút/JD để shortlist*                       | *Giảm 1–2h/JD, tăng tốc time-to-interview*         | *Giảm 2–3h/JD + tăng chất lượng shortlist, giảm churn tuyển dụng* |
| **Net**        | *Positive nếu tiết kiệm ≥ 1–2h/ngày tổng*               | *Positive rõ rệt nếu tiết kiệm ≥ 10–20h/ngày tổng* | *Rất lớn nếu scale + giảm chi phí sai người*                      |


**Kill criteria:** *Nếu recruiter không tin/không dùng (precision@K < 0.5 hoặc explanation helpful < 40%) trong 2 vòng demo/tuần thử nghiệm, hoặc cost tăng mà time-to-shortlist không giảm đáng kể.*

---

## 6. Mini AI spec (1 trang)

Product hỗ trợ recruiter lọc CV và đánh giá mức độ phù hợp với Job Description nhanh và minh bạch hơn. User upload JD và nhiều CV, hệ thống dùng pipeline multi-agent để: (1) phân tích JD (must-have/nice-to-have, seniority, domain), (2) phân tích CV (skills, kinh nghiệm, dự án, tech stack), (3) matching & ranking dựa trên semantic similarity (embeddings) kết hợp rule-based scoring và weighted aggregation, (4) cung cấp explainability (reasoning + evidence + skill gaps), (5) dùng critic agent để kiểm tra inconsistency/bias và refine kết quả, và (6) sinh bộ câu hỏi phỏng vấn dựa trên JD + CV + gaps.

Hệ thống theo hướng **augmentation**: AI đề xuất shortlist/score/câu hỏi, recruiter quyết định và có quyền override. Quality ưu tiên **precision cho shortlist** (giảm false positives), đo bằng Precision@K, thời gian tạo shortlist, và mức độ hữu ích của explanation. Risk chính gồm lỗi parse PDF dẫn đến thiếu thông tin, keyword overfit gây match sai, và bias. Mitigation: schema-based structured outputs, hiển thị confidence + evidence, critic agent verify reasoning, guardrails và cơ chế sửa/override rõ ràng.

Data flywheel đến từ hành vi recruiter: accept/reject shortlist, override score, chỉnh must-have/nice-to-have, feedback explanation và câu hỏi phỏng vấn. Các signal này dùng để tinh chỉnh weights, prompts, và threshold confidence theo domain/role.

Kiến trúc đề xuất: API layer (FastAPI/Flask) + orchestrator (LangGraph/CrewAI) điều phối các agent (JD Agent, CV Agent, Match Agent, Critic Agent, Interview Generator). Embeddings dùng OpenAI/SentenceTransformers; vector similarity bằng cosine (FAISS/Chroma). Storage dùng PostgreSQL cho metadata/logs và S3/local cho file CV.