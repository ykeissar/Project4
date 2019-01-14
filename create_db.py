import sqlite3


# ------------------------DAO-----------------
import sys


class _Courses:
    def __init__(self, conn):
        self._conn = conn

    def insert(self, course):
        self._conn.execute("""
        INSERT INTO courses VALUES(?,?,?,?,?,?)
        """, [course.id, course.course_name, course.student, course.number_of_students, course.class_id,
              course.course_length])

    def find(self, course_id):
        c = self._conn.cursor()
        c.execute("""
            SELECT * FROM courses WHERE id = ?
            """, [course_id])
        return Course(*c.fetchone())

    def print_table(self):
        for item in self.get_table():
            print(item)

    def get_table(self):
        c = self._conn.cursor()
        c.execute("""
               SELECT * FROM courses
           """)
        return c.fetchall()


class _Students:
    def __init__(self, conn):
        self._conn = conn

    def insert(self, student):
        self._conn.execute("""
        INSERT INTO students VALUES(?,?)
        """, [student.grade, student.count])

    def find(self, grade):
        c = self._conn.cursor()
        c.execute("""
            SELECT * FROM students WHERE grade = ?
            """, [grade])

        return Student(*c.fetchone())

    def print_table(self):
        for item in self.get_table():
            print(item)

    def get_table(self):
        c = self._conn.cursor()
        c.execute("""
                 SELECT * FROM students
             """)
        return c.fetchall()


class _Classrooms:
    def __init__(self, conn):
        self._conn = conn

    def insert(self, classroom):
        self._conn.execute("""
        INSERT INTO classrooms VALUES(?,?,?,?)
        """, [classroom.id, classroom.location, classroom.current_course_id, classroom.current_course_time_left])

    def find(self, id):
        c = self._conn.cursor()
        c.execute("""
            SELECT * FROM classrooms WHERE id = ?
            """, [id])

        return Classroom(*c.fetchone())

    def print_table(self):
        for item in self.get_table():
            print(item)

    def get_table(self):
        c = self._conn.cursor()
        c.execute("""
                   SELECT * FROM classrooms
               """)
        return c.fetchall()


class _Repository:
    def __init__(self):
        self._conn = sqlite3.connect('schedule.db')
        self.courses = _Courses(self._conn)
        self.students = _Students(self._conn)
        self.classrooms = _Classrooms(self._conn)

    def _close(self):
        self._conn.commit()
        self._conn.close()

    def create_tables(self):
        self._conn.executescript("""
        CREATE TABLE courses (
            id INTEGER PRIMARY KEY,
            course_name TEXT NOT NULL,
            student TEXT NOT NULL,
            number_of_students INTEGER NOT NULL,
            class_id INTEGER REFERENCES classrooms(id),
            course_length INTEGER NOT NULL
        );

        CREATE TABLE students (
            grade TEXT PRIMARY KEY,
            count INTEGER NOT NULL
        );

        CREATE TABLE classrooms (
            id INTEGER PRIMARY KEY,
            location TEXT NOT NULL,
            current_course_id INTEGER NOT NULL,
            current_course_time_left INTEGER NOT NULL
        );
         """)

    def close_tables(self):
        c = self._conn.cursor()
        c.execute("""DROP TABLE courses
                     DROP TABLE students
                     DROP TABLE classrooms
        """)

    def print_tables(self):
        print("courses")
        self.courses.print_table()
        print("classrooms")
        self.classrooms.print_table()
        print("students")
        self.students.print_table()

    def check_if_exist(self):
        c = self._conn.cursor()
        c.execute("""
                           SELECT count(*) FROM sqlite_master WHERE type='table' AND name='students' 
                       """)
        return c.fetchone()[0]


# ----------------------DTO---------------------
class Course:
    def __init__(self, id, course_name, student, number_of_students, class_id, course_length):
        self.id = id
        self.course_name = course_name
        self.student = student
        self.number_of_students = number_of_students
        self.class_id = class_id
        self.course_length = course_length


class Student:
    def __init__(self, grade, count):
        self.count = count
        self.grade = grade


class Classroom:
    def __init__(self, id, location):
        self.current_course_time_left = 0
        self.current_course_id = 0
        self.location = location
        self.id = id


# -------------------SetupDB--------------------
if __name__ == "__main__":
    rep = _Repository()
    if rep.check_if_exist() is not 1:
        rep.create_tables()
        f = open(sys.argv[1], 'r')
        lines = f.readlines()
        for line in lines:
            s = line.split(', ')
            if s[0] is 'S':
                s[2] = s[2].replace('\n', '')
                rep.students.insert(Student(s[1], s[2]))
            if s[0] is 'R':
                s[2] = s[2].replace('\n', '')
                rep.classrooms.insert(Classroom(s[1], s[2]))
            if s[0] is 'C':
                s[6] = s[6].replace('\n', '')
                rep.courses.insert(Course(s[1], s[2], s[3], s[4], s[5], s[6]))
        rep._conn.commit()
        rep.print_tables()
