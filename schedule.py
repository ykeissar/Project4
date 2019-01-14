import sqlite3


class _Repository:
    def __init__(self):
        self._conn = sqlite3.connect('schedule.db')
        self.courses = _Courses(self._conn)
        self.students = _Students(self._conn)
        self.classrooms = _Classrooms(self._conn)

    def assign_course(self, classroom_id, course_id):
        # decreasing students from student
        course = self.courses.find(course_id)
        st = self.students.find(course.student)
        c = self._conn.cursor()
        c.execute("""
                       UPDATE students SET count=(?) WHERE grade=(?)
                   """, [st.count - course.number_of_students, course.student])
        # inserting course_id and course length to classroom
        c.execute("""
                    UPDATE 
                    classrooms SET current_course_id=(?), current_course_time_left=(?) WHERE id=(?)
                  """, [course_id, course.course_length + 1, classroom_id])

    def get_waiting_course(self, classroom_id):
        c = self._conn.cursor()
        c.execute("""
                SELECT id FROM courses WHERE class_id=(?)
                """, [classroom_id])
        return c.fetchone()

    def finish_course(self, course_id):
        c = self._conn.cursor()
        c.execute("""
                    UPDATE classrooms SET current_course_id=(?) WHERE id=(?)
                          """, [0, self.courses.find(course_id).class_id])
        c.execute("""
                    DELETE FROM courses WHERE id=(?)
                                        """, [course_id])

    def print_tables(self):
        print("courses")
        self.courses.print_table()
        print("classrooms")
        self.classrooms.print_table()
        print("students")
        self.students.print_table()

    def occupied_classes(self):
        c = self._conn.cursor()
        c.execute("""
                       SELECT id FROM classrooms WHERE current_course_id > (?)
                       """, [0])
        return c.fetchall()


class _Courses:
    def __init__(self, conn):
        self._conn = conn

    def find(self, course_id):
        c = self._conn.cursor()
        c.execute("""
            SELECT * FROM courses WHERE id = (?)
            """, [course_id])
        # if c.fetchall() is not None:
        return Course(*c.fetchone())
        # else:
        #     return None

    def is_empty(self):
        c = self._conn.cursor()
        c.execute("""
                    SELECT count(*) FROM courses 
                    """, )
        self._conn.commit()
        return c.fetchone()[0] == 0

    def get_table(self):
        c = self._conn.cursor()
        c.execute("""
            SELECT * FROM courses
            """)
        return c.fetchall()

    def print_table(self):
        for item in self.get_table():
            print(item)


class _Students:
    def __init__(self, conn):
        self._conn = conn

    def find(self, grade):
        c = self._conn.cursor()
        c.execute("""
            SELECT * FROM students WHERE grade = ?
            """, [grade])

        # if c.fetchall() is not None:
        return Student(*c.fetchone())
        # else:
        #     return None

    def get_table(self):
        c = self._conn.cursor()
        c.execute("""
               SELECT * FROM students
           """)
        return c.fetchall()

    def print_table(self):
        for item in self.get_table():
            print(item)


class _Classrooms:
    def __init__(self, conn):
        self._conn = conn

    def find(self, classroom_id):
        c = self._conn.cursor()
        c.execute("""
            SELECT * FROM classrooms WHERE id = (?)
            """, [classroom_id])

        # if c.fetchall() is not None:
        return Classroom(*c.fetchone())
        # else:
        #     return None

    def empty_classes(self):
        c = self._conn.cursor()
        c.execute("""
                    SELECT id FROM classrooms WHERE current_course_time_left = (?)
                    """, [0])
        return c.fetchall()

    def decrease_time_left(self, classroom_id):
        cl = self.find(classroom_id)
        c = self._conn.cursor()
        c.execute("""
                      UPDATE classrooms SET current_course_time_left=(?) WHERE id=(?)
                  """, [cl.current_course_time_left - 1, classroom_id])

    def get_table(self):
        c = self._conn.cursor()
        table = c.execute("""
            SELECT * FROM classrooms
        """).fetchall()
        return table

    def print_table(self):
        for item in self.get_table():
            print(item)


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
    def __init__(self, id, location, current_course_id, current_course_time_left):
        self.current_course_time_left = current_course_time_left
        self.current_course_id = current_course_id
        self.location = location
        self.id = id


if __name__ == "__main__":
    rep = _Repository()
    iter_num = 0
    while True:
        #       if there is no more courses - break
        if rep.courses.is_empty():
            break
        #       check if classes are empty and assign them
        for class_id in rep.classrooms.empty_classes():  # get empty class id
            c = rep.get_waiting_course(class_id[0])
            if c is not None:
                rep.assign_course(class_id[0], c[0])
                print("(" + str(iter_num) + ") " + rep.classrooms.find(class_id[0]).location + ": " + rep.courses.find(
                    c[0]).course_name + " is schedule to start")
        for class_id in rep.occupied_classes():
            rep.classrooms.decrease_time_left(class_id[0])
            cl = rep.classrooms.find(class_id[0])
            if rep.courses.find(cl.current_course_id).course_length is not cl.current_course_time_left and \
                    cl.current_course_time_left is not 0:
                print("(" + str(iter_num) + ") " + cl.location + ": occupied by " + rep.courses.find(
                    cl.current_course_id).course_name)
        for class_id in rep.classrooms.empty_classes():
            cl = rep.classrooms.find(class_id[0])
            if cl.current_course_id is not 0:
                cr = rep.courses.find(cl.current_course_id)
                rep.finish_course(cl.current_course_id)
                print("(" + str(iter_num) + ") " + rep.classrooms.find(
                    class_id[0]).location + ": " + cr.course_name + " is done")
                c = rep.get_waiting_course(class_id[0])
                if c is not None:
                    rep.assign_course(class_id[0], c[0])
                    print("(" + str(iter_num) + ") " + rep.classrooms.find(
                        class_id[0]).location + ": " + rep.courses.find(
                        c[0]).course_name + " is schedule to start")
                    rep.classrooms.decrease_time_left(class_id[0])
        rep.print_tables()
        iter_num += 1
