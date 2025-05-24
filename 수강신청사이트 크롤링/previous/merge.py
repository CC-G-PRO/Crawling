import pandas as pd

# 1) CSV 병합
df1 = pd.read_csv("computer_lectures_2025_1_0_50_with_desc.csv", encoding="utf-8-sig")
df2 = pd.read_csv("computer_lectures_2025_1_50_100_with_desc.csv", encoding="utf-8-sig")
df = pd.concat([df1, df2], ignore_index=True)
df.to_csv("computer_lectures_2025_1_full_with_desc.csv", index=False, encoding="utf-8-sig")

# 2) JSON 병합
j1 = pd.read_json("computer_lectures_2025_1_0_50_with_desc.json", encoding="utf-8-sig", orient="records")
j2 = pd.read_json("computer_lectures_2025_1_50_100_with_desc.json", encoding="utf-8-sig", orient="records")
df_json = pd.concat([j1, j2], ignore_index=True)
df_json.to_json("computer_lectures_2025_1_full_with_desc.json", orient="records", force_ascii=False, indent=2)
