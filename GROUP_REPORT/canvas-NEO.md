# AI Product Canvas — Chatbot NEO (Vietnam Airlines)

---

## Canvas

|   | Value | Trust | Feasibility |
|---|-------|-------|-------------|
| **Câu hỏi guide** | User nào? Pain gì? AI giải quyết gì mà cách hiện tại không giải được? | Khi AI sai thì user bị ảnh hưởng thế nào? User biết AI sai bằng cách nào? User sửa bằng cách nào? | Cost bao nhiêu/request? Latency bao lâu? Risk chính là gì? |
| **Trả lời** | **User**: Hành khách Vietnam Airlines (đang cân nhắc mua vé / đã mua vé / chuẩn bị bay) cần tra cứu nhanh thông tin chuyến bay, vé, hành lý, thủ tục.<br><br>**Pain**: Tìm thông tin rải rác trên web/app, gọi tổng đài chờ lâu; câu hỏi lặp lại (hành lý, hoàn/đổi, giấy tờ) cần câu trả lời “đúng & nhanh”.<br><br>**AI (NEO)**: Trả lời FAQ 24/7; hướng dẫn từng bước + dẫn nguồn; tra cứu đặt chỗ khi user cung cấp mã đặt chỗ + email; gợi ý ưu đãi/khuyến mãi (cần cập nhật theo thời gian).<br><br>**Value**: Giảm thời gian tự tìm/đợi tổng đài, tăng self‑service, giảm tải CS; tăng chuyển đổi mua vé khi user hỏi lịch bay/ưu đãi/thanh toán. | **Ảnh hưởng tới User khi AI sai**: User có thể chuẩn bị sai giấy tờ/hành lý (phát sinh phí, bị từ chối vận chuyển), hiểu sai điều kiện hoàn/đổi (mất tiền/thời gian), hoặc bỏ lỡ chuyến do hiểu sai giờ/điểm làm thủ tục.<br><br>**User biết AI sai khi**: Đối chiếu với “Manage booking” trên app/web, email xác nhận đặt chỗ, trang chính sách/FAQ chính thức; thấy thông tin khuyến mãi đã hết hạn.<br><br>**Hướng giải quyết**: Luôn kèm link nguồn chính thức; với câu hỏi rủi ro cao yêu cầu user xác nhận bối cảnh (đường bay, hạng vé, hành lý…); nếu không chắc → nói rõ “chưa chắc”, chuyển người dùng sang kênh hỗ trợ/CSKH hoặc trang tra cứu chính thức; cho phép user báo “thông tin sai/đã hết hạn”. | **Cost**: ~\$0.01–\$0.05/turn (tùy model + RAG; có thể giảm bằng model nhỏ cho FAQ, chỉ dùng model lớn khi cần).<br><br>**Latency**: ~2–6 giây (tăng nếu gọi API tra cứu đặt chỗ / flight status).<br><br>**Risk chính**: Nội dung soạn sẵn bị lỗi thời (ưu đãi hết hạn, policy đổi); hallucination nếu thiếu grounding; rò rỉ/thu thập PII (mã đặt chỗ, email); tích hợp sai với hệ thống đặt chỗ/flight status; đa ngôn ngữ & thuật ngữ hàng không gây hiểu nhầm.

---

## Automation hay augmentation?

☐ Automation — AI làm thay, user không can thiệp  
☑ Augmentation — AI gợi ý, user quyết định cuối cùng

**Justify:** **Augmentation (chính)** — vì nhiều câu trả lời có rủi ro cao nếu sai (hành lý/hoàn‑đổi/giấy tờ). NEO nên **gợi ý + dẫn nguồn** và yêu cầu xác nhận khi thông tin phụ thuộc bối cảnh. Automation chỉ nên áp dụng cho tra cứu “read‑only” (ví dụ: trạng thái chuyến bay/đặt chỗ) khi user đã cung cấp định danh và kết quả lấy trực tiếp từ API.

---

## Learning signal

| # | Câu hỏi | Trả lời |
|---|---------|---------|
| 1 | User correction đi vào đâu? | Nút feedback + form “thông tin sai/hết hạn”; log hội thoại gắn nhãn intent (hành lý/hoàn‑đổi/đặt chỗ…); ticket nội bộ để cập nhật KB/CMS và rule routing (khi cần chuyển CSKH). |
| 2 | Product thu signal gì để biết tốt lên hay tệ đi? | Tỉ lệ giải quyết không cần chuyển CSKH (deflection), CSAT sau phiên chat, tỉ lệ “đưa link đúng và user click”, tỉ lệ user hỏi lại cùng câu (repeat‑question), số báo cáo “sai/hết hạn”, latency, và tỉ lệ fallback “không chắc”. |
| 3 | Data thuộc loại nào? ☐ User-specific · ☐ Domain-specific · ☐ Real-time · ☐ Human-judgment · ☐ Khác: ___ | ☑ User-specific (PNR/email, hành trình) · ☑ Domain-specific (policy, thuật ngữ) · ☑ Real-time (giờ bay/trạng thái) · ☑ Human-judgment (feedback đúng/sai, CSAT) |

**Có marginal value không?** (Model đã biết cái này chưa? Ai khác cũng thu được data này không?)

Có. Model nền thường **không cập nhật kịp** ưu đãi/chính sách theo thời gian và không hiểu hết **ngữ cảnh địa phương/tiếng Việt** (cách hỏi, viết tắt). Signal từ hội thoại + feedback giúp phát hiện nội dung lỗi thời, intent mới, và điểm “đau” thực tế (ví dụ: user hay hỏi giá rẻ nhất nhưng hiện chưa đáp ứng), là dữ liệu gắn với Vietnam Airlines nên bên ngoài khó thu được.

