import os
import glob
import re
import pdfplumber
import pandas as pd
import json
from pathlib import Path

# 이수구분(type) 매핑 테이블
type_map = {
    "전공필수": "04",
    "전공선택": "05",
    "전공기초": "11",
}

def parse_one_curriculum(pdf_path):
    rows = []
    with pdfplumber.open(pdf_path) as pdf:
        # 1) 교육과정 편성표 시작 페이지 찾기
        start_page = None
        for i, page in enumerate(pdf.pages):
            text = page.extract_text() or ""
            if "컴퓨터공학과 교육과정 편성표" in text:
                start_page = i
                break
        # 2) 못 찾으면 과목 코드 패턴으로 대체
        if start_page is None:
            for i, page in enumerate(pdf.pages):
                text = page.extract_text() or ""
                if re.search(r"\bCSE\d{3}\b", text):
                    start_page = i
                    break
        if start_page is None:
            raise RuntimeError(f"{os.path.basename(pdf_path)}: 편성표 시작 페이지를 찾을 수 없습니다.")

        current_type = ""
        # 3) 최대 3페이지에 걸쳐 표 추출
        for p in range(start_page, min(start_page + 3, len(pdf.pages))):
            tables = pdf.pages[p].extract_tables()
            for table in tables:
                if len(table) < 2:
                    continue
                header = table[0]
                cols = [(h or "").replace("\n", "").strip() for h in header]
                try:
                    idx_type   = cols.index("이수구분")
                    idx_name   = cols.index("교과목명")
                    idx_code   = cols.index("학수번호")
                    idx_credit = cols.index("학점")
                    idx_grade  = cols.index("이수학년")
                except ValueError:
                    continue

                for row in table[1:]:
                    if len(row) <= max(idx_type, idx_code, idx_grade):
                        continue
                    raw_type = (row[idx_type] or "").strip()
                    if raw_type:
                        current_type = raw_type
                    subject_code = (row[idx_code] or "").strip()
                    if not subject_code:
                        continue
                    rows.append({
                        "type": current_type,
                        "subject_code": subject_code,
                        "subject_name": (row[idx_name] or "").strip(),
                        "credit": (row[idx_credit] or "").strip(),
                        "target_grade": (row[idx_grade] or "").strip(),
                    })
    return rows


def main():
    base_dir = Path(__file__).parent.resolve()
    print(f"Script directory: {base_dir}")

    # PDF 파일 검색
    pattern = "[0-9][0-9][0-9][0-9]*교육과정.pdf"
    pdf_files = sorted(base_dir.glob(pattern))
    print(f"Using pattern '{pattern}', found {len(pdf_files)} file(s):")
    for f in pdf_files:
        print(f" - {f.name}")
    if not pdf_files:
        print("⚠️ No PDF files found. 패턴과 디렉토리를 확인하세요.")
        return

    # 각 PDF 파싱 및 파일 저장
    for pdf_path in pdf_files:
        year = pdf_path.stem.split()[0]
        try:
            rows = parse_one_curriculum(pdf_path)
        except Exception as e:
            print(f"❌ {year} 파싱 실패: {e}")
            continue

        # type_number 매핑 및 subject_year 추가
        for r in rows:
            raw_type = r.pop('type', '')
            clean_type = raw_type.replace("\n", "").strip()
            r['type_number'] = type_map.get(clean_type, "")
            r['subject_year'] = year

        df = pd.DataFrame(rows)
        csv_path = base_dir / f"computer_curriculum_{year}.csv"
        df.to_csv(csv_path, index=False, encoding="utf-8-sig")

        filtered = [r for r in rows if r['subject_code']]
        json_path = base_dir / f"computer_curriculum_{year}.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(filtered, f, ensure_ascii=False, indent=2)
        
        print(f"✅ {year} 저장 완료: {len(df)}건 → {csv_path.name}, {json_path.name}")

if __name__ == "__main__":
    main()