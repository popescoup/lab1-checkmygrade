
import os
import shutil
import tempfile
import time
import unittest

from models import (
    Student, Professor, Course, Grades, User,
    _read_csv, _write_csv,
    STUDENT_FIELDS, PROFESSOR_FIELDS, COURSE_FIELDS,
    ENROLLMENT_FIELDS, LOGIN_FIELDS,
)
from data_structures import LinkedList, HashTable
from utils import encrypt_password, decrypt_password


def _seed_dir(data_dir: str) -> None:
    _write_csv(os.path.join(data_dir, "students.csv"),    STUDENT_FIELDS,    [])
    _write_csv(os.path.join(data_dir, "enrollments.csv"), ENROLLMENT_FIELDS, [])
    _write_csv(os.path.join(data_dir, "login.csv"),       LOGIN_FIELDS,      [])
    _write_csv(
        os.path.join(data_dir, "courses.csv"),
        COURSE_FIELDS,
        [
            {
                "course_id":   3001,
                "course_code": "DATA200",
                "course_name": "Programming for Data Analytics",
                "description": "Basics of Python Programming for numerical implementation of mathematical and statistical algorithms",
                "credits":     3,
            },
            {
                "course_id":   3002,
                "course_code": "DATA201",
                "course_name": "Database Technologies",
                "description": "Fundamentals of SQL and database design",
                "credits":     3,
            },
        ],
    )
    _write_csv(
        os.path.join(data_dir, "professors.csv"),
        PROFESSOR_FIELDS,
        [
            {
                "professor_id":   2001,
                "email_address":  "luca@sjsu.edu",
                "professor_name": "Luca Popescu",
                "rank":           "Senior Professor",
                "course_ids":     "3001,3002",
            }
        ],
    )
    _write_csv(
        os.path.join(data_dir, "login.csv"),
        LOGIN_FIELDS,
        [
            {
                "email_address": "luca@sjsu.edu",
                "password":      encrypt_password("LucaIsCool1"),
                "role":          "professor",
            }
        ],
    )


def _bulk_add_students(n: int, data_dir: str) -> None:
    for i in range(n):
        Student.add_new_student(
            email_address      = f"student_{i}@sjsu.edu",
            first_name         = f"First{i}",
            last_name          = f"Last{i}",
            plaintext_password = f"LucaIsCool{i + 1}",
            data_dir           = data_dir,
        )


def _load_ll(data_dir: str) -> LinkedList:
    return Student.load_linked_list(data_dir=data_dir)


class TestStudentRecords(unittest.TestCase):
    def setUp(self) -> None:
        self.data_dir = tempfile.mkdtemp()
        _seed_dir(self.data_dir)

    def tearDown(self) -> None:
        shutil.rmtree(self.data_dir)


    def test_add_student(self) -> None:
        result = Student.add_new_student(
            "ozzy@sjsu.edu", "Ozzy", "Osbourne", "LucaIsCool2",
            data_dir=self.data_dir,
        )
        self.assertIsNotNone(result)
        self.assertEqual(result["student_id"], 1001)
        self.assertEqual(result["first_name"], "Ozzy")
        self.assertEqual(result["last_name"],  "Osbourne")

        rows = _read_csv(os.path.join(self.data_dir, "students.csv"))
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["email_address"], "ozzy@sjsu.edu")

        login_rows = _read_csv(os.path.join(self.data_dir, "login.csv"))
        student_login = next(
            (r for r in login_rows if r["email_address"] == "ozzy@sjsu.edu"), None
        )
        self.assertIsNotNone(student_login)
        self.assertEqual(student_login["role"], "student")
        self.assertEqual(decrypt_password(student_login["password"]), "LucaIsCool2")

        result2 = Student.add_new_student(
            "mick@sjsu.edu", "Mick", "Jagger", "LucaIsCool3",
            data_dir=self.data_dir,
        )
        self.assertEqual(result2["student_id"], 1002)

        dup = Student.add_new_student(
            "ozzy@sjsu.edu", "Ozzy", "Osbourne", "LucaIsCool2",
            data_dir=self.data_dir,
        )
        self.assertIsNone(dup)

        rows = _read_csv(os.path.join(self.data_dir, "students.csv"))
        self.assertEqual(len(rows), 2)


    def test_delete_student(self) -> None:
        Student.add_new_student(
            "john@sjsu.edu", "John", "Lennon", "LucaIsCool2",
            data_dir=self.data_dir,
        )
        Grades.add_grade(1001, 3001, 88, data_dir=self.data_dir)

        enrollments = _read_csv(os.path.join(self.data_dir, "enrollments.csv"))
        self.assertEqual(len(enrollments), 1)

        ok = Student.delete_student(1001, data_dir=self.data_dir)
        self.assertTrue(ok)

        rows = _read_csv(os.path.join(self.data_dir, "students.csv"))
        self.assertFalse(any(int(r["student_id"]) == 1001 for r in rows))

        login_rows = _read_csv(os.path.join(self.data_dir, "login.csv"))
        self.assertFalse(any(r["email_address"] == "john@sjsu.edu" for r in login_rows))

        enrollments = _read_csv(os.path.join(self.data_dir, "enrollments.csv"))
        self.assertEqual(len(enrollments), 0)

        miss = Student.delete_student(9999, data_dir=self.data_dir)
        self.assertFalse(miss)


    def test_modify_student(self) -> None:
        Student.add_new_student(
            "freddie@sjsu.edu", "Freddie", "Mercury", "LucaIsCool2",
            data_dir=self.data_dir,
        )

        ok = Student.update_student(1001, first_name="Frederick", data_dir=self.data_dir)
        self.assertTrue(ok)
        rows = _read_csv(os.path.join(self.data_dir, "students.csv"))
        row = next(r for r in rows if int(r["student_id"]) == 1001)
        self.assertEqual(row["first_name"], "Frederick")
        self.assertEqual(row["last_name"],  "Mercury")

        ok = Student.update_student(
            1001, new_email="frederick@sjsu.edu", data_dir=self.data_dir
        )
        self.assertTrue(ok)
        login_rows = _read_csv(os.path.join(self.data_dir, "login.csv"))
        self.assertFalse(any(r["email_address"] == "freddie@sjsu.edu"   for r in login_rows))
        self.assertTrue( any(r["email_address"] == "frederick@sjsu.edu" for r in login_rows))

        miss = Student.update_student(9999, first_name="Ghost", data_dir=self.data_dir)
        self.assertFalse(miss)


    def test_bulk_add_1000_students(self) -> None:
        N = 1000

        start = time.time()
        _bulk_add_students(N, self.data_dir)
        elapsed = time.time() - start

        print(f"\n  [TIMING] Bulk insert {N} students: {elapsed:.4f} seconds")

        rows = _read_csv(os.path.join(self.data_dir, "students.csv"))
        self.assertEqual(len(rows), N)

        ids = [int(r["student_id"]) for r in rows]
        self.assertEqual(len(set(ids)), N)
        self.assertEqual(min(ids), 1001)


class TestSearchAndSort(unittest.TestCase):
    def setUp(self) -> None:
        self.data_dir = tempfile.mkdtemp()
        _seed_dir(self.data_dir)

        _bulk_add_students(1000, self.data_dir)
        self.ll = _load_ll(self.data_dir)

    def tearDown(self) -> None:
        shutil.rmtree(self.data_dir)


    def test_search_with_timing(self) -> None:
        target = "student_500@sjsu.edu"

        start   = time.time()
        result  = self.ll.search(target, "email_address")
        elapsed = time.time() - start

        print(f"\n  [TIMING] Search (1 000 records, by email): {elapsed:.6f} seconds")

        self.assertIsNotNone(result)
        self.assertEqual(result["email_address"], target)


    def test_sort_by_marks_asc(self) -> None:

        for i in range(1000):
            Grades.add_grade(1001 + i, 3001, i % 101, data_dir=self.data_dir)

        ll = LinkedList()
        enrollments = _read_csv(os.path.join(self.data_dir, "enrollments.csv"))
        marks_map = {int(e["student_id"]): int(e["marks"]) for e in enrollments}

        for row in _read_csv(os.path.join(self.data_dir, "students.csv")):
            sid = int(row["student_id"])
            ll.insert({
                "student_id":    sid,
                "email_address": row["email_address"],
                "first_name":    row["first_name"],
                "last_name":     row["last_name"],
                "marks":         marks_map.get(sid, 0),
            })

        start   = time.time()
        ll.sort(key="marks", reverse=False)
        elapsed = time.time() - start

        print(f"\n  [TIMING] Sort by marks ascending (1 000 records): {elapsed:.6f} seconds")

        records = ll.traverse()
        mark_values = [r["marks"] for r in records]
        self.assertEqual(mark_values, sorted(mark_values))


    def test_sort_by_marks_desc(self) -> None:
        for i in range(1000):
            Grades.add_grade(1001 + i, 3001, i % 101, data_dir=self.data_dir)

        ll = LinkedList()
        enrollments = _read_csv(os.path.join(self.data_dir, "enrollments.csv"))
        marks_map = {int(e["student_id"]): int(e["marks"]) for e in enrollments}

        for row in _read_csv(os.path.join(self.data_dir, "students.csv")):
            sid = int(row["student_id"])
            ll.insert({
                "student_id":    sid,
                "email_address": row["email_address"],
                "first_name":    row["first_name"],
                "last_name":     row["last_name"],
                "marks":         marks_map.get(sid, 0),
            })

        start   = time.time()
        ll.sort(key="marks", reverse=True)
        elapsed = time.time() - start

        print(f"\n  [TIMING] Sort by marks descending (1 000 records): {elapsed:.6f} seconds")

        records = ll.traverse()
        mark_values = [r["marks"] for r in records]
        self.assertEqual(mark_values, sorted(mark_values, reverse=True))


    def test_sort_by_email_asc(self) -> None:
 
        ll = _load_ll(self.data_dir)

        start   = time.time()
        ll.sort(key="email_address", reverse=False)
        elapsed = time.time() - start

        print(f"\n  [TIMING] Sort by email ascending (1 000 records): {elapsed:.6f} seconds")

        records = ll.traverse()
        emails  = [r["email_address"].lower() for r in records]
        self.assertEqual(emails, sorted(emails))


    def test_sort_by_email_desc(self) -> None:
        ll = _load_ll(self.data_dir)

        start   = time.time()
        ll.sort(key="email_address", reverse=True)
        elapsed = time.time() - start

        print(f"\n  [TIMING] Sort by email descending (1 000 records): {elapsed:.6f} seconds")

        records = ll.traverse()
        emails  = [r["email_address"].lower() for r in records]
        self.assertEqual(emails, sorted(emails, reverse=True))


class TestCourseRecords(unittest.TestCase):

    def setUp(self) -> None:
        self.data_dir = tempfile.mkdtemp()
        _seed_dir(self.data_dir)

    def tearDown(self) -> None:
        shutil.rmtree(self.data_dir)


    def test_add_course(self) -> None:
        result = Course.add_new_course(
            "DATA301", "Machine Learning", "Fundamentals of ML and predictive modelling", 3,
            data_dir=self.data_dir,
        )
        self.assertIsNotNone(result)
        self.assertEqual(result["course_id"],   3003)
        self.assertEqual(result["course_code"], "DATA301")
        self.assertEqual(result["course_name"], "Machine Learning")

        rows = _read_csv(os.path.join(self.data_dir, "courses.csv"))

        self.assertEqual(len(rows), 3)
        codes = [r["course_code"] for r in rows]
        self.assertIn("DATA301", codes)


    def test_delete_course(self) -> None:

        ok = Course.delete_course(3001, data_dir=self.data_dir)
        self.assertTrue(ok)

        rows = _read_csv(os.path.join(self.data_dir, "courses.csv"))
        self.assertFalse(any(int(r["course_id"]) == 3001 for r in rows))

        self.assertEqual(len(rows), 1)

        miss = Course.delete_course(9999, data_dir=self.data_dir)
        self.assertFalse(miss)


    def test_modify_course(self) -> None:

        ok = Course.modify_course(
            3001,
            course_name = "Advanced Programming for Data Analytics",
            credits     = 4,
            data_dir    = self.data_dir,
        )
        self.assertTrue(ok)

        rows = _read_csv(os.path.join(self.data_dir, "courses.csv"))
        row  = next(r for r in rows if int(r["course_id"]) == 3001)
        self.assertEqual(row["course_name"], "Advanced Programming for Data Analytics")
        self.assertEqual(int(row["credits"]), 4)
        self.assertEqual(row["course_code"], "DATA200")

        miss = Course.modify_course(9999, course_name="Ghost", data_dir=self.data_dir)
        self.assertFalse(miss)


class TestProfessorRecords(unittest.TestCase):

    def setUp(self) -> None:
        self.data_dir = tempfile.mkdtemp()
        _seed_dir(self.data_dir)

    def tearDown(self) -> None:
        shutil.rmtree(self.data_dir)

    def test_add_professor(self) -> None:
        result = Professor.add_new_professor(
            "jimmy@sjsu.edu", "Jimmy Page", "Lecturer", "LucaIsCool2",
            course_ids=[3001],
            data_dir=self.data_dir,
        )
        self.assertIsNotNone(result)
        self.assertEqual(result["professor_id"],   2002)
        self.assertEqual(result["professor_name"], "Jimmy Page")
        self.assertEqual(result["rank"],           "Lecturer")

        rows = _read_csv(os.path.join(self.data_dir, "professors.csv"))
        self.assertEqual(len(rows), 2)
        emails = [r["email_address"] for r in rows]
        self.assertIn("jimmy@sjsu.edu", emails)

        login_rows = _read_csv(os.path.join(self.data_dir, "login.csv"))
        prof_login = next(
            (r for r in login_rows if r["email_address"] == "jimmy@sjsu.edu"), None
        )
        self.assertIsNotNone(prof_login)
        self.assertEqual(prof_login["role"], "professor")
        self.assertEqual(decrypt_password(prof_login["password"]), "LucaIsCool2")

        dup = Professor.add_new_professor(
            "jimmy@sjsu.edu", "Jimmy Page", "Lecturer", "LucaIsCool2",
            data_dir=self.data_dir,
        )
        self.assertIsNone(dup)


    def test_delete_professor(self) -> None:
        Professor.add_new_professor(
            "jimmy@sjsu.edu", "Jimmy Page", "Lecturer", "LucaIsCool2",
            data_dir=self.data_dir,
        )

        ok = Professor.delete_professor(2002, data_dir=self.data_dir)
        self.assertTrue(ok)

        rows = _read_csv(os.path.join(self.data_dir, "professors.csv"))
        self.assertFalse(any(int(r["professor_id"]) == 2002 for r in rows))

        login_rows = _read_csv(os.path.join(self.data_dir, "login.csv"))
        self.assertFalse(any(r["email_address"] == "jimmy@sjsu.edu" for r in login_rows))

        miss = Professor.delete_professor(9999, data_dir=self.data_dir)
        self.assertFalse(miss)


    def test_modify_professor(self) -> None:
        ok = Professor.modify_professor(
            2001, rank="Distinguished Professor", data_dir=self.data_dir
        )
        self.assertTrue(ok)

        rows = _read_csv(os.path.join(self.data_dir, "professors.csv"))
        row  = next(r for r in rows if int(r["professor_id"]) == 2001)
        self.assertEqual(row["rank"],           "Distinguished Professor")
        self.assertEqual(row["professor_name"], "Luca Popescu")

        ok = Professor.modify_professor(
            2001, new_email="luca.popescu@sjsu.edu", data_dir=self.data_dir
        )
        self.assertTrue(ok)
        login_rows = _read_csv(os.path.join(self.data_dir, "login.csv"))
        self.assertFalse(any(r["email_address"] == "luca@sjsu.edu"         for r in login_rows))
        self.assertTrue( any(r["email_address"] == "luca.popescu@sjsu.edu" for r in login_rows))

        miss = Professor.modify_professor(9999, rank="Ghost", data_dir=self.data_dir)
        self.assertFalse(miss)


if __name__ == "__main__":
    unittest.main(verbosity=2)