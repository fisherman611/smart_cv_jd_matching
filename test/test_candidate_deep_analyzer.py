import argparse
import json
import sys
from pathlib import Path

# Thêm project root vào sys.path để có thể import từ src
sys.path.append(str(Path(__file__).resolve().parents[1]))
from src.agents.candidate_deep_analyzer import CandidateDeepAnalyzer

def main():
    parser = argparse.ArgumentParser(description="Batch test CandidateDeepAnalyzer with analyzed CV and JD JSON files")
    parser.add_argument("--cv-dir", default="data/cv_analysis_results", help="Folder chứa kết quả phân tích CV (JSON)")
    parser.add_argument("--jd-file", default="data/jd_analysis_results/jd_ai_01.json", help="File phân tích JD mục tiêu (JSON)")
    parser.add_argument("--output-dir", default="data/deep_analysis_results", help="Folder lưu kết quả đối chiếu sâu")
    parser.add_argument("--pattern", default="*.json", help="Pattern file CV analysis")
    args = parser.parse_args()

    cv_dir = Path(args.cv_dir)
    jd_file_path = Path(args.jd_file)
    output_dir = Path(args.output_dir)

    # Kiểm tra tồn tại
    if not cv_dir.exists():
        print(f"[ERROR] Thư mục CV không tồn tại: {cv_dir}")
        sys.exit(1)
    
    if not jd_file_path.exists():
        print(f"[ERROR] File JD không tồn tại: {jd_file_path}")
        sys.exit(1)

    cv_analysis_files = sorted(cv_dir.glob(args.pattern))
    if not cv_analysis_files:
        print(f"[ERROR] Không tìm thấy file JSON nào trong {cv_dir}")
        sys.exit(1)

    # Load dữ liệu JD (dùng chung cho mọi CV trong batch này)
    jd_analysis = json.loads(jd_file_path.read_text(encoding="utf-8"))

    output_dir.mkdir(parents=True, exist_ok=True)
    analyzer = CandidateDeepAnalyzer()

    ok = 0
    fail = 0

    print(f"[INFO] Bắt đầu phân tích sâu cho {len(cv_analysis_files)} ứng viên...")
    print(f"[INFO] Đối chiếu với JD: {jd_file_path.name}")

    for cv_file in cv_analysis_files:
        try:
            # Load dữ liệu CV
            cv_analysis = json.loads(cv_file.read_text(encoding="utf-8"))
            
            # Thực hiện phân tích sâu
            result = analyzer.analyze(cv_analysis, jd_analysis)

            # Lưu kết quả
            out_file = output_dir / f"deep_{cv_file.name}"
            out_file.write_text(
                json.dumps(result, ensure_ascii=False, indent=2),
                encoding="utf-8"
            )

            print(f"[OK] {cv_file.name} -> {out_file.name}")
            ok += 1
        except Exception as e:
            print(f"[FAIL] {cv_file.name}: {e}")
            fail += 1

    print("\n===== SUMMARY =====")
    print(f"Success: {ok}")
    print(f"Failed : {fail}")
    print(f"Output : {output_dir}")

if __name__ == "__main__":
    main()
