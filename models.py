
import csv
import os

from utils import encrypt_password, decrypt_password
from data_structures import LinkedList, HashTable


def _read_csv(filepath: str) -> list[dict]:
    if not os.path.exists(filepath):
        return []
    with open(filepath, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _write_csv(filepath: str, fieldnames: list[str], rows: list[dict]) -> None:
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


STUDENT_FIELDS    = ["student_id", "email_address", "first_name", "last_name"]
PROFESSOR_FIELDS  = ["professor_id", "email_address", "professor_name", "rank", "course_ids"]
COURSE_FIELDS     = ["course_id", "course_code", "course_name", "description", "credits"]
ENROLLMENT_FIELDS = ["student_id", "course_id", "marks", "grade"]
LOGIN_FIELDS      = ["email_address", "password", "role"]


class User:

    def __init__(self, email_address: str, password: str):
        self.email_address = email_address
        self.password = password

    @staticmethod
    def encrypt_password(plaintext: str) -> str:
        return encrypt_password(plaintext)

    @staticmethod
    def decrypt_password(encrypted: str) -> str:
        return decrypt_password(encrypted)

    @staticmethod
    def login(email: str, plaintext: str, hash_table: HashTable) -> dict | None:
        record = hash_table.get(email)
        if record is None:
            return None
        if decrypt_password(record["password"]) == plaintext:
            return record
        return None

    @staticmethod
    def change_password(
        email: str,
        old_password: str,
        new_password: str,
        hash_table: HashTable,
        data_dir: str = "data/",
    ) -> bool:

        record = hash_table.get(email)
        if record is None:
            return False
        if decrypt_password(record["password"]) != old_password:
            return False

        encrypted_new = encrypt_password(new_password)

        hash_table.put(email, {"password": encrypted_new, "role": record["role"]})

        login_path = os.path.join(data_dir, "login.csv")
        rows = _read_csv(login_path)
        for row in rows:
            if row["email_address"] == email:
                row["password"] = encrypted_new
        _write_csv(login_path, LOGIN_FIELDS, rows)
        return True

    @staticmethod
    def logout() -> None:
        pass


class Student(User):

    ID_START = 1001

    def __init__(
        self,
        student_id: int,
        email_address: str,
        first_name: str,
        last_name: str,
        password: str = "",
    ):
        super().__init__(email_address, password)
        self.student_id = student_id
        self.first_name = first_name
        self.last_name = last_name

    @staticmethod
    def _next_id(data_dir: str) -> int:
        rows = _read_csv(os.path.join(data_dir, "students.csv"))
        if not rows:
            return Student.ID_START
        ids = [int(r["student_id"]) for r in rows]
        return max(ids) + 1

    @staticmethod
    def add_new_student(
        email_address: str,
        first_name: str,
        last_name: str,
        plaintext_password: str,
        data_dir: str = "data/",
    ) -> dict | None:

        login_rows = _read_csv(os.path.join(data_dir, "login.csv"))
        if any(r["email_address"] == email_address for r in login_rows):
            return None

        student_id = Student._next_id(data_dir)
        new_student = {
            "student_id":    student_id,
            "email_address": email_address,
            "first_name":    first_name,
            "last_name":     last_name,
        }

        student_path = os.path.join(data_dir, "students.csv")
        rows = _read_csv(student_path)
        rows.append(new_student)
        _write_csv(student_path, STUDENT_FIELDS, rows)

        login_rows.append({
            "email_address": email_address,
            "password":      encrypt_password(plaintext_password),
            "role":          "student",
        })
        _write_csv(os.path.join(data_dir, "login.csv"), LOGIN_FIELDS, login_rows)

        return new_student


    @staticmethod
    def delete_student(
        student_id: int,
        data_dir: str = "data/",
    ) -> bool:
 
        student_path = os.path.join(data_dir, "students.csv")
        rows = _read_csv(student_path)
        remaining = [r for r in rows if int(r["student_id"]) != student_id]

        if len(remaining) == len(rows):
            return False

        email = next(r["email_address"] for r in rows if int(r["student_id"]) == student_id)

        _write_csv(student_path, STUDENT_FIELDS, remaining)

        login_path = os.path.join(data_dir, "login.csv")
        login_rows = _read_csv(login_path)
        _write_csv(
            login_path,
            LOGIN_FIELDS,
            [r for r in login_rows if r["email_address"] != email],
        )

        enrollment_path = os.path.join(data_dir, "enrollments.csv")
        enrollment_rows = _read_csv(enrollment_path)
        _write_csv(
            enrollment_path,
            ENROLLMENT_FIELDS,
            [r for r in enrollment_rows if int(r["student_id"]) != student_id],
        )

        return True


    @staticmethod
    def update_student(
        student_id: int,
        first_name: str | None = None,
        last_name: str | None = None,
        new_email: str | None = None,
        data_dir: str = "data/",
    ) -> bool:
        
        student_path = os.path.join(data_dir, "students.csv")
        rows = _read_csv(student_path)
        updated = False
        old_email = None

        for row in rows:
            if int(row["student_id"]) == student_id:
                old_email = row["email_address"]
                if first_name:
                    row["first_name"] = first_name
                if last_name:
                    row["last_name"] = last_name
                if new_email:
                    row["email_address"] = new_email
                updated = True
                break

        if not updated:
            return False

        _write_csv(student_path, STUDENT_FIELDS, rows)

        if new_email and old_email and new_email != old_email:
            login_path = os.path.join(data_dir, "login.csv")
            login_rows = _read_csv(login_path)
            for row in login_rows:
                if row["email_address"] == old_email:
                    row["email_address"] = new_email
            _write_csv(login_path, LOGIN_FIELDS, login_rows)

        return True


    @staticmethod
    def display_records(data_dir: str = "data/") -> list[dict]:

        rows = _read_csv(os.path.join(data_dir, "students.csv"))

        ll = LinkedList()
        for r in rows:
            ll.insert({
                "student_id":    int(r["student_id"]),
                "email_address": r["email_address"],
                "first_name":    r["first_name"],
                "last_name":     r["last_name"],
            })
        ll.sort(key="last_name", reverse=False)
        sorted_records = ll.traverse()

        if not sorted_records:
            print("  No student records found.")
            return []

        print(f"\n  {'ID':<8} {'First Name':<15} {'Last Name':<15} {'Email'}")
        print(f"  {'-'*8} {'-'*15} {'-'*15} {'-'*30}")
        for r in sorted_records:
            print(f"  {r['student_id']:<8} {r['first_name']:<15} {r['last_name']:<15} {r['email_address']}")

        return sorted_records


    @staticmethod
    def check_my_grades(student_id: int, data_dir: str = "data/") -> list[dict]:

        enrollment_path = os.path.join(data_dir, "enrollments.csv")
        course_path     = os.path.join(data_dir, "courses.csv")

        enrollments = _read_csv(enrollment_path)
        courses     = {r["course_id"]: r for r in _read_csv(course_path)}

        my_rows = [r for r in enrollments if int(r["student_id"]) == student_id]

        if not my_rows:
            print("  No grades on record.")
            return []

        print(f"\n  {'Course Code':<14} {'Course Name':<25} {'Marks':<8} {'Grade'}")
        print(f"  {'-'*14} {'-'*25} {'-'*8} {'-'*6}")
        for r in my_rows:
            course = courses.get(r["course_id"], {})
            print(
                f"  {course.get('course_code', r['course_id']):<14} "
                f"{course.get('course_name', 'Unknown'):<25} "
                f"{r['marks']:<8} {r['grade']}"
            )

        return my_rows


    @staticmethod
    def load_linked_list(data_dir: str = "data/") -> LinkedList:

        ll = LinkedList()
        for r in _read_csv(os.path.join(data_dir, "students.csv")):
            ll.insert({
                "student_id":    int(r["student_id"]),
                "email_address": r["email_address"],
                "first_name":    r["first_name"],
                "last_name":     r["last_name"],
            })
        return ll


class Professor(User):

    ID_START = 2001

    def __init__(
        self,
        professor_id: int,
        email_address: str,
        professor_name: str,
        rank: str,
        course_ids: list,
        password: str = "",
    ):
        super().__init__(email_address, password)
        self.professor_id   = professor_id
        self.professor_name = professor_name
        self.rank           = rank
        self.course_ids     = course_ids


    @staticmethod
    def _next_id(data_dir: str) -> int:
        rows = _read_csv(os.path.join(data_dir, "professors.csv"))
        if not rows:
            return Professor.ID_START
        ids = [int(r["professor_id"]) for r in rows]
        return max(ids) + 1


    @staticmethod
    def add_new_professor(
        email_address: str,
        professor_name: str,
        rank: str,
        plaintext_password: str,
        course_ids: list | None = None,
        data_dir: str = "data/",
    ) -> dict | None:

        login_rows = _read_csv(os.path.join(data_dir, "login.csv"))
        if any(r["email_address"] == email_address for r in login_rows):
            return None

        professor_id = Professor._next_id(data_dir)
        course_ids_str = ",".join(str(c) for c in (course_ids or []))

        new_prof = {
            "professor_id":   professor_id,
            "email_address":  email_address,
            "professor_name": professor_name,
            "rank":           rank,
            "course_ids":     course_ids_str,
        }

        prof_path = os.path.join(data_dir, "professors.csv")
        rows = _read_csv(prof_path)
        rows.append(new_prof)
        _write_csv(prof_path, PROFESSOR_FIELDS, rows)

        login_rows.append({
            "email_address": email_address,
            "password":      encrypt_password(plaintext_password),
            "role":          "professor",
        })
        _write_csv(os.path.join(data_dir, "login.csv"), LOGIN_FIELDS, login_rows)

        return new_prof


    @staticmethod
    def delete_professor(professor_id: int, data_dir: str = "data/") -> bool:

        prof_path = os.path.join(data_dir, "professors.csv")
        rows = _read_csv(prof_path)
        remaining = [r for r in rows if int(r["professor_id"]) != professor_id]

        if len(remaining) == len(rows):
            return False

        email = next(r["email_address"] for r in rows if int(r["professor_id"]) == professor_id)
        _write_csv(prof_path, PROFESSOR_FIELDS, remaining)

        login_path = os.path.join(data_dir, "login.csv")
        login_rows = _read_csv(login_path)
        _write_csv(
            login_path,
            LOGIN_FIELDS,
            [r for r in login_rows if r["email_address"] != email],
        )
        return True


    @staticmethod
    def modify_professor(
        professor_id: int,
        professor_name: str | None = None,
        rank: str | None = None,
        new_email: str | None = None,
        course_ids: list | None = None,
        data_dir: str = "data/",
    ) -> bool:

        prof_path = os.path.join(data_dir, "professors.csv")
        rows = _read_csv(prof_path)
        updated = False
        old_email = None

        for row in rows:
            if int(row["professor_id"]) == professor_id:
                old_email = row["email_address"]
                if professor_name:
                    row["professor_name"] = professor_name
                if rank:
                    row["rank"] = rank
                if new_email:
                    row["email_address"] = new_email
                if course_ids is not None:
                    row["course_ids"] = ",".join(str(c) for c in course_ids)
                updated = True
                break

        if not updated:
            return False

        _write_csv(prof_path, PROFESSOR_FIELDS, rows)

        if new_email and old_email and new_email != old_email:
            login_path = os.path.join(data_dir, "login.csv")
            login_rows = _read_csv(login_path)
            for row in login_rows:
                if row["email_address"] == old_email:
                    row["email_address"] = new_email
            _write_csv(login_path, LOGIN_FIELDS, login_rows)

        return True

    @staticmethod
    def display_records(data_dir: str = "data/") -> list[dict]:

        rows = _read_csv(os.path.join(data_dir, "professors.csv"))

        if not rows:
            print("  No professor records found.")
            return []

        print(f"\n  {'ID':<8} {'Name':<25} {'Rank':<22} {'Email':<28} {'Courses'}")
        print(f"  {'-'*8} {'-'*25} {'-'*22} {'-'*28} {'-'*15}")
        for r in rows:
            print(
                f"  {r['professor_id']:<8} {r['professor_name']:<25} "
                f"{r['rank']:<22} {r['email_address']:<28} {r['course_ids']}"
            )

        return rows

    @staticmethod
    def show_course_by_professor(professor_id: int, data_dir: str = "data/") -> list[dict]:

        prof_rows = _read_csv(os.path.join(data_dir, "professors.csv"))
        prof = next((r for r in prof_rows if int(r["professor_id"]) == professor_id), None)

        if not prof:
            print("  Professor not found.")
            return []

        raw_ids = [cid.strip() for cid in prof["course_ids"].split(",") if cid.strip()]
        if not raw_ids:
            print("  No courses assigned to this professor.")
            return []

        all_courses = _read_csv(os.path.join(data_dir, "courses.csv"))
        courses = [c for c in all_courses if c["course_id"] in raw_ids]

        if not courses:
            print("  No matching courses found.")
            return []

        print(f"\n  Courses taught by {prof['professor_name']}:")
        print(f"\n  {'ID':<8} {'Code':<12} {'Name':<25} {'Credits'}")
        print(f"  {'-'*8} {'-'*12} {'-'*25} {'-'*7}")
        for c in courses:
            print(f"  {c['course_id']:<8} {c['course_code']:<12} {c['course_name']:<25} {c['credits']}")

        return courses

class Course:

    ID_START = 3001

    def __init__(
        self,
        course_id: int,
        course_code: str,
        course_name: str,
        description: str,
        credits: int,
    ):
        self.course_id   = course_id
        self.course_code = course_code
        self.course_name = course_name
        self.description = description
        self.credits     = credits


    @staticmethod
    def _next_id(data_dir: str) -> int:
        rows = _read_csv(os.path.join(data_dir, "courses.csv"))
        if not rows:
            return Course.ID_START
        ids = [int(r["course_id"]) for r in rows]
        return max(ids) + 1

    @staticmethod
    def add_new_course(
        course_code: str,
        course_name: str,
        description: str,
        credits: int,
        data_dir: str = "data/",
    ) -> dict:

        course_id = Course._next_id(data_dir)
        new_course = {
            "course_id":   course_id,
            "course_code": course_code,
            "course_name": course_name,
            "description": description,
            "credits":     credits,
        }

        course_path = os.path.join(data_dir, "courses.csv")
        rows = _read_csv(course_path)
        rows.append(new_course)
        _write_csv(course_path, COURSE_FIELDS, rows)
        return new_course


    @staticmethod
    def delete_course(course_id: int, data_dir: str = "data/") -> bool:

        course_path = os.path.join(data_dir, "courses.csv")
        rows = _read_csv(course_path)
        remaining = [r for r in rows if int(r["course_id"]) != course_id]

        if len(remaining) == len(rows):
            return False

        _write_csv(course_path, COURSE_FIELDS, remaining)
        return True


    @staticmethod
    def modify_course(
        course_id: int,
        course_code: str | None = None,
        course_name: str | None = None,
        description: str | None = None,
        credits: int | None = None,
        data_dir: str = "data/",
    ) -> bool:

        course_path = os.path.join(data_dir, "courses.csv")
        rows = _read_csv(course_path)
        updated = False

        for row in rows:
            if int(row["course_id"]) == course_id:
                if course_code:
                    row["course_code"] = course_code
                if course_name:
                    row["course_name"] = course_name
                if description:
                    row["description"] = description
                if credits is not None:
                    row["credits"] = credits
                updated = True
                break

        if not updated:
            return False

        _write_csv(course_path, COURSE_FIELDS, rows)
        return True

    @staticmethod
    def display_courses(data_dir: str = "data/") -> list[dict]:
        rows = _read_csv(os.path.join(data_dir, "courses.csv"))

        if not rows:
            print("  No courses found.")
            return []

        print(f"\n  {'ID':<8} {'Code':<12} {'Name':<25} {'Credits':<9} {'Description'}")
        print(f"  {'-'*8} {'-'*12} {'-'*25} {'-'*9} {'-'*35}")
        for r in rows:
            print(
                f"  {r['course_id']:<8} {r['course_code']:<12} "
                f"{r['course_name']:<25} {r['credits']:<9} {r['description']}"
            )

        return rows


class Grades:

    SCALE = [
        (97, "A+"),
        (93, "A"),
        (90, "A-"),
        (87, "B+"),
        (83, "B"),
        (80, "B-"),
        (77, "C+"),
        (73, "C"),
        (70, "C-"),
        (60, "D"),
        (0,  "F"),
    ]

    @staticmethod
    def get_grade_from_marks(marks: int) -> str:
        if not (0 <= int(marks) <= 100):
            raise ValueError(f"Marks must be between 0 and 100, got {marks}.")
        for threshold, letter in Grades.SCALE:
            if int(marks) >= threshold:
                return letter
        return "F"


    @staticmethod
    def enroll_student(
        student_id: int,
        course_id: int,
        data_dir: str = "data/",
    ) -> bool:
        enrollment_path = os.path.join(data_dir, "enrollments.csv")
        rows = _read_csv(enrollment_path)

        for row in rows:
            if int(row["student_id"]) == student_id and int(row["course_id"]) == course_id:
                return True

        rows.append({
            "student_id": student_id,
            "course_id":  course_id,
            "marks":      "",
            "grade":      "N/A",
        })
        _write_csv(enrollment_path, ENROLLMENT_FIELDS, rows)
        return True


    @staticmethod
    def add_grade(
        student_id: int,
        course_id: int,
        marks: int,
        data_dir: str = "data/",
    ) -> dict | None:

        try:
            grade_letter = Grades.get_grade_from_marks(marks)
        except ValueError:
            return None

        enrollment_path = os.path.join(data_dir, "enrollments.csv")
        rows = _read_csv(enrollment_path)

        new_row = {
            "student_id": student_id,
            "course_id":  course_id,
            "marks":      marks,
            "grade":      grade_letter,
        }

        for row in rows:
            if int(row["student_id"]) == student_id and int(row["course_id"]) == course_id:
                row["marks"] = marks
                row["grade"] = grade_letter
                _write_csv(enrollment_path, ENROLLMENT_FIELDS, rows)
                return new_row

        rows.append(new_row)
        _write_csv(enrollment_path, ENROLLMENT_FIELDS, rows)
        return new_row


    @staticmethod
    def delete_grade(
        student_id: int,
        course_id: int,
        data_dir: str = "data/",
    ) -> bool:

        enrollment_path = os.path.join(data_dir, "enrollments.csv")
        rows = _read_csv(enrollment_path)
        remaining = [
            r for r in rows
            if not (int(r["student_id"]) == student_id and int(r["course_id"]) == course_id)
        ]

        if len(remaining) == len(rows):
            return False

        _write_csv(enrollment_path, ENROLLMENT_FIELDS, remaining)
        return True


    @staticmethod
    def modify_grade(
        student_id: int,
        course_id: int,
        new_marks: int,
        data_dir: str = "data/",
    ) -> bool:

        enrollment_path = os.path.join(data_dir, "enrollments.csv")
        rows = _read_csv(enrollment_path)
        updated = False

        for row in rows:
            if int(row["student_id"]) == student_id and int(row["course_id"]) == course_id:
                row["marks"] = new_marks
                row["grade"] = Grades.get_grade_from_marks(new_marks)
                updated = True
                break

        if not updated:
            return False

        _write_csv(enrollment_path, ENROLLMENT_FIELDS, rows)
        return True


    @staticmethod
    def average_score(course_id: int, data_dir: str = "data/") -> float | None:

        rows = _read_csv(os.path.join(data_dir, "enrollments.csv"))
        marks = [int(r["marks"]) for r in rows if int(r["course_id"]) == course_id and r["marks"] != ""]

        if not marks:
            return None

        return round(sum(marks) / len(marks), 2)

    @staticmethod
    def median_score(course_id: int, data_dir: str = "data/") -> float | None:

        rows = _read_csv(os.path.join(data_dir, "enrollments.csv"))
        marks = sorted(int(r["marks"]) for r in rows if int(r["course_id"]) == course_id and r["marks"] != "")

        if not marks:
            return None

        n = len(marks)
        mid = n // 2
        if n % 2 == 0:
            return round((marks[mid - 1] + marks[mid]) / 2, 2)
        return float(marks[mid])

    @staticmethod
    def display_grade_report(
        filter_by: str,
        value,
        data_dir: str = "data/",
    ) -> list[dict]:

        enrollments = _read_csv(os.path.join(data_dir, "enrollments.csv"))
        courses     = {r["course_id"]: r for r in _read_csv(os.path.join(data_dir, "courses.csv"))}
        students    = {r["student_id"]: r for r in _read_csv(os.path.join(data_dir, "students.csv"))}

        if filter_by == "course":
            rows = [r for r in enrollments if int(r["course_id"]) == value]

        elif filter_by == "student":
            rows = [r for r in enrollments if int(r["student_id"]) == value]

        elif filter_by == "professor":
            prof_rows = _read_csv(os.path.join(data_dir, "professors.csv"))
            prof = next((p for p in prof_rows if int(p["professor_id"]) == value), None)
            if not prof:
                print("  Professor not found.")
                return []
            prof_course_ids = [c.strip() for c in prof["course_ids"].split(",") if c.strip()]
            rows = [r for r in enrollments if r["course_id"] in prof_course_ids]

        else:
            print(f"  Unknown filter_by value: {filter_by!r}")
            return []

        if not rows:
            print("  No grade records found for this filter.")
            return []

        print(f"\n  {'Student ID':<12} {'Student Name':<22} {'Course Code':<14} {'Marks':<8} {'Grade'}")
        print(f"  {'-'*12} {'-'*22} {'-'*14} {'-'*8} {'-'*6}")

        report = []
        for r in rows:
            student = students.get(r["student_id"], {})
            course  = courses.get(r["course_id"], {})
            name    = f"{student.get('first_name', '?')} {student.get('last_name', '?')}"
            code    = course.get("course_code", r["course_id"])
            row_out = {
                "student_id":   r["student_id"],
                "student_name": name,
                "course_code":  code,
                "marks":        r["marks"],
                "grade":        r["grade"],
            }
            print(
                f"  {r['student_id']:<12} {name:<22} {code:<14} "
                f"{r['marks']:<8} {r['grade']}"
            )
            report.append(row_out)

        return report