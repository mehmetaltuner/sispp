import os
import sys
import copy

import psycopg2 as dbapi2

from models.room import Room
from models.classroom import Classroom
from models.instructor import Instructor
from models.student import Student
from models.people import People

class Database:

    def __init__(self):
        self.rooms = {}
        self.classrooms = {}
        self.instructors = {}
        self.students = {}
        self.people = {}
        
        self._last_room_key = 0
        self._last_classroom_key = 0
        self._last_inst_key = 0
        self._last_stu_key = 0
        self._last_people_key = 0

        self.url = os.getenv("DATABASE_URL")

    ############# ROOMS ###############

    def add_room(self, room):
        self._last_room_key += 1
        self.rooms[self._last_room_key] = room
        return self._last_room_key

    def delete_room(self, room_key):
        if room_key in self.rooms:
            del self.rooms[room_key]

    def get_room(self, room_key):
        room = self.rooms.get(room_key)
        if room is None:
            return None
        room_ = Room(room.building, room.name, room.cap, room.classroom, room.room, room.lab)
        return room_
        
    def get_rooms(self):
        rooms = []
        for room_key, room in self.rooms.items():
            room_ = Room(room.building, room.name, room.cap, room.classroom, room.room, room.lab)
            rooms.append((room_key, room_))
        return rooms

   ############# CLASSROOMS ###############

    def add_classroom(self, classroom):
        self._last_classroom_key += 1
        self.classrooms[self._last_classroom_key] = classroom
        return self._last_classroom_key

    def delete_classroom(self, classroom_key):
        if classroom_key in self.classrooms:
            del self.classrooms[classroom_key]

    def get_classroom(self, classroom_key):
        classroom = self.classrooms.get(classroom_key)
        if classroom is None:
            return None
        classroom_ = Classroom(classroom.id, classroom.building, classroom.type, classroom.restoration_date, classroom.availability, classroom.conditioner, classroom.board_type)
        return classroom_
        
    def get_classrooms(self):
        classrooms = []
        for classroom_key, classroom in self.classrooms.items():
            classroom_ = Classroom(classroom.id, classroom.building, classroom.type, classroom.restoration_date, classroom.availability, classroom.conditioner, classroom.board_type)
            classrooms.append((classroom_key, classroom_))
        return classrooms

    ############# INSTRUCTORS ###############

    def add_instructor(self, instructor):
        self._last_inst_key += 1
        self.instructors[self._last_inst_key] = instructor
        return self._last_inst_key

    def delete_instructor(self, instructor_key):
        if instructor_key in self.instructors:
            del self.instructors[instructor_key]

    def get_instructor(self, instructor_key):
        instructor = self.instructors.get(instructor_key)
        if instructor is None:
            return None
        instructor_ = Instructor(instructor.name, instructor.department, instructor.lecture_id, instructor.room, instructor.lab)
        return instructor_
        
    def get_instructors(self):
        instructors = []
        for instructor_key, instructor in self.instructors.items():
            instructor_ = Instructor(instructor.name, instructor.department, instructor.lecture_id, instructor.room, instructor.lab)
            instructors.append((instructor_key, instructor_))
        return instructors


    ############# PEOPLE   ###############

    def add_person(self, person):
        try:
            with dbapi2.connect(self.url) as connection:
                cursor = connection.cursor()
                statement = "INSERT INTO PEOPLE VALUES (%s, %s, %s)"
                data = [person.name, person.mail, person.photo]
                cursor.execute(statement, data)
                statement = "SELECT P_ID FROM PEOPLE WHERE NAME = '%s'"
                data = [person.name]
                cursor.execute(statement, data)
                value = cursor.fetchall()
                person.id = value["P_ID"]
                cursor.close()
        except Exception as err:
            print("Error: ", err)

        self._last_people_key += 1
        self.people[self._last_people_key] = person

        return self._last_people_key

    def get_person(self, person_key):
        person = self.people.get(person_key)
        if not person:
            return None
        return person

    def get_people(self):
        if not len(self.people):
            try:
                with dbapi2.connect(self.url) as connection:
                    cursor = connection.cursor()
                    statement = "SELECT * FROM PEOPLE"
                    cursor.execute(statement)
                    datas = cursor.fetchall()
                    for data in datas:
                        person = People(data[0], data[1], data[2], data[3])
                        self._last_people_key += 1
                        self.people[_last_people_key] = person
                    cursor.close()
            except Exception as err:
                print("Error: ", err)

        return self.people.copy()


    ############# STUDENTS ###############

    def add_student(self, student):
        self._last_stu_key += 1
        self.students[self._last_stu_key] = student
        person_obj = People(student.name)
        person = get_person(add_person(person_obj))

        try:
            with dbapi2.connect(self.url) as connection:
                cursor = connection.cursor()

                statement = "INSERT INTO STUDENTS VALUES (%s, %s, %s, %s, %s, %s, %s)"
                data = [person.id, student.number, student.cred, student.depart, student.facu, student.club, student.lab]
                cursor.execute(statement, data)
                cursor.close()
        except Exception as err:
            print("Error: ", err)

        return self._last_stu_key

    def get_student(self, student_key):
        student = self.students.get(student_key)
        if not student:
            return None
        return copy.copy(student)

    def get_students(self):
        if not len(self.students):
            try:
                with dbapi2.connect(self.url) as connection:
                    cursor = connection.cursor()
                    statement = "SELECT * FROM STUDENTS"
                    cursor.execute(statement)
                    datas = cursor.fetchall()
                    for data in datas:
                        student = Student(data[0], data[1], data[2], data[3], data[4], data[5], data[6])
                        self._last_stu_key += 1
                        self.students[_last_stu_key] = student
                    cursor.close()
            except Exception as err:
                print("DB Error: ", err)

        return copy.copy(self.students)

    def delete_student(self, student_key):
        student = self.students.get(student_key)
        if student:
            try:
                with dbapi2.connect(self.url) as connection:
                    cursor = connection.cursor()
                    statement = "DELETE FROM STUDENTS WHERE number = %s"
                    values = [student.number]
                    cursor.execute(statement, values)
                    cursor.close()
                    del self.students[student_key]
            except Exception as err:
                print("Error: ", err)

    def update_student(self, student_key, attrs, values):
        student = self.students.get(student_key)
        attrs_lookup_table = {
            "id": "STU_ID",
            "number": "NUMBER",
            "cred": "EARNED_CREDITS",
            "depart": "DEPARTMANT",
            "facu": "FACULTY",
            "club": "CLUB",
            "lab": "LAB"
        }
        if student:
            try:
                with dbapi2.connect(self.url) as connection:
                    cursor = connection.cursor()
                    statement = "UPDATE STUDENTS SET "
                    for attr in attrs:
                        statement += attrs_lookup_table[attr] + " = %s "
                    statement += " WHERE number = %s"
                    values.append(student.number)
                    cursor.execute(statement, values)
                    cursor.close()
                    del self.students[student_key]
            except Exception as err:
                print("Error: ", err)