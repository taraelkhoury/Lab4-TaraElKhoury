import tkinter as tk
from tkinter import ttk, messagebox
from part1 import Student, Instructor, Course, save_data, load_data


students = []
instructors = []
courses = []


def unique_id(items, attribute, value):
    return all(getattr(item, attribute) != value for item in items)


def selected_course(course_box):
    course_id = course_box.get().split(" - ")[0]
    return next((course for course in courses if course.course_id == course_id), None)


def add_student():
    try:
        if not unique_id(students, "student_id", student_id.get().strip()):
            raise ValueError("Student ID already exists")
        student = Student(
            student_name.get(), student_age.get(), student_email.get(),
            student_id.get()
        )
        course = selected_course(student_course)
        if course:
            student.register_course(course)
        students.append(student)
        refresh_table()
        clear_student_form()
    except ValueError as error:
        messagebox.showerror("Error", str(error))


def add_instructor():
    try:
        if not unique_id(instructors, "instructor_id", instructor_id.get().strip()):
            raise ValueError("Instructor ID already exists")
        instructor = Instructor(
            instructor_name.get(), instructor_age.get(), instructor_email.get(),
            instructor_id.get()
        )
        course = selected_course(instructor_course)
        if course:
            instructor.assign_course(course)
        instructors.append(instructor)
        refresh_table()
        clear_instructor_form()
    except ValueError as error:
        messagebox.showerror("Error", str(error))


def add_course():
    try:
        if not unique_id(courses, "course_id", course_id.get().strip()):
            raise ValueError("Course ID already exists")
        courses.append(Course(course_id.get(), course_name.get()))
        update_dropdowns()
        refresh_table()
        course_id.delete(0, tk.END)
        course_name.delete(0, tk.END)
    except ValueError as error:
        messagebox.showerror("Error", str(error))


def register_selected_student():
    selected = table.selection()
    course = selected_course(student_course)
    if not selected or not course:
        messagebox.showerror("Error", "Select a student and a course")
        return
    record_type, record_id = table.item(selected[0])["values"][:2]
    if record_type != "Student":
        messagebox.showerror("Error", "The selected record is not a student")
        return
    student = next(s for s in students if s.student_id == str(record_id))
    student.register_course(course)
    refresh_table()


def assign_selected_instructor():
    selected = table.selection()
    course = selected_course(instructor_course)
    if not selected or not course:
        messagebox.showerror("Error", "Select an instructor and a course")
        return
    record_type, record_id = table.item(selected[0])["values"][:2]
    if record_type != "Instructor":
        messagebox.showerror("Error", "The selected record is not an instructor")
        return
    instructor = next(i for i in instructors if i.instructor_id == str(record_id))
    instructor.assign_course(course)
    refresh_table()


def update_selected():
    selected = table.selection()
    if not selected:
        messagebox.showerror("Error", "Select a record first")
        return
    record_type, record_id = table.item(selected[0])["values"][:2]
    record_id = str(record_id)
    try:
        if record_type == "Student":
            student = next(s for s in students if s.student_id == record_id)
            updated = Student(
                student_name.get(), student_age.get(), student_email.get(), record_id
            )
            student.name, student.age, student.email = updated.name, updated.age, updated.email
            course = selected_course(student_course)
            if course:
                student.register_course(course)
        elif record_type == "Instructor":
            instructor = next(i for i in instructors if i.instructor_id == record_id)
            updated = Instructor(
                instructor_name.get(), instructor_age.get(), instructor_email.get(), record_id
            )
            instructor.name = updated.name
            instructor.age = updated.age
            instructor.email = updated.email
            course = selected_course(instructor_course)
            if course:
                instructor.assign_course(course)
        else:
            course = next(c for c in courses if c.course_id == record_id)
            if not course_name.get().strip():
                raise ValueError("Course name cannot be empty")
            course.course_name = course_name.get().strip()
        update_dropdowns()
        refresh_table()
    except ValueError as error:
        messagebox.showerror("Error", str(error))


def delete_record():
    selected = table.selection()
    if not selected:
        return
    record_type, record_id = table.item(selected[0])["values"][:2]
    record_id = str(record_id)
    if record_type == "Student":
        student = next(s for s in students if s.student_id == record_id)
        for course in student.registered_courses[:]:
            student.unregister_course(course)
        students.remove(student)
    elif record_type == "Instructor":
        instructor = next(i for i in instructors if i.instructor_id == record_id)
        for course in instructor.assigned_courses[:]:
            instructor.remove_course(course)
        instructors.remove(instructor)
    else:
        course = next(c for c in courses if c.course_id == record_id)
        for student in course.enrolled_students[:]:
            student.unregister_course(course)
        if course.instructor:
            course.instructor.remove_course(course)
        courses.remove(course)
    update_dropdowns()
    refresh_table()


def refresh_table(*args):
    for row in table.get_children():
        table.delete(row)
    search = search_entry.get().lower()
    records = []
    for student in students:
        course_names = ", ".join(c.course_name for c in student.registered_courses)
        records.append(("Student", student.student_id, student.name, course_names))
    for instructor in instructors:
        course_names = ", ".join(c.course_name for c in instructor.assigned_courses)
        records.append(("Instructor", instructor.instructor_id, instructor.name, course_names))
    for course in courses:
        instructor_name = course.instructor.name if course.instructor else ""
        records.append(("Course", course.course_id, course.course_name, instructor_name))
    for record in records:
        if search in " ".join(str(value) for value in record).lower():
            table.insert("", "end", values=record)


def fill_form(event=None):
    selected = table.selection()
    if not selected:
        return
    record_type, record_id = table.item(selected[0])["values"][:2]
    record_id = str(record_id)
    if record_type == "Student":
        student = next(s for s in students if s.student_id == record_id)
        clear_student_form()
        student_name.insert(0, student.name)
        student_age.insert(0, str(student.age))
        student_email.insert(0, student.email)
        student_id.insert(0, student.student_id)
        if student.registered_courses:
            course = student.registered_courses[0]
            student_course.set(f"{course.course_id} - {course.course_name}")
        notebook.select(student_tab)
    elif record_type == "Instructor":
        instructor = next(i for i in instructors if i.instructor_id == record_id)
        clear_instructor_form()
        instructor_name.insert(0, instructor.name)
        instructor_age.insert(0, str(instructor.age))
        instructor_email.insert(0, instructor.email)
        instructor_id.insert(0, instructor.instructor_id)
        if instructor.assigned_courses:
            course = instructor.assigned_courses[0]
            instructor_course.set(f"{course.course_id} - {course.course_name}")
        notebook.select(instructor_tab)
    else:
        course = next(c for c in courses if c.course_id == record_id)
        course_id.delete(0, tk.END)
        course_name.delete(0, tk.END)
        course_id.insert(0, course.course_id)
        course_name.insert(0, course.course_name)
        notebook.select(course_tab)


def update_dropdowns():
    values = [f"{c.course_id} - {c.course_name}" for c in courses]
    student_course["values"] = values
    instructor_course["values"] = values


def save_file():
    save_data(students, instructors, courses)
    messagebox.showinfo("Saved", "All data and relationships were saved")


def load_file():
    global students, instructors, courses
    try:
        students, instructors, courses = load_data()
        update_dropdowns()
        refresh_table()
        messagebox.showinfo("Loaded", "Data loaded successfully")
    except (FileNotFoundError, ValueError) as error:
        messagebox.showerror("Error", str(error))


def clear_student_form():
    for entry in (student_name, student_age, student_email, student_id):
        entry.delete(0, tk.END)
    student_course.set("")


def clear_instructor_form():
    for entry in (instructor_name, instructor_age, instructor_email, instructor_id):
        entry.delete(0, tk.END)
    instructor_course.set("")


root = tk.Tk()
root.title("School Management System")
root.geometry("760x620")
notebook = ttk.Notebook(root)
notebook.pack(fill="both", expand=True)
student_tab, instructor_tab, course_tab, records_tab = [
    ttk.Frame(notebook) for _ in range(4)
]
for tab, title in zip(
    (student_tab, instructor_tab, course_tab, records_tab),
    ("Student", "Instructor", "Course", "Records")
):
    notebook.add(tab, text=title)


def make_entry(tab, label):
    ttk.Label(tab, text=label).pack()
    entry = ttk.Entry(tab)
    entry.pack()
    return entry


student_name = make_entry(student_tab, "Name")
student_age = make_entry(student_tab, "Age")
student_email = make_entry(student_tab, "Email")
student_id = make_entry(student_tab, "Student ID")
ttk.Label(student_tab, text="Course").pack()
student_course = ttk.Combobox(student_tab, state="readonly")
student_course.pack()
ttk.Button(student_tab, text="Add Student", command=add_student).pack(pady=10)
ttk.Button(
    student_tab, text="Register Selected Student in Another Course",
    command=register_selected_student
).pack()

instructor_name = make_entry(instructor_tab, "Name")
instructor_age = make_entry(instructor_tab, "Age")
instructor_email = make_entry(instructor_tab, "Email")
instructor_id = make_entry(instructor_tab, "Instructor ID")
ttk.Label(instructor_tab, text="Course").pack()
instructor_course = ttk.Combobox(instructor_tab, state="readonly")
instructor_course.pack()
ttk.Button(instructor_tab, text="Add Instructor", command=add_instructor).pack(pady=10)
ttk.Button(
    instructor_tab, text="Assign Another Course to Selected Instructor",
    command=assign_selected_instructor
).pack()

course_id = make_entry(course_tab, "Course ID")
course_name = make_entry(course_tab, "Course Name")
ttk.Button(course_tab, text="Add Course", command=add_course).pack(pady=10)

search_entry = ttk.Entry(records_tab)
search_entry.pack(fill="x", padx=10, pady=5)
search_entry.bind("<KeyRelease>", refresh_table)
table = ttk.Treeview(
    records_tab, columns=("Type", "ID", "Name", "Course"), show="headings"
)
for column in ("Type", "ID", "Name", "Course"):
    table.heading(column, text=column)
table.pack(fill="both", expand=True, padx=10, pady=5)
table.bind("<<TreeviewSelect>>", fill_form)
buttons = ttk.Frame(records_tab)
buttons.pack(pady=5)
for text, command in (
    ("Update Selected", update_selected), ("Delete", delete_record),
    ("Save", save_file), ("Load", load_file)
):
    ttk.Button(buttons, text=text, command=command).pack(side="left", padx=5)

root.mainloop()
