import argparse
import json
import sys
from pathlib import Path

# Thêm project root vào sys.path để có thể import từ src
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.agents.jd_analyzer import JDAnalyzer
from src.engine.llm_service import LLMService

def main():
    parser = argparse.ArgumentParser(description="Batch test JDAnalyzer with JD text files")
    parser.add_argument("--input-dir", default="data/jds", help="Folder chứa JD .txt")
    parser.add_argument("--output-dir", default="data/jd_analysis_results", help="Folder lưu JSON kết quả")
    parser.add_argument("--pattern", default="*.txt", help="Pattern file JD")
    args = parser.parse_args()

    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir)

    if not input_dir.exists():
        print(f"[ERROR] Input folder không tồn tại: {input_dir}")
        sys.exit(1)

    jd_files = sorted(input_dir.glob(args.pattern))
    if not jd_files:
        print(f"[ERROR] Không tìm thấy file nào theo pattern {args.pattern} trong {input_dir}")
        sys.exit(1)

    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Khởi tạo analyzer (LLMService sẽ lấy config từ .env)
    analyzer = JDAnalyzer()

    ok = 0
    fail = 0

    print(f"[INFO] Tổng số JD: {len(jd_files)}")
    for jd_file in jd_files:
        try:
            jd_text = jd_file.read_text(encoding="utf-8")
            result = analyzer.analyze(jd_text)

            out_file = output_dir / f"{jd_file.stem}.json"
            out_file.write_text(
                json.dumps(result, ensure_ascii=False, indent=2),
                encoding="utf-8"
            )

            print(f"[OK] {jd_file.name} -> {out_file}")
            ok += 1
        except Exception as e:
            print(f"[FAIL] {jd_file.name}: {e}")
            fail += 1

    print("\n===== SUMMARY =====")
    print(f"Success: {ok}")
    print(f"Failed : {fail}")
    print(f"Output : {output_dir}")

if __name__ == "__main__":
    main()
