# Crawling
1️⃣ 종합시간표 조회 사이트 크롤링

- 경희대 종합시간표 조회 페이지 접속
- 대상: 2025년 1학기, 소프트웨어융합대학 컴퓨터공학과
- 크롤링 항목:
  - 학수번호 (`subject_code`)
  - 강좌명 (`subject_name`)
  - 교수명
  - 학점
  - 강의시간 및 장소
  - 언어구분 (`영어`, `영어(부분)` 등)
  - 특이사항 (`실습`, `본인 노트북 지참` 등)
  - 강의계획서 링크

> 📁 결과 저장:  
> - `computer_lectures_2025_1.csv` (엑셀 호환)  
> - `computer_lectures_2025_1.json` (API 서버 연동용)

---

2️⃣ 교육과정 PDF에서 과목 구분 정보 파싱 (작업 예정)

- 컴퓨터공학과 교육과정 PDF에서 과목 분류 정보 추출
  - 전공기초 / 전공필수 / 전공선택 구분
  - 학년/학기별 개설 정보
  - 과목 설명 및 학점
- 파싱 도구: [`pdfplumber`](https://github.com/jsvine/pdfplumber)
- 파싱된 데이터는 종합시간표 데이터와 **과목 코드 기준으로 통합** 가능

> 📁 결과 저장 예정:
> - `subject_classification.json`
> - `subject_classification.csv`
