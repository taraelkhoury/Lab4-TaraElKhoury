# EECE435L – Lab 4

## Overview

This repository contains my implementation of **Lab 4 for EECE435L**.

The purpose of this lab is to practice using **Git and GitHub** while integrating different graphical user interfaces into a Python application. The project includes both **Tkinter** and **PyQt** interfaces connected to the same student/course management system.

The project was completed individually.

## Features

The application provides functionality for managing:

- Students
- Instructors
- Courses
- Course registrations
- Instructor course assignments

The system uses object-oriented programming concepts to represent the different entities and their relationships.

## User Interfaces

Two graphical user interfaces are included in the project.

### Tkinter

The Tkinter interface allows the user to interact with the system through a simple Python GUI.

It can be used to:

- Add students and instructors
- Create courses
- Register students in courses
- Assign instructors to courses
- View stored records

### PyQt

The PyQt interface provides another graphical interface for interacting with the same application data and functionality.

It supports the main operations of the student and course management system through PyQt widgets.

## Technologies Used

- Python 3
- Tkinter
- PyQt5
- Object-Oriented Programming
- Git
- GitHub

## Installation

Clone the repository:

```bash
git clone https://github.com/taraelkhoury/Lab4-TaraElKhoury.git
```

Move into the project directory:

```bash
cd Lab4-TaraElKhoury
```

Install PyQt5 if it is not already installed:

```bash
pip install PyQt5
```

Tkinter is normally included with Python.

## Running the Project

The project contains separate interfaces for **Tkinter** and **PyQt**.

Run the corresponding Python file for the interface you want to use:

```bash
python part2.py
```

or

```bash
python part3.py
```

The applications can then be used to create and manage students, instructors, courses, and enrollments.

## Project Structure

The project separates the application logic from the graphical interfaces.

The backend contains the classes and functions used to manage:

- `Person`
- `Student`
- `Instructor`
- `Course`

The GUI files provide the Tkinter and PyQt interfaces that interact with this backend.

## GitHub Workflow

Since this lab was completed individually, development was done directly in the repository without the collaborator workflow required for a two-person group.

The completed implementation, testing, and documentation are stored in the `main` branch.

## Author

**Tara El Khoury**

American University of Beirut  
EECE435L