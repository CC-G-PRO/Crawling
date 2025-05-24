# prepare_lectures_df.py

import pandas as pd

def main():
    # 1) 원본 CSV 불러오기
    df = pd.read_csv("computer_lectures_2025_1_full_with_desc.csv", encoding="utf-8-sig")

    # 2) 칼럼명 변경
    df = df.rename(columns={
        "course_no":   "lecture_code",
        "title":       "subject_name",
        "professor":   "professor_name",
        "time_place":  "lecture_place"
    })

    # 3) RDS 테이블 스키마에 맞춰 칼럼 추리기
    cols_to_keep = [
        "lecture_year",
        "semester",
        "professor_name",
        "subject_name",
        "lecture_code",
        "lecture_place",
        "capacity",
        "language",
        "is_english",
        "note",
        "syllabus_url",
        "ai_description"
    ]
    df = df[cols_to_keep]

    # 4) 전처리된 CSV/JSON으로 저장
    df.to_csv("lectures_prepared.csv", index=False, encoding="utf-8-sig")
    df.to_json("lectures_prepared.json", orient="records", force_ascii=False, indent=2)
    print("✅ 칼럼 정리 완료: lectures_prepared.(csv|json) 생성됨")

if __name__ == "__main__":
    main()
