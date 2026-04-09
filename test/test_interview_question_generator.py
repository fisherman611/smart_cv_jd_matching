import argparse
import json
import sys
from pathlib import Path

# Thêm project root vào sys.path để có thể import từ src
sys.path.append(str(Path(__file__).resolve().parents[1]))
from src.agents.interview_question_generator import InterviewQuestionGenerator

def main():
    parser = argparse.ArgumentParser(description="Batch test InterviewQuestionGenerator with Deep Analysis JSON files")
    parser.add_argument("--input-dir", default="data/deep_analysis_results", help="Folder chứa kết quả phân tích sâu (JSON)")
    parser.add_argument("--output-dir", default="data/interview_questions", help="Folder lưu bộ câu hỏi phỏng vấn (JSON)")
    parser.add_argument("--db-path", default="data/interview_question_db.json", help="Đường dẫn tới DB câu hỏi nội bộ")
    parser.add_argument("--pos", default="Giảng viên Khoa học Máy tính", help="Vị trí ứng tuyển mục tiêu")
    parser.add_argument("--pattern", default="*.json", help="Pattern file Deep analysis")
    args = parser.parse_args()

    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir)
    db_path = Path(args.db_path)

    if not input_dir.exists():
        print(f"[ERROR] Input folder không tồn tại: {input_dir}")
        sys.exit(1)
    
    if not db_path.exists():
        print(f"[ERROR] Database không tồn tại: {db_path}")
        sys.exit(1)

    deep_analysis_files = sorted(input_dir.glob(args.pattern))
    if not deep_analysis_files:
        print(f"[ERROR] Không tìm thấy file JSON nào trong {input_dir}")
        sys.exit(1)

    output_dir.mkdir(parents=True, exist_ok=True)
    generator = InterviewQuestionGenerator()

    ok = 0
    fail = 0

    print(f"[INFO] Bắt đầu tạo câu hỏi phỏng vấn từ kết quả Deep Analysis...")
    print(f"[INFO] Vị trí mục tiêu: {args.pos}")

    for file in deep_analysis_files:
        try:
            # Load kết quả phân tích sâu
            deep_data = json.loads(file.read_text(encoding="utf-8"))
            
            # Lấy điểm mạnh/điểm yếu từ file deep analysis
            strengths = deep_data.get("strengths", "")
            weaknesses = deep_data.get("weaknesses", "")

            # Gọi generator
            result = generator.generate_questions(
                target_position=args.pos,
                strengths=strengths,
                weaknesses=weaknesses,
                db_path=str(db_path)
            )

            # Lưu kết quả
            out_file = output_dir / f"interview_{file.name}"
            out_file.write_text(
                json.dumps(result, ensure_ascii=False, indent=2),
                encoding="utf-8"
            )

            print(f"[OK] {file.name} -> {out_file.name}")
            ok += 1
        except Exception as e:
            print(f"[FAIL] {file.name}: {e}")
            fail += 1

    print("\n===== SUMMARY =====")
    print(f"Success: {ok}")
    print(f"Failed : {fail}")
    print(f"Output : {output_dir}")

if __name__ == "__main__":
    main()
