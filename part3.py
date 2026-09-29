import csv
import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton,
    QComboBox, QTableWidget, QTableWidgetItem, QMessageBox
)
from part1 import Student, Instructor, Course, save_data, load_data


class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.students = []
        self.instructors = []
        self.courses = []
        self.setWindowTitle("School Management System")
        self.resize(760, 680)
        layout = QVBoxLayout(self)

        self.name = QLineEdit()
        self.name.setPlaceholderText("Name")
        self.age = QLineEdit()
        self.age.setPlaceholderText("Age")
        self.email = QLineEdit()
        self.email.setPlaceholderText("Email")
        self.record_id = QLineEdit()
        self.record_id.setPlaceholderText("Student, instructor, or course ID")
        self.course_name = QLineEdit()
        self.course_name.setPlaceholderText("Course Name")
        self.course_box = QComboBox()
        self.course_box.addItem("No course", None)

        for widget in (
            self.name, self.age, self.email, self.record_id,
            self.course_name, self.course_box
        ):
            layout.addWidget(widget)

        add_buttons = QHBoxLayout()
        for text, method in (
            ("Add Student", self.add_student),
            ("Add Instructor", self.add_instructor),
            ("Add Course", self.add_course),
            ("Register Course", self.register_course),
            ("Assign Course", self.assign_course)
        ):
            button = QPushButton(text)
            button.clicked.connect(method)
            add_buttons.addWidget(button)
        layout.addLayout(add_buttons)

        self.search = QLineEdit()
        self.search.setPlaceholderText("Search by name, ID, or course")
        self.search.textChanged.connect(self.refresh)
        layout.addWidget(self.search)

        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["Type", "ID", "Name", "Course"])
        self.table.cellClicked.connect(self.fill_form)
        layout.addWidget(self.table)

        action_buttons = QHBoxLayout()
        for text, method in (
            ("Update Selected", self.update_record),
            ("Delete Selected", self.delete_record),
            ("Save", self.save_file),
            ("Load", self.load_file),
            ("Export CSV", self.export_csv)
        ):
            button = QPushButton(text)
            button.clicked.connect(method)
            action_buttons.addWidget(button)
        layout.addLayout(action_buttons)

    def get_course(self):
        course_id = self.course_box.currentData()
        return next((c for c in self.courses if c.course_id == course_id), None)

    def id_exists(self, items, attribute, value):
        return any(getattr(item, attribute) == value for item in items)

    def add_student(self):
        try:
            student_id = self.record_id.text().strip()
            if self.id_exists(self.students, "student_id", student_id):
                raise ValueError("Student ID already exists")
            student = Student(
                self.name.text(), self.age.text(), self.email.text(), student_id
            )
            course = self.get_course()
            if course:
                student.register_course(course)
            self.students.append(student)
            self.refresh()
            self.clear_form()
        except ValueError as error:
            QMessageBox.warning(self, "Error", str(error))

    def add_instructor(self):
        try:
            instructor_id = self.record_id.text().strip()
            if self.id_exists(self.instructors, "instructor_id", instructor_id):
                raise ValueError("Instructor ID already exists")
            instructor = Instructor(
                self.name.text(), self.age.text(), self.email.text(), instructor_id
            )
            course = self.get_course()
            if course:
                instructor.assign_course(course)
            self.instructors.append(instructor)
            self.refresh()
            self.clear_form()
        except ValueError as error:
            QMessageBox.warning(self, "Error", str(error))

    def add_course(self):
        try:
            course_id = self.record_id.text().strip()
            if self.id_exists(self.courses, "course_id", course_id):
                raise ValueError("Course ID already exists")
            self.courses.append(Course(course_id, self.course_name.text()))
            self.update_course_box()
            self.refresh()
            self.clear_form()
        except ValueError as error:
            QMessageBox.warning(self, "Error", str(error))

    def register_course(self):
        try:
            record_type, record_id = self.selected_record()
            if record_type != "Student" or not self.get_course():
                raise ValueError("Select a student and a course")
            student = next(s for s in self.students if s.student_id == record_id)
            student.register_course(self.get_course())
            self.refresh()
        except ValueError as error:
            QMessageBox.warning(self, "Error", str(error))

    def assign_course(self):
        try:
            record_type, record_id = self.selected_record()
            if record_type != "Instructor" or not self.get_course():
                raise ValueError("Select an instructor and a course")
            instructor = next(i for i in self.instructors if i.instructor_id == record_id)
            instructor.assign_course(self.get_course())
            self.refresh()
        except ValueError as error:
            QMessageBox.warning(self, "Error", str(error))

    def records(self):
        result = []
        for student in self.students:
            names = ", ".join(c.course_name for c in student.registered_courses)
            result.append(("Student", student.student_id, student.name, names))
        for instructor in self.instructors:
            names = ", ".join(c.course_name for c in instructor.assigned_courses)
            result.append(("Instructor", instructor.instructor_id, instructor.name, names))
        for course in self.courses:
            instructor = course.instructor.name if course.instructor else ""
            result.append(("Course", course.course_id, course.course_name, instructor))
        return result

    def refresh(self):
        self.table.setRowCount(0)
        search_text = self.search.text().lower()
        for record in self.records():
            values = [str(value) for value in record]
            if search_text in " ".join(values).lower():
                row = self.table.rowCount()
                self.table.insertRow(row)
                for column, value in enumerate(values):
                    self.table.setItem(row, column, QTableWidgetItem(value))

    def selected_record(self):
        row = self.table.currentRow()
        if row < 0:
            raise ValueError("Select a record first")
        return self.table.item(row, 0).text(), self.table.item(row, 1).text()

    def fill_form(self, row, column):
        record_type = self.table.item(row, 0).text()
        record_id = self.table.item(row, 1).text()
        self.clear_form()
        self.record_id.setText(record_id)
        if record_type == "Student":
            item = next(s for s in self.students if s.student_id == record_id)
            self.name.setText(item.name)
            self.age.setText(str(item.age))
            self.email.setText(item.email)
            if item.registered_courses:
                self.course_box.setCurrentIndex(
                    self.course_box.findData(item.registered_courses[0].course_id)
                )
        elif record_type == "Instructor":
            item = next(i for i in self.instructors if i.instructor_id == record_id)
            self.name.setText(item.name)
            self.age.setText(str(item.age))
            self.email.setText(item.email)
            if item.assigned_courses:
                self.course_box.setCurrentIndex(
                    self.course_box.findData(item.assigned_courses[0].course_id)
                )
        else:
            item = next(c for c in self.courses if c.course_id == record_id)
            self.course_name.setText(item.course_name)

    def update_record(self):
        try:
            record_type, record_id = self.selected_record()
            if record_type == "Student":
                student = next(s for s in self.students if s.student_id == record_id)
                checked = Student(self.name.text(), self.age.text(), self.email.text(), record_id)
                student.name, student.age, student.email = checked.name, checked.age, checked.email
                if self.get_course():
                    student.register_course(self.get_course())
            elif record_type == "Instructor":
                instructor = next(i for i in self.instructors if i.instructor_id == record_id)
                checked = Instructor(self.name.text(), self.age.text(), self.email.text(), record_id)
                instructor.name = checked.name
                instructor.age = checked.age
                instructor.email = checked.email
                if self.get_course():
                    instructor.assign_course(self.get_course())
            else:
                course = next(c for c in self.courses if c.course_id == record_id)
                if not self.course_name.text().strip():
                    raise ValueError("Course name cannot be empty")
                course.course_name = self.course_name.text().strip()
                self.update_course_box()
            self.refresh()
        except ValueError as error:
            QMessageBox.warning(self, "Error", str(error))

    def delete_record(self):
        try:
            record_type, record_id = self.selected_record()
            if record_type == "Student":
                item = next(s for s in self.students if s.student_id == record_id)
                for course in item.registered_courses[:]:
                    item.unregister_course(course)
                self.students.remove(item)
            elif record_type == "Instructor":
                item = next(i for i in self.instructors if i.instructor_id == record_id)
                for course in item.assigned_courses[:]:
                    item.remove_course(course)
                self.instructors.remove(item)
            else:
                item = next(c for c in self.courses if c.course_id == record_id)
                for student in item.enrolled_students[:]:
                    student.unregister_course(item)
                if item.instructor:
                    item.instructor.remove_course(item)
                self.courses.remove(item)
                self.update_course_box()
            self.refresh()
        except ValueError as error:
            QMessageBox.warning(self, "Error", str(error))

    def save_file(self):
        save_data(self.students, self.instructors, self.courses)
        QMessageBox.information(self, "Saved", "All data and relationships were saved")

    def load_file(self):
        try:
            self.students, self.instructors, self.courses = load_data()
            self.update_course_box()
            self.refresh()
            QMessageBox.information(self, "Loaded", "Data loaded successfully")
        except (FileNotFoundError, ValueError) as error:
            QMessageBox.warning(self, "Error", str(error))

    def export_csv(self):
        with open("school_records.csv", "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["Type", "ID", "Name", "Course or Instructor"])
            writer.writerows(self.records())
        QMessageBox.information(self, "Export", "CSV file exported")

    def update_course_box(self):
        selected_id = self.course_box.currentData()
        self.course_box.clear()
        self.course_box.addItem("No course", None)
        for course in self.courses:
            self.course_box.addItem(
                f"{course.course_id} - {course.course_name}", course.course_id
            )
        index = self.course_box.findData(selected_id)
        if index >= 0:
            self.course_box.setCurrentIndex(index)

    def clear_form(self):
        for field in (self.name, self.age, self.email, self.record_id, self.course_name):
            field.clear()
        self.course_box.setCurrentIndex(0)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec_())
