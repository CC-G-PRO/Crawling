from playwright.sync_api import sync_playwright
import pandas as pd
import json
from pathlib import Path

def crawl_computer_engineering():
    data = []

    # 파일 저장 디렉터리 설정 (스크립트 위치 기준)
    base_dir = Path(__file__).parent.resolve()
    csv_path = base_dir / "computer_lectures_2025_1.csv"
    json_path = base_dir / "computer_lectures_2025_1.json"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        # 1) 메인 진입
        page.goto("https://sugang.khu.ac.kr")
        page.wait_for_timeout(3000)

        # 2) Main → coreMain 프레임 전환
        core_frame = page.frame(name="coreMain")
        if not core_frame:
            print("❌ coreMain 프레임 접근 실패")
            browser.close()
            return
        core_frame.wait_for_load_state("domcontentloaded")

        # 3) “종합시간표 조회” 탭 열기
        core_frame.wait_for_function("typeof fnLoad === 'function'", timeout=5000)
        core_frame.evaluate(
            "fnLoad(urlCoreLectureList, document.querySelector(\"li[onclick*='urlCoreLectureList']\"))"
        )
        print("✅ 종합시간표 조회 메뉴 열기 성공")
        page.wait_for_timeout(2000)

        # 4) 드롭다운 선택 및 값 저장
        core_frame.wait_for_selector("select#p_year", timeout=5000)
        core_frame.select_option("select#p_year", "2025")
        page.wait_for_timeout(500)
        lecture_year = int(core_frame.evaluate("() => document.querySelector('select#p_year option:checked').innerText"))

        core_frame.wait_for_selector("select#p_term", timeout=5000)
        core_frame.select_option("select#p_term", label="1학기")
        page.wait_for_timeout(500)
        semester_text = core_frame.evaluate("() => document.querySelector('select#p_term option:checked').innerText")
        semester = int(semester_text.replace('학기', '').strip())

        core_frame.wait_for_selector("select#p_daehak", timeout=5000)
        core_frame.select_option("select#p_daehak", label="소프트웨어융합대학")
        page.wait_for_timeout(500)

        core_frame.wait_for_selector("select#p_major", timeout=5000)
        core_frame.select_option(
            "select#p_major",
            label="소프트웨어융합대학 컴퓨터공학부 컴퓨터공학과"
        )
        page.wait_for_timeout(500)
        print(f"✅ 드롭다운 선택 완료: {lecture_year}년 {semester}학기")

        # 5) 조회 버튼 클릭
        core_frame.click("button:has-text('조회')")
        core_frame.wait_for_timeout(2000)
        print("✅ 조회 버튼 클릭 완료")

        # 6) 테이블 파싱 (헤더 행 스킵, popup을 통해 syllabus_url 획득)
        rows = core_frame.query_selector_all("table tbody tr")
        for row in rows[1:]:
            cols = row.query_selector_all("td")
            if len(cols) < 12:
                continue

            campus     = cols[1].inner_text().strip()
            course_no  = cols[2].inner_text().strip()
            title      = cols[3].inner_text().strip()
            target_year= cols[4].inner_text().strip()
            capacity   = cols[5].inner_text().strip()
            professor  = cols[6].inner_text().strip()
            credit     = cols[7].inner_text().strip()
            time_place = cols[8].inner_text().strip()
            language   = cols[10].inner_text().strip()
            is_english = isinstance(language, str) and ('영어' in language or 'English' in language)
            note       = cols[11].inner_text().strip()

            # 강의계획서 아이콘 클릭 후 popup URL 획득
            img = cols[12].query_selector("img[title='강의계획안 보기']")
            syllabus_url = ""
            if img:
                with page.expect_popup() as popup_info:
                    img.click()
                popup = popup_info.value
                popup.wait_for_load_state()
                syllabus_url = popup.url
                popup.close()

            data.append({
                "lecture_year": lecture_year,
                "semester": semester,
                "campus": campus,
                "course_no": course_no,
                "title": title,
                "target_year": target_year,
                "capacity": capacity,
                "professor": professor,
                "credit": credit,
                "time_place": time_place,
                "language": language,
                "is_english": is_english,
                "note": note,
                "syllabus_url": syllabus_url
            })

        browser.close()

    # 7) CSV & JSON 저장 (campus NaN 제거)
    df = pd.DataFrame(data)
    df.replace('', pd.NA, inplace=True)
    df.dropna(how='all', inplace=True)
    df.dropna(subset=['campus'], inplace=True)

    print(f"Saving to: {csv_path}")
    df.to_csv(csv_path, index=False, encoding="utf-8-sig")
    print(f"✅ CSV saved with {len(df)} rows.")

    print(f"Saving to: {json_path}")
    records = df.to_dict(orient='records')
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)
    print(f"✅ JSON saved with {len(records)} records.")

if __name__ == "__main__":
    print(f"Current working directory: {Path.cwd()}")
    crawl_computer_engineering()