import os
import glob
import re
import pdfplumber
import pandas as pd
import json

def parse_one_curriculum(pdf_path):
    rows = []
    with pdfplumber.open(pdf_path) as pdf:
        # 1) 우선 헤더 문구로 찾되
        start_page = None
        for i, page in enumerate(pdf.pages):
            text = page.extract_text() or ""
            if "컴퓨터공학과 교육과정 편성표" in text:
                start_page = i
                break

        # 2) 못 찾으면, CSExxx 과목코드 패턴으로 대체 탐색
        if start_page is None:
            for i, page in enumerate(pdf.pages):
                text = page.extract_text() or ""
                if re.search(r"\bCSE\d{3}\b", text):
                    start_page = i
                    break

        if start_page is None:
            raise RuntimeError(f"{os.path.basename(pdf_path)}: 편성표 시작 페이지를 찾을 수 없습니다.")

        current_type = ""
        # 3) 편성표가 걸친 3페이지
        for p in range(start_page, start_page + 3):
            if p >= len(pdf.pages): break
            tables = pdf.pages[p].extract_tables()
            for table in tables:
                if len(table) < 2: continue

                header = table[0]
                cols = [(h or "").replace("\n","").strip() for h in header]
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
                    type_ = current_type

                    subject_code = (row[idx_code] or "").strip()
                    if not subject_code:
                        continue

                    rows.append({
                        "type":          type_,
                        "subject_code":  subject_code,
                        "subject_name":  (row[idx_name] or "").strip(),
                        "credit":        (row[idx_credit] or "").strip(),
                        "target_grade":  (row[idx_grade] or "").strip(),
                    })

    return rows

def main():
    pdf_files = sorted(glob.glob("[0-9][0-9][0-9][0-9]*교육과정.pdf"))
    for pdf_path in pdf_files:
        year = os.path.basename(pdf_path).split()[0]
        try:
            rows = parse_one_curriculum(pdf_path)
        except Exception as e:
            print(f"❌ {year} 파싱 실패: {e}")
            continue

        df = pd.DataFrame(rows)
        csv_name = f"computer_curriculum_{year}.csv"
        df.to_csv(csv_name, index=False, encoding="utf-8-sig")

        filtered = [r for r in rows if r["subject_code"]]
        json_name = f"computer_curriculum_{year}.json"
        with open(json_name, "w", encoding="utf-8") as f:
            json.dump(filtered, f, ensure_ascii=False, indent=2)

        print(f"✅ {year} 저장 완료: {len(df)}건 → {csv_name}, {json_name}")

if __name__ == "__main__":
    main()
