
import csv
import pymysql

def insert_subjects(conn):
    cursor = conn.cursor()
    subject_code_to_id = {}
    with open("subjects.csv", encoding="cp949") as f:
        reader = csv.DictReader(f)
        for row in reader:
            cursor.execute(
                "INSERT INTO subjects (subject_code, credit, target_grade, type_number, ai_description, category) VALUES (%s, %s, %s, %s, %s, %s)",
                (
                    row["subject_code"],
                    row["credit"],
                    row["target_grade"],
                    row["type_number"] or None,
                    row["ai_description"] or None,
                    row["category"] or None,
                ),
            )
            subject_code_to_id[row["subject_code"]] = cursor.lastrowid
    conn.commit()
    return subject_code_to_id

def insert_curriculum(conn, subject_code_to_id):
    cursor = conn.cursor()
    with open("curriculum.csv", encoding="cp949") as f:
        reader = csv.DictReader(f)
        for row in reader:
            subject_code = row["subject_id"]
            subject_id = subject_code_to_id.get(subject_code)
            cursor.execute(
                "INSERT INTO curriculum (entry_year, subject_id, major_category) VALUES (%s, %s, %s)",
                (
                    row["entry_year"],
                    subject_id,
                    row["major_category"],
                ),
            )
    conn.commit()

def insert_lectures(conn, subject_code_to_id):
    cursor = conn.cursor()
    division_code_to_id = {}
    with open("lectures.csv", encoding="cp949") as f:
        reader = csv.DictReader(f)
        for row in reader:
            subject_id = subject_code_to_id.get(row["subject_code"])
            cursor.execute(
                """INSERT INTO lectures (
                    lecture_year, semester, professor_name, subject_name, division_code,
                    lecture_place, capacity, language, is_english, note, syllabus_url,
                    subject_id, created_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                (
                    row["lecture_year"],
                    row["semester"],
                    row["professor_name"],
                    row["subject_name"],
                    row["division_code"],
                    row["lecture_place"],
                    row["capacity"],
                    row["language"],
                    row["is_english"] == "TRUE",
                    row["note"],
                    row["syllabus_url"],
                    subject_id,
                    row["created_at"],
                ),
            )
            division_code_to_id[row["division_code"]] = cursor.lastrowid
    conn.commit()
    return division_code_to_id

def insert_lecture_times(conn, division_code_to_id):
    cursor = conn.cursor()
    with open("lecture_times.csv", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            lecture_id = division_code_to_id.get(row["division_code"])
            if lecture_id:
                cursor.execute(
                    "INSERT INTO lecture_times (lecture_id, day_of_week, start_time, end_time) VALUES (%s, %s, %s, %s)",
                    (
                        lecture_id,
                        row["day"],
                        row["start_time"],
                        row["end_time"],
                    ),
                )
    conn.commit()

def main():
    conn = pymysql.connect(
        host="db-sugang.czskim0kcrra.ap-northeast-2.rds.amazonaws.com",
        port=3306,
        user="admin",
        password="78S>AN:OisHjY_8Dj<Ydw2x)]5$W",
        database="sugang_prod",
        charset="utf8mb4"
    )

    print("Inserting subjects...")
    subject_code_to_id = insert_subjects(conn)

    print("Inserting curriculum...")
    insert_curriculum(conn, subject_code_to_id)

    print("Inserting lectures...")
    division_code_to_id = insert_lectures(conn, subject_code_to_id)

    print("Inserting lecture_times...")
    insert_lecture_times(conn, division_code_to_id)

    conn.close()

if __name__ == "__main__":
    main()
