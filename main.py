
# PRE-SEEDED PROFESSOR CREDENTIALS:
#   Email   : luca@sjsu.edu
#   Password: LucaIsCool1


import os
import time

from data_structures import HashTable, LinkedList
from models import (
    User, Student, Professor, Course, Grades,
    _read_csv, LOGIN_FIELDS
)

DATA_DIR = "data/"

login_hash_table: HashTable = HashTable()

student_linked_list: LinkedList = LinkedList()

current_user: dict | None = None 


def load_data() -> None:
    global login_hash_table, student_linked_list

    login_hash_table   = HashTable()
    student_linked_list = LinkedList()

    for row in _read_csv(os.path.join(DATA_DIR, "login.csv")):
        login_hash_table.put(
            row["email_address"],
            {"password": row["password"], "role": row["role"]},
        )

    for row in _read_csv(os.path.join(DATA_DIR, "students.csv")):
        student_linked_list.insert({
            "student_id":    int(row["student_id"]),
            "email_address": row["email_address"],
            "first_name":    row["first_name"],
            "last_name":     row["last_name"],
        })


def clear() -> None:
    os.system("cls" if os.name == "nt" else "clear")


def divider(char: str = "-", width: int = 56) -> None:
    print(f"  {char * width}")


def header(title: str) -> None:
    print()
    divider("-")
    print(f"  {title}")
    divider("-")


def pause() -> None:
    pass


def prompt(label: str) -> str:
    return input(f"  {label}: ").strip()


def confirm(message: str) -> bool:
    answer = input(f"  {message} (y/n): ").strip().lower()
    return answer == "y"


def get_int(label: str) -> int | None:
    raw = prompt(label)
    try:
        return int(raw)
    except ValueError:
        print("  Invalid input — please enter a number.")
        return None


def _get_student_id_by_email(email: str) -> int | None:
    for row in _read_csv(os.path.join(DATA_DIR, "students.csv")):
        if row["email_address"] == email:
            return int(row["student_id"])
    return None


def _get_professor_id_by_email(email: str) -> int | None:
    for row in _read_csv(os.path.join(DATA_DIR, "professors.csv")):
        if row["email_address"] == email:
            return int(row["professor_id"])
    return None


def do_login() -> bool:
    global current_user

    header("Login")
    email    = prompt("Email")
    password = prompt("Password")

    record = User.login(email, password, login_hash_table)
    if record is None:
        print("\n  Incorrect email or password. Please try again.")
        pause()
        return False

    role = record["role"]
    uid  = (
        _get_student_id_by_email(email)
        if role == "student"
        else _get_professor_id_by_email(email)
    )

    current_user = {"email": email, "role": role, "id": uid}
    print(f"\n  Welcome back! Logged in as {role}.")
    pause()
    return True


def do_register() -> None:
    header("Student Registration")
    email     = prompt("Email address")
    first     = prompt("First name")
    last      = prompt("Last name")
    password  = prompt("Password")
    password2 = prompt("Confirm password")

    if password != password2:
        print("\n  Passwords do not match. Registration cancelled.")
        pause()
        return

    result = Student.add_new_student(email, first, last, password, data_dir=DATA_DIR)
    if result is None:
        print("\n  That email address is already registered.")
        pause()
        return

    from utils import encrypt_password
    login_hash_table.put(email, {"password": encrypt_password(password), "role": "student"})

    student_linked_list.insert({
        "student_id":    result["student_id"],
        "email_address": email,
        "first_name":    first,
        "last_name":     last,
    })

    print(f"\n  Registration successful! Your student ID is {result['student_id']}.")
    print("  You can now log in.")
    pause()


def do_change_password() -> None:
    header("Change Password")
    old_pw  = prompt("Current password")
    new_pw  = prompt("New password")
    new_pw2 = prompt("Confirm new password")

    if new_pw != new_pw2:
        print("\n  Passwords do not match.")
        pause()
        return

    ok = User.change_password(
        current_user["email"], old_pw, new_pw,
        login_hash_table, data_dir=DATA_DIR
    )
    if ok:
        print("\n  Password changed successfully.")
    else:
        print("\n  Current password was incorrect.")
    pause()


def prof_menu_students() -> None:
    while True:
        header("Student Management")
        print("  1. Add student")
        print("  2. Delete student")
        print("  3. Modify student")
        print("  4. Search student")
        print("  5. Sort & display students")
        print("  6. Display all students")
        print("  0. Back")
        divider()
        choice = prompt("Select option")

        if choice == "1":
            _prof_add_student()
        elif choice == "2":
            _prof_delete_student()
        elif choice == "3":
            _prof_modify_student()
        elif choice == "4":
            _prof_search_student()
        elif choice == "5":
            _prof_sort_students()
        elif choice == "6":
            header("All Students")
            Student.display_records(data_dir=DATA_DIR)
            pause()
        elif choice == "0":
            break
        else:
            print("  Invalid option.")
            pause()


def _prof_add_student() -> None:
    header("Add Student")
    email    = prompt("Email address")
    first    = prompt("First name")
    last     = prompt("Last name")
    password = prompt("Temporary password")

    result = Student.add_new_student(email, first, last, password, data_dir=DATA_DIR)
    if result is None:
        print("\n  That email is already registered.")
    else:
        from utils import encrypt_password
        login_hash_table.put(email, {"password": encrypt_password(password), "role": "student"})
        student_linked_list.insert({
            "student_id":    result["student_id"],
            "email_address": email,
            "first_name":    first,
            "last_name":     last,
        })
        print(f"\n  Student added. ID: {result['student_id']}")
    pause()


def _prof_delete_student() -> None:
    header("Delete Student")
    sid = get_int("Student ID")
    if sid is None:
        pause()
        return

    email = None
    for row in _read_csv(os.path.join(DATA_DIR, "students.csv")):
        if int(row["student_id"]) == sid:
            email = row["email_address"]
            break

    if not confirm(f"Delete student {sid}? This also removes their enrollments"):
        return

    ok = Student.delete_student(sid, data_dir=DATA_DIR)
    if ok:
        student_linked_list.delete(sid)
        if email:
            login_hash_table.delete(email)
        print("\n  Student deleted.")
    else:
        print("\n  Student ID not found.")
    pause()


def _prof_modify_student() -> None:
    header("Modify Student")
    sid = get_int("Student ID")
    if sid is None:
        pause()
        return

    print("  Leave a field blank to keep the current value.")
    first     = prompt("New first name (or blank)")
    last      = prompt("New last name (or blank)")
    new_email = prompt("New email (or blank)")

    ok = Student.update_student(
        sid,
        first_name = first     or None,
        last_name  = last      or None,
        new_email  = new_email or None,
        data_dir   = DATA_DIR,
    )
    if ok:
        global student_linked_list
        student_linked_list = Student.load_linked_list(data_dir=DATA_DIR)
        print("\n  Student updated.")
    else:
        print("\n  Student ID not found.")
    pause()


def _prof_search_student() -> None:
    header("Search Student")
    print("  Search by:")
    print("  1. Student ID")
    print("  2. Email address")
    choice = prompt("Select option")

    if choice == "1":
        sid = get_int("Student ID")
        if sid is None:
            pause()
            return
        start  = time.time()
        result = student_linked_list.search(sid, "student_id")
        elapsed = time.time() - start
    elif choice == "2":
        email  = prompt("Email address")
        start  = time.time()
        result = student_linked_list.search(email, "email_address")
        elapsed = time.time() - start
    else:
        print("  Invalid option.")
        pause()
        return

    print(f"\n  Search completed in {elapsed:.6f} seconds.")
    if result:
        print(f"\n  ID       : {result['student_id']}")
        print(f"  Name     : {result['first_name']} {result['last_name']}")
        print(f"  Email    : {result['email_address']}")
    else:
        print("\n  No student found.")
    pause()


def _prof_sort_students() -> None:
    header("Sort & Display Students")
    print("  Sort by:")
    print("  1. Last name (A → Z)")
    print("  2. Last name (Z → A)")
    print("  3. Marks (low → high)")
    print("  4. Marks (high → low)")
    print("  5. Email (A → Z)")
    print("  6. Email (Z → A)")
    choice = prompt("Select option")

    sort_map = {
        "1": ("last_name",     False),
        "2": ("last_name",     True),
        "3": ("marks",         False),
        "4": ("marks",         True),
        "5": ("email_address", False),
        "6": ("email_address", True),
    }

    if choice not in sort_map:
        print("  Invalid option.")
        pause()
        return

    key, reverse = sort_map[choice]

    if key == "marks":
        enrollments = _read_csv(os.path.join(DATA_DIR, "enrollments.csv"))
        marks_by_student = {}
        for e in enrollments:
            sid = int(e["student_id"])
            marks_by_student.setdefault(sid, []).append(int(e["marks"]))

        ll_marks = LinkedList()
        for row in _read_csv(os.path.join(DATA_DIR, "students.csv")):
            sid = int(row["student_id"])
            avg = (
                round(sum(marks_by_student[sid]) / len(marks_by_student[sid]), 2)
                if sid in marks_by_student else 0
            )
            ll_marks.insert({
                "student_id":    sid,
                "email_address": row["email_address"],
                "first_name":    row["first_name"],
                "last_name":     row["last_name"],
                "marks":         avg,
            })

        start = time.time()
        ll_marks.sort(key="marks", reverse=reverse)
        elapsed = time.time() - start
        records = ll_marks.traverse()

        print(f"\n  Sort completed in {elapsed:.6f} seconds.")
        print(f"\n  {'ID':<8} {'First Name':<15} {'Last Name':<15} {'Avg Marks':<10} {'Email'}")
        divider()
        for r in records:
            print(f"  {r['student_id']:<8} {r['first_name']:<15} {r['last_name']:<15} {r['marks']:<10} {r['email_address']}")

    else:
        ll = Student.load_linked_list(data_dir=DATA_DIR)
        start = time.time()
        ll.sort(key=key, reverse=reverse)
        elapsed = time.time() - start
        records = ll.traverse()

        print(f"\n  Sort completed in {elapsed:.6f} seconds.")
        print(f"\n  {'ID':<8} {'First Name':<15} {'Last Name':<15} {'Email'}")
        divider()
        for r in records:
            print(f"  {r['student_id']:<8} {r['first_name']:<15} {r['last_name']:<15} {r['email_address']}")

    pause()


def prof_menu_courses() -> None:
    while True:
        header("Course Management")
        print("  1. Add course")
        print("  2. Delete course")
        print("  3. Modify course")
        print("  4. Display all courses")
        print("  0. Back")
        divider()
        choice = prompt("Select option")

        if choice == "1":
            _prof_add_course()
        elif choice == "2":
            _prof_delete_course()
        elif choice == "3":
            _prof_modify_course()
        elif choice == "4":
            header("All Courses")
            Course.display_courses(data_dir=DATA_DIR)
            pause()
        elif choice == "0":
            break
        else:
            print("  Invalid option.")
            pause()


def _prof_add_course() -> None:
    header("Add Course")
    code    = prompt("Course code (e.g. DATA200)")
    name    = prompt("Course name")
    desc    = prompt("Description")
    credits = get_int("Credits")
    if credits is None:
        pause()
        return
    result = Course.add_new_course(code, name, desc, credits, data_dir=DATA_DIR)
    print(f"\n  Course added. ID: {result['course_id']}")
    pause()


def _prof_delete_course() -> None:
    header("Delete Course")
    cid = get_int("Course ID")
    if cid is None:
        pause()
        return
    if not confirm(f"Delete course {cid}?"):
        return
    ok = Course.delete_course(cid, data_dir=DATA_DIR)
    print("\n  Course deleted." if ok else "\n  Course ID not found.")
    pause()


def _prof_modify_course() -> None:
    header("Modify Course")
    cid = get_int("Course ID")
    if cid is None:
        pause()
        return
    print("  Leave a field blank to keep the current value.")
    code    = prompt("New course code (or blank)")
    name    = prompt("New course name (or blank)")
    desc    = prompt("New description (or blank)")
    credits_raw = prompt("New credits (or blank)")
    credits = int(credits_raw) if credits_raw else None

    ok = Course.modify_course(
        cid,
        course_code  = code  or None,
        course_name  = name  or None,
        description  = desc  or None,
        credits      = credits,
        data_dir     = DATA_DIR,
    )
    print("\n  Course updated." if ok else "\n  Course ID not found.")
    pause()


def prof_menu_professors() -> None:
    while True:
        header("Professor Management")
        print("  1. Add professor")
        print("  2. Delete professor")
        print("  3. Modify professor")
        print("  4. Display all professors")
        print("  5. View my courses")
        print("  0. Back")
        divider()
        choice = prompt("Select option")

        if choice == "1":
            _prof_add_professor()
        elif choice == "2":
            _prof_delete_professor()
        elif choice == "3":
            _prof_modify_professor()
        elif choice == "4":
            header("All Professors")
            Professor.display_records(data_dir=DATA_DIR)
            pause()
        elif choice == "5":
            header("My Courses")
            Professor.show_course_by_professor(current_user["id"], data_dir=DATA_DIR)
            pause()
        elif choice == "0":
            break
        else:
            print("  Invalid option.")
            pause()


def _prof_add_professor() -> None:
    header("Add Professor")
    email    = prompt("Email address")
    name     = prompt("Professor name")
    rank     = prompt("Rank (e.g. Senior Professor, Lecturer)")
    password = prompt("Temporary password")

    result = Professor.add_new_professor(email, name, rank, password, data_dir=DATA_DIR)
    if result is None:
        print("\n  That email is already registered.")
    else:
        from utils import encrypt_password
        login_hash_table.put(email, {"password": encrypt_password(password), "role": "professor"})
        print(f"\n  Professor added. ID: {result['professor_id']}")
    pause()


def _prof_delete_professor() -> None:
    header("Delete Professor")
    pid = get_int("Professor ID")
    if pid is None:
        pause()
        return
    if pid == current_user["id"]:
        print("\n  You cannot delete your own account.")
        pause()
        return
    if not confirm(f"Delete professor {pid}?"):
        return
    ok = Professor.delete_professor(pid, data_dir=DATA_DIR)
    if ok:
        print("\n  Professor deleted.")
    else:
        print("\n  Professor ID not found.")
    pause()


def _prof_modify_professor() -> None:
    header("Modify Professor")
    pid = get_int("Professor ID")
    if pid is None:
        pause()
        return
    print("  Leave a field blank to keep the current value.")
    name      = prompt("New name (or blank)")
    rank      = prompt("New rank (or blank)")
    new_email = prompt("New email (or blank)")

    ok = Professor.modify_professor(
        pid,
        professor_name = name      or None,
        rank           = rank      or None,
        new_email      = new_email or None,
        data_dir       = DATA_DIR,
    )
    print("\n  Professor updated." if ok else "\n  Professor ID not found.")
    pause()


def prof_menu_enrollments() -> None:
    while True:
        header("Enrollment & Grade Management")
        print("  1. Assign / update grade")
        print("  2. Delete enrollment")
        print("  0. Back")
        divider()
        choice = prompt("Select option")

        if choice == "1":
            _prof_assign_grade()
        elif choice == "2":
            _prof_delete_enrollment()
        elif choice == "0":
            break
        else:
            print("  Invalid option.")
            pause()


def _prof_assign_grade() -> None:
    header("Assign / Update Grade")
    sid = get_int("Student ID")
    if sid is None:
        pause()
        return
    cid = get_int("Course ID")
    if cid is None:
        pause()
        return
    marks = get_int("Marks (0–100)")
    if marks is None:
        pause()
        return

    result = Grades.add_grade(sid, cid, marks, data_dir=DATA_DIR)
    if result is None:
        print("\n  Invalid marks value (must be 0–100).")
    else:
        print(f"\n  Grade assigned: {result['marks']} → {result['grade']}")
    pause()


def _prof_delete_enrollment() -> None:
    header("Delete Enrollment")
    sid = get_int("Student ID")
    if sid is None:
        pause()
        return
    cid = get_int("Course ID")
    if cid is None:
        pause()
        return
    if not confirm(f"Remove enrollment for student {sid} in course {cid}?"):
        return
    ok = Grades.delete_grade(sid, cid, data_dir=DATA_DIR)
    print("\n  Enrollment removed." if ok else "\n  Enrollment not found.")
    pause()


def prof_menu_reports() -> None:
    while True:
        header("Reports & Statistics")
        print("  1. Grade report by course")
        print("  2. Grade report by professor")
        print("  3. Grade report by student")
        print("  4. Average score by course")
        print("  5. Median score by course")
        print("  0. Back")
        divider()
        choice = prompt("Select option")

        if choice == "1":
            header("Grade Report — By Course")
            cid = get_int("Course ID")
            if cid:
                Grades.display_grade_report("course", cid, data_dir=DATA_DIR)
            pause()
        elif choice == "2":
            header("Grade Report — By Professor")
            pid = get_int("Professor ID")
            if pid:
                Grades.display_grade_report("professor", pid, data_dir=DATA_DIR)
            pause()
        elif choice == "3":
            header("Grade Report — By Student")
            sid = get_int("Student ID")
            if sid:
                Grades.display_grade_report("student", sid, data_dir=DATA_DIR)
            pause()
        elif choice == "4":
            header("Average Score — By Course")
            cid = get_int("Course ID")
            if cid:
                avg = Grades.average_score(cid, data_dir=DATA_DIR)
                if avg is None:
                    print("  No enrollments found for that course.")
                else:
                    print(f"\n  Average score: {avg}")
            pause()
        elif choice == "5":
            header("Median Score — By Course")
            cid = get_int("Course ID")
            if cid:
                med = Grades.median_score(cid, data_dir=DATA_DIR)
                if med is None:
                    print("  No enrollments found for that course.")
                else:
                    print(f"\n  Median score: {med}")
            pause()
        elif choice == "0":
            break
        else:
            print("  Invalid option.")
            pause()


def professor_menu() -> None:
    while True:
        header(f"Professor Menu  [{current_user['email']}]")
        print("  1. Student Management")
        print("  2. Course Management")
        print("  3. Professor Management")
        print("  4. Enrollment & Grades")
        print("  5. Reports & Statistics")
        print("  6. Change Password")
        print("  7. Logout")
        divider()
        choice = prompt("Select option")

        if choice == "1":
            prof_menu_students()
        elif choice == "2":
            prof_menu_courses()
        elif choice == "3":
            prof_menu_professors()
        elif choice == "4":
            prof_menu_enrollments()
        elif choice == "5":
            prof_menu_reports()
        elif choice == "6":
            do_change_password()
        elif choice == "7":
            User.logout()
            print("\n  Logged out successfully.")
            pause()
            break
        else:
            print("  Invalid option.")
            pause()


def _student_enroll() -> None:
    header("Enroll in a Course")
    Course.display_courses(data_dir=DATA_DIR)
    cid = get_int("\n  Enter Course ID to enroll in")
    if cid is None:
        pause()
        return

    courses = _read_csv(os.path.join(DATA_DIR, "courses.csv"))
    if not any(int(c["course_id"]) == cid for c in courses):
        print("\n  Course not found.")
        pause()
        return

    Grades.enroll_student(current_user["id"], cid, data_dir=DATA_DIR)
    print("\n  Enrolled successfully.")
    pause()


def _student_unenroll() -> None:
    header("Unenroll from a Course")
    my_rows = Student.check_my_grades(current_user["id"], data_dir=DATA_DIR)
    if not my_rows:
        pause()
        return

    cid = get_int("\n  Enter Course ID to unenroll from")
    if cid is None:
        pause()
        return

    ok = Grades.delete_grade(current_user["id"], cid, data_dir=DATA_DIR)
    print("\n  Unenrolled successfully." if ok else "\n  You are not enrolled in that course.")
    pause()


def student_menu() -> None:
    while True:
        header(f"Student Menu  [{current_user['email']}]")
        print("  1. View my grades")
        print("  2. View all courses")
        print("  3. Enroll in a course")
        print("  4. Unenroll from a course")
        print("  5. Change password")
        print("  6. Logout")
        divider()
        choice = prompt("Select option")

        if choice == "1":
            header("My Grades")
            Student.check_my_grades(current_user["id"], data_dir=DATA_DIR)
            pause()
        elif choice == "2":
            header("All Courses")
            Course.display_courses(data_dir=DATA_DIR)
            pause()
        elif choice == "3":
            _student_enroll()
        elif choice == "4":
            _student_unenroll()
        elif choice == "5":
            do_change_password()
        elif choice == "6":
            User.logout()
            print("\n  Logged out successfully.")
            pause()
            break
        else:
            print("  Invalid option.")
            pause()


def welcome_menu() -> None:
    global current_user
    while True:
        header("Welcome to CheckMyGrade")
        print("  1. Login")
        print("  2. Register (students only)")
        print("  3. Exit")
        divider()
        choice = prompt("Select option")

        if choice == "1":
            success = do_login()
            if success:
                if current_user["role"] == "professor":
                    professor_menu()
                else:
                    student_menu()
                current_user = None

        elif choice == "2":
            do_register()

        elif choice == "3":
            print("\n  Goodbye!\n")
            break

        else:
            print("  Invalid option.")
            pause()


if __name__ == "__main__":
    load_data()
    welcome_menu()