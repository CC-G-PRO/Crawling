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
        model="gpt-4o-mini",            # 또는 "gpt-3.5-turbo"
        messages=[{"role": "user", "content": prompt}],
        max_tokens=150
    )
    return resp.choices[0].message.content.strip()

def clean_desc(raw: str) -> str:
    # 1) 불필요한 마크다운(헤더 등) 제거
    text = re.sub(r"\*\*.*?\*\*", "", raw)
    # 2) 과도한 개행(2줄 이상) → 한 줄 개행으로 정리
    return re.sub(r"\n{2,}", "\n", text.strip())

def main():
    parser = argparse.ArgumentParser(
        description="기본 CSV에 AI 설명을 추가하고, 결과를 CSV/JSON으로 출력합니다."
    )
    parser.add_argument(
        "--input_csv",
        default="computer_lectures_2025_1.csv",
        help="크롤러가 생성한 기본 CSV 파일 경로"
    )
    parser.add_argument(
        "--pause_sec",
        type=float,
        default=1.0,
        help="OpenAI 호출 간 대기 시간(초)"
    )
    args = parser.parse_args()

    # 1) OpenAI 클라이언트 초기화
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("환경 변수 OPENAI_API_KEY 가 설정되지 않았습니다.")
    client = OpenAI(api_key=api_key)

    # 2) CSV 로드 및 컬럼 준비
    df = pd.read_csv(args.input_csv, encoding="utf-8-sig")
    if "ai_description" not in df.columns:
        df["ai_description"] = ""

    total = len(df)
    print(f"▶ 시작: 총 {total}개 과목에 대해 설명 생성")

    # 3) 전체 과목 순회하며 설명 생성
    descriptions = []
    for idx, row in df.iterrows():
        title = row["title"]
        print(f"  - [{idx+1}/{total}] {title} 처리 중…", end="", flush=True)

        if row["ai_description"]:
            descriptions.append(row["ai_description"])
            print(" 스킵")
            continue

        raw = generate_ai_description(client, title)
        desc = clean_desc(raw)
        descriptions.append(desc)

        print(" 완료")
        time.sleep(args.pause_sec)

    df["ai_description"] = descriptions

    # 4) 결과 저장
    base, _ = os.path.splitext(args.input_csv)
    out_csv  = f"{base}_with_desc.csv"
    out_json = f"{base}_with_desc.json"

    df.to_csv(out_csv, index=False, encoding="utf-8-sig")
    df.to_json(out_json, orient="records", force_ascii=False, indent=2)
    print(f"✅ 완료: {out_csv}, {out_json}")

if __name__ == "__main__":
    main()
