# generate_ai_description.py

import os
import time
import argparse
import re

import pandas as pd
from openai import OpenAI

def generate_ai_description(client: OpenAI, subject_name: str) -> str:
    prompt = (
        "다음 과목에 대해서\n"
        "3문장 이내의 간결한 설명을 작성해주세요.\n"
        f"- 과목명: {subject_name}"
    )
    resp = client.chat.completions.create(
        model="gpt-4o-mini",            # gpt-3.5-turbo 로 바꿀 수도 있습니다
        messages=[{"role": "user", "content": prompt}],
        max_tokens=150
    )
    return resp.choices[0].message.content.strip()

def clean_desc(raw: str) -> str:
    text = re.sub(r"\*\*.*?\*\*", "", raw)                    # 마크다운 헤더 제거
    return re.sub(r"\n{2,}", "\n", text.strip())               # 과도한 개행 정리

def main():
    parser = argparse.ArgumentParser(
        description="CSV의 일부 행(과목)에 AI 설명을 추가하고, 결과를 CSV/JSON으로 출력합니다."
    )
    parser.add_argument("--input_csv",
                        default="computer_lectures_2025_1.csv",
                        help="원본 CSV 파일 경로")
    parser.add_argument("--pause_sec", type=float, default=1.0,
                        help="OpenAI 호출 간 대기 시간(초)")
    parser.add_argument("--start_idx", type=int, default=0,
                        help="처리 시작 인덱스 (0부터)")
    parser.add_argument("--end_idx", type=int, default=None,
                        help="처리 끝 인덱스 (exclusive)")
    args = parser.parse_args()

    # 1) OpenAI 클라이언트
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("환경 변수 OPENAI_API_KEY 가 설정되지 않았습니다.")
    client = OpenAI(api_key=api_key)

    # 2) 원본 CSV 로드
    df = pd.read_csv(args.input_csv, encoding="utf-8-sig")
    total = len(df)
    start = args.start_idx
    end = args.end_idx if args.end_idx is not None else total
    df_slice = df.iloc[start:end]

    # 3) ai_description 컬럼 준비
    if "ai_description" not in df_slice.columns:
        df_slice["ai_description"] = ""

    chunk_len = len(df_slice)
    print(f"▶ [{start}:{end}] 총 {chunk_len}개 과목 처리 시작 (전체 {total}개 중)")

    # 4) 실제 처리
    descriptions = []
    for i, (_, row) in enumerate(df_slice.iterrows(), start=1):
        title = row["title"]
        abs_idx = start + i - 1
        print(f"  - [{abs_idx+1}/{total}] {title} 처리 중…", end="", flush=True)

        # 스킵 로직(이미 값이 있으면)
        if pd.notna(row.get("ai_description")) and row["ai_description"].strip():
            descriptions.append(row["ai_description"])
            print(" 스킵")
            continue

        raw = generate_ai_description(client, title)
        desc = clean_desc(raw)
        descriptions.append(desc)
        print(" 완료")
        time.sleep(args.pause_sec)

    df_slice["ai_description"] = descriptions

    # 5) 저장 (범위를 파일명에 포함)
    base, _ = os.path.splitext(os.path.basename(args.input_csv))
    out_csv  = f"{base}_{start}_{end}_with_desc.csv"
    out_json = f"{base}_{start}_{end}_with_desc.json"

    df_slice.to_csv(out_csv, index=False, encoding="utf-8-sig")
    df_slice.to_json(out_json, orient="records", force_ascii=False, indent=2)
    print(f"✅ 완료: {out_csv}, {out_json}")

if __name__ == "__main__":
    main()
