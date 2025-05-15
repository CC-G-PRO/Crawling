from playwright.sync_api import sync_playwright
import pandas as pd
import json

def crawl_computer_engineering():
    data = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        # 1) 메인 진입
        page.goto("https://sugang.khu.ac.kr")
        page.wait_for_timeout(3000)

        # 2) Main → coreMain 프레임 전환
        #    (좌측 메뉴 fnLoad 호출 전에 coreMain 이 이미 올라와 있을 수 있음)
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

        # 4) 드롭다운 순서대로 선택
        core_frame.wait_for_selector("select#p_year", timeout=5000)
        core_frame.select_option("select#p_year", "2025")
        core_frame.wait_for_timeout(500)

        core_frame.wait_for_selector("select#p_term", timeout=5000)
        core_frame.select_option("select#p_term", label="1학기")
        core_frame.wait_for_timeout(500)

        core_frame.wait_for_selector("select#p_daehak", timeout=5000)
        core_frame.select_option("select#p_daehak", label="소프트웨어융합대학")
        core_frame.wait_for_timeout(500)

        core_frame.wait_for_selector("select#p_major", timeout=5000)
        core_frame.select_option(
            "select#p_major",
            label="소프트웨어융합대학 컴퓨터공학부 컴퓨터공학과"
        )
        core_frame.wait_for_timeout(500)

        print("✅ 드롭다운 선택 완료")

        # 5) 조회 버튼 클릭
        core_frame.click("button:has-text('조회')")
        core_frame.wait_for_timeout(2000)
        print("✅ 조회 버튼 클릭 완료")

        # 6) 테이블 파싱 (이수구분 인덱스는 건너뜀)
        for row in core_frame.query_selector_all("table tbody tr"):
            cols = row.query_selector_all("td")
            if len(cols) < 12:
                continue

            campus      = cols[1].inner_text().strip()
            course_no   = cols[2].inner_text().strip()
            title       = cols[3].inner_text().strip()
            target_year = cols[4].inner_text().strip()
            capacity    = cols[5].inner_text().strip()
            professor   = cols[6].inner_text().strip()
            credit      = cols[7].inner_text().strip()
            time_place  = cols[8].inner_text().strip()
            # cols[9] = 이수구분 (skip)
            language    = cols[10].inner_text().strip()
            note        = cols[11].inner_text().strip()
            link_el     = cols[12].query_selector("a")
            syllabus_url= link_el.get_attribute("href") if link_el else ""

            data.append({
                "campus": campus,
                "course_no": course_no,
                "title": title,
                "target_year": target_year,
                "capacity": capacity,
                "professor": professor,
                "credit": credit,
                "time_place": time_place,
                "language": language,
                "note": note,
                "syllabus_url": syllabus_url
            })

        browser.close()

    # 7) CSV & JSON 저장
    df = pd.DataFrame(data)
    # 빈 문자열을 NaN으로 바꾸고, 모든 값이 NaN인 행은 삭제
    df.replace('', pd.NA, inplace=True)
    df.dropna(how='all', inplace=True)
    df.to_csv("computer_lectures_2025_1.csv", index=False, encoding="utf-8-sig")
    # data 중에 모든 값이 빈 문자열인 행은 제외
    filtered = [row for row in data if any(v != "" for v in row.values())]
    with open("computer_lectures_2025_1.json", "w", encoding="utf-8") as f:
        json.dump(filtered, f, ensure_ascii=False, indent=2)

    print(f"✅ 총 {len(data)}건 저장 완료")

if __name__ == "__main__":
    crawl_computer_engineering()
