import os
import shutil
import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from part1 import valid_email


DATABASE = "school.db"
BACKUP = "school_backup.db"
connection = sqlite3.connect(DATABASE)
connection.execute("PRAGMA foreign_keys = ON")
cursor = connection.cursor()
cursor.executescript("""
CREATE TABLE IF NOT EXISTS students (
    student_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    age INTEGER NOT NULL CHECK(age >= 0),
    email TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS instructors (
    instructor_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    age INTEGER NOT NULL CHECK(age >= 0),
    email TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS courses (
    course_id TEXT PRIMARY KEY,
    course_name TEXT NOT NULL,
    instructor_id TEXT,
    FOREIGN KEY(instructor_id) REFERENCES instructors(instructor_id)
        ON DELETE SET NULL
);
CREATE TABLE IF NOT EXISTS enrollments (
    student_id TEXT,
    course_id TEXT,
    PRIMARY KEY(student_id, course_id),
    FOREIGN KEY(student_id) REFERENCES students(student_id) ON DELETE CASCADE,
    FOREIGN KEY(course_id) REFERENCES courses(course_id) ON DELETE CASCADE
);
""")
connection.commit()


def person_values():
    name = name_entry.get().strip()
    email = email_entry.get().strip()
    if not id_entry.get().strip() or not name:
        raise ValueError("ID and name cannot be empty")
    age = int(age_entry.get())
    if age < 0:
        raise ValueError("Age cannot be negative")
    if not valid_email(email):
        raise ValueError("Invalid email")
    return name, age, email


def selected_course_id():
    value = course_box.get()
    return value.split(" - ")[0] if value else None


def add_student():
    try:
        name, age, email = person_values()
        student_id = id_entry.get().strip()
        cursor.execute(
            "INSERT INTO students VALUES (?, ?, ?, ?)",
            (student_id, name, age, email)
        )
        course_id = selected_course_id()
        if course_id:
            cursor.execute("INSERT INTO enrollments VALUES (?, ?)", (student_id, course_id))
        connection.commit()
        refresh()
    except (ValueError, sqlite3.Error) as error:
        connection.rollback()
        messagebox.showerror("Error", str(error))


def add_instructor():
    try:
        name, age, email = person_values()
        instructor_id = id_entry.get().strip()
        cursor.execute(
            "INSERT INTO instructors VALUES (?, ?, ?, ?)",
            (instructor_id, name, age, email)
        )
        course_id = selected_course_id()
        if course_id:
            cursor.execute(
                "UPDATE courses SET instructor_id=? WHERE course_id=?",
                (instructor_id, course_id)
            )
        connection.commit()
        refresh()
    except (ValueError, sqlite3.Error) as error:
        connection.rollback()
        messagebox.showerror("Error", str(error))


def add_course():
    try:
        course_id = id_entry.get().strip()
        course_name = course_name_entry.get().strip()
        if not course_id or not course_name:
            raise ValueError("Course ID and name cannot be empty")
        cursor.execute("INSERT INTO courses VALUES (?, ?, NULL)", (course_id, course_name))
        connection.commit()
        update_courses()
        refresh()
    except (ValueError, sqlite3.Error) as error:
        connection.rollback()
        messagebox.showerror("Error", str(error))


def register_selected_student():
    selected = table.selection()
    course_id = selected_course_id()
    if not selected or not course_id:
        messagebox.showerror("Error", "Select a student and a course")
        return
    record_type, student_id = table.item(selected[0])["values"][:2]
    if record_type != "Student":
        messagebox.showerror("Error", "The selected record is not a student")
        return
    try:
        cursor.execute("INSERT INTO enrollments VALUES (?, ?)", (str(student_id), course_id))
        connection.commit()
        refresh()
    except sqlite3.IntegrityError:
        messagebox.showerror("Error", "Student is already registered in this course")


def assign_selected_instructor():
    selected = table.selection()
    course_id = selected_course_id()
    if not selected or not course_id:
        messagebox.showerror("Error", "Select an instructor and a course")
        return
    record_type, instructor_id = table.item(selected[0])["values"][:2]
    if record_type != "Instructor":
        messagebox.showerror("Error", "The selected record is not an instructor")
        return
    cursor.execute(
        "UPDATE courses SET instructor_id=? WHERE course_id=?",
        (str(instructor_id), course_id)
    )
    connection.commit()
    refresh()


def update_selected():
    selected = table.selection()
    if not selected:
        messagebox.showerror("Error", "Select a record first")
        return
    record_type, record_id = table.item(selected[0])["values"][:2]
    record_id = str(record_id)
    try:
        if record_type == "Student":
            name, age, email = person_values()
            cursor.execute(
                "UPDATE students SET name=?, age=?, email=? WHERE student_id=?",
                (name, age, email, record_id)
            )
            course_id = selected_course_id()
            if course_id:
                cursor.execute(
                    "INSERT OR IGNORE INTO enrollments VALUES (?, ?)",
                    (record_id, course_id)
                )
        elif record_type == "Instructor":
            name, age, email = person_values()
            cursor.execute(
                "UPDATE instructors SET name=?, age=?, email=? WHERE instructor_id=?",
                (name, age, email, record_id)
            )
            course_id = selected_course_id()
            if course_id:
                cursor.execute(
                    "UPDATE courses SET instructor_id=? WHERE course_id=?",
                    (record_id, course_id)
                )
        else:
            course_name = course_name_entry.get().strip()
            if not course_name:
                raise ValueError("Course name cannot be empty")
            cursor.execute(
                "UPDATE courses SET course_name=? WHERE course_id=?",
                (course_name, record_id)
            )
        connection.commit()
        update_courses()
        refresh()
    except (ValueError, sqlite3.Error) as error:
        connection.rollback()
        messagebox.showerror("Error", str(error))


def delete_selected():
    selected = table.selection()
    if not selected:
        return
    record_type, record_id = table.item(selected[0])["values"][:2]
    record_id = str(record_id)
    table_name = {
        "Student": ("students", "student_id"),
        "Instructor": ("instructors", "instructor_id"),
        "Course": ("courses", "course_id")
    }[record_type]
    cursor.execute(f"DELETE FROM {table_name[0]} WHERE {table_name[1]}=?", (record_id,))
    connection.commit()
    update_courses()
    refresh()


def refresh(*args):
    for row in table.get_children():
        table.delete(row)
    search = search_entry.get().lower()
    queries = (
        ("Student", """
            SELECT s.student_id, s.name, COALESCE(GROUP_CONCAT(c.course_name, ', '), '')
            FROM students s LEFT JOIN enrollments e ON s.student_id=e.student_id
            LEFT JOIN courses c ON e.course_id=c.course_id GROUP BY s.student_id
        """),
        ("Instructor", """
            SELECT i.instructor_id, i.name, COALESCE(GROUP_CONCAT(c.course_name, ', '), '')
            FROM instructors i LEFT JOIN courses c ON i.instructor_id=c.instructor_id
            GROUP BY i.instructor_id
        """),
        ("Course", """
            SELECT c.course_id, c.course_name, COALESCE(i.name, '')
            FROM courses c LEFT JOIN instructors i ON c.instructor_id=i.instructor_id
        """)
    )
    for record_type, query in queries:
        for row in cursor.execute(query).fetchall():
            record = (record_type,) + row
            if search in " ".join(str(value) for value in record).lower():
                table.insert("", "end", values=record)


def fill_form(event=None):
    selected = table.selection()
    if not selected:
        return
    record_type, record_id = table.item(selected[0])["values"][:2]
    record_id = str(record_id)
    clear_form()
    id_entry.insert(0, record_id)
    if record_type == "Student":
        result = cursor.execute(
            "SELECT name, age, email FROM students WHERE student_id=?", (record_id,)
        ).fetchone()
        course = cursor.execute(
            "SELECT course_id FROM enrollments WHERE student_id=?", (record_id,)
        ).fetchone()
    elif record_type == "Instructor":
        result = cursor.execute(
            "SELECT name, age, email FROM instructors WHERE instructor_id=?", (record_id,)
        ).fetchone()
        course = cursor.execute(
            "SELECT course_id FROM courses WHERE instructor_id=?", (record_id,)
        ).fetchone()
    else:
        result = cursor.execute(
            "SELECT course_name FROM courses WHERE course_id=?", (record_id,)
        ).fetchone()
        course_name_entry.insert(0, result[0])
        return
    name_entry.insert(0, result[0])
    age_entry.insert(0, str(result[1]))
    email_entry.insert(0, result[2])
    if course:
        for value in course_box["values"]:
            if value.startswith(course[0] + " - "):
                course_box.set(value)


def update_courses():
    values = [
        f"{course_id} - {course_name}"
        for course_id, course_name in cursor.execute(
            "SELECT course_id, course_name FROM courses ORDER BY course_id"
        )
    ]
    course_box["values"] = values


def backup_database():
    connection.commit()
    backup_connection = sqlite3.connect(BACKUP)
    connection.backup(backup_connection)
    backup_connection.close()
    messagebox.showinfo("Backup", "school_backup.db was created")


def restore_database():
    global connection, cursor
    if not os.path.exists(BACKUP):
        messagebox.showerror("Error", "No backup file was found")
        return
    connection.close()
    shutil.copy2(BACKUP, DATABASE)
    connection = sqlite3.connect(DATABASE)
    connection.execute("PRAGMA foreign_keys = ON")
    cursor = connection.cursor()
    update_courses()
    refresh()
    messagebox.showinfo("Restore", "Database restored")


def clear_form():
    for entry in (name_entry, age_entry, email_entry, id_entry, course_name_entry):
        entry.delete(0, tk.END)
    course_box.set("")


root = tk.Tk()
root.title("School Management System - SQLite")
root.geometry("780x650")


def entry(label):
    ttk.Label(root, text=label).pack()
    widget = ttk.Entry(root)
    widget.pack(fill="x", padx=20)
    return widget


name_entry = entry("Name")
age_entry = entry("Age")
email_entry = entry("Email")
id_entry = entry("ID")
course_name_entry = entry("Course Name")
ttk.Label(root, text="Course").pack()
course_box = ttk.Combobox(root, state="readonly")
course_box.pack(fill="x", padx=20)

buttons = ttk.Frame(root)
buttons.pack(pady=8)
for index, (text, command) in enumerate((
    ("Add Student", add_student), ("Add Instructor", add_instructor),
    ("Add Course", add_course), ("Update", update_selected),
    ("Delete", delete_selected), ("Backup", backup_database),
    ("Restore", restore_database), ("Register Course", register_selected_student),
    ("Assign Course", assign_selected_instructor)
)):
    ttk.Button(buttons, text=text, command=command).grid(
        row=index // 5, column=index % 5, padx=3, pady=3
    )

search_entry = ttk.Entry(root)
search_entry.pack(fill="x", padx=20, pady=5)
search_entry.bind("<KeyRelease>", refresh)
table = ttk.Treeview(root, columns=("Type", "ID", "Name", "Course"), show="headings")
for column in ("Type", "ID", "Name", "Course"):
    table.heading(column, text=column)
table.pack(fill="both", expand=True, padx=20, pady=5)
table.bind("<<TreeviewSelect>>", fill_form)

update_courses()
refresh()
root.protocol("WM_DELETE_WINDOW", lambda: (connection.close(), root.destroy()))
root.mainloop()
