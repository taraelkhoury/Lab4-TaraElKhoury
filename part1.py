import json
import re


def valid_email(email):
    return re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email) is not None


class Person:
    def __init__(self, name, age, email):
        if not name.strip():
            raise ValueError("Name cannot be empty")
        if int(age) < 0:
            raise ValueError("Age cannot be negative")
        if not valid_email(email):
            raise ValueError("Invalid email")
        self.name = name.strip()
        self.age = int(age)
        self._email = email.strip()

    @property
    def email(self):
        return self._email

    @email.setter
    def email(self, value):
        if not valid_email(value):
            raise ValueError("Invalid email")
        self._email = value.strip()

    def introduce(self):
        return f"Hello, my name is {self.name} and I am {self.age} years old."


class Student(Person):
    def __init__(self, name, age, email, student_id, registered_courses=None):
        super().__init__(name, age, email)
        if not student_id.strip():
            raise ValueError("Student ID cannot be empty")
        self.student_id = student_id.strip()
        self.registered_courses = registered_courses or []

    def register_course(self, course):
        if course not in self.registered_courses:
            self.registered_courses.append(course)
        if self not in course.enrolled_students:
            course.enrolled_students.append(self)

    def unregister_course(self, course):
        if course in self.registered_courses:
            self.registered_courses.remove(course)
        if self in course.enrolled_students:
            course.enrolled_students.remove(self)


class Instructor(Person):
    def __init__(self, name, age, email, instructor_id, assigned_courses=None):
        super().__init__(name, age, email)
        if not instructor_id.strip():
            raise ValueError("Instructor ID cannot be empty")
        self.instructor_id = instructor_id.strip()
        self.assigned_courses = assigned_courses or []

    def assign_course(self, course):
        if course.instructor is not None and course.instructor is not self:
            old_instructor = course.instructor
            if course in old_instructor.assigned_courses:
                old_instructor.assigned_courses.remove(course)
        course.instructor = self
        if course not in self.assigned_courses:
            self.assigned_courses.append(course)

    def remove_course(self, course):
        if course in self.assigned_courses:
            self.assigned_courses.remove(course)
        if course.instructor is self:
            course.instructor = None


class Course:
    def __init__(self, course_id, course_name):
        if not course_id.strip() or not course_name.strip():
            raise ValueError("Course ID and name cannot be empty")
        self.course_id = course_id.strip()
        self.course_name = course_name.strip()
        self.instructor = None
        self.enrolled_students = []

    def add_student(self, student):
        student.register_course(self)


def save_data(students, instructors, courses, filename="school_data.json"):
    data = {
        "students": [
            {
                "name": student.name,
                "age": student.age,
                "email": student.email,
                "student_id": student.student_id,
                "registered_courses": [
                    course.course_id for course in student.registered_courses
                ]
            }
            for student in students
        ],
        "instructors": [
            {
                "name": instructor.name,
                "age": instructor.age,
                "email": instructor.email,
                "instructor_id": instructor.instructor_id,
                "assigned_courses": [
                    course.course_id for course in instructor.assigned_courses
                ]
            }
            for instructor in instructors
        ],
        "courses": [
            {
                "course_id": course.course_id,
                "course_name": course.course_name,
                "instructor_id": (
                    course.instructor.instructor_id if course.instructor else None
                ),
                "enrolled_students": [
                    student.student_id for student in course.enrolled_students
                ]
            }
            for course in courses
        ]
    }
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)


def load_data(filename="school_data.json"):
    with open(filename, "r", encoding="utf-8") as file:
        data = json.load(file)

    courses = [
        Course(item["course_id"], item["course_name"])
        for item in data.get("courses", [])
    ]
    students = [
        Student(item["name"], item["age"], item["email"], item["student_id"])
        for item in data.get("students", [])
    ]
    instructors = [
        Instructor(
            item["name"], item["age"], item["email"], item["instructor_id"]
        )
        for item in data.get("instructors", [])
    ]

    course_by_id = {course.course_id: course for course in courses}
    student_by_id = {student.student_id: student for student in students}
    instructor_by_id = {
        instructor.instructor_id: instructor for instructor in instructors
    }

    for item in data.get("courses", []):
        course = course_by_id[item["course_id"]]
        instructor_id = item.get("instructor_id")
        if instructor_id in instructor_by_id:
            instructor_by_id[instructor_id].assign_course(course)
        for student_id in item.get("enrolled_students", []):
            if student_id in student_by_id:
                student_by_id[student_id].register_course(course)

    return students, instructors, courses


if __name__ == "__main__":
    print("Part 1 contains the OOP classes, validation, and save/load functions.")
