from flask import session
from controller import constants
from controller.database import Database
from .user import User
from .blog import Blog


class Student(User):
    def __init__(self, email, password, sex, name, skills, school, _id=None):
        User.__init__(self, email, password, sex, name, _id)
        self.skills = skills
        self.school = school

    @classmethod
    def get_by_email(cls, email):
        user = Database.find_one(collection=constants.STUDENT_COLLECTION,
                                 query={"email": email})
        if user is not None:
            return cls(**user)
        return None

    @classmethod
    def get_by_id(cls, _id):
        user = Database.find_one(collection=constants.STUDENT_COLLECTION,
                                 query={"_id": _id})
        if user:
            return cls(**user)
        return None

    def add_skill(self, skill):
        self.skills.append(skill)
        return 1

    def delete_skill(self, skill):
        self.skills.remove(skill)
        return 1

    @classmethod
    def register(cls, email, password, sex, skill, name, school):
        if not len(email) or not len(password):
            return False
        user = cls.get_by_email(email)
        if not user:
            new_user = cls(email, password, sex, name, skill,  school)
            new_user.save_to_mongo()
            session.__setitem__('email', email)
            session.__setitem__('name', name)
            return True
        return False


    def json(self):
        return {
            'email': self.email,
            '_id': self._id,
            "password": self.password,
            'sex': self.sex,
            'skills': self.skills,
            'name': self.name,
            'school': self.school
        }

    def save_to_mongo(self):
        Database.insert(
            constants.STUDENT_COLLECTION,
            self.json()
        )

    def update_password(self, new_email, new_password=None):
        Database.update(
            constants.STUDENT_COLLECTION,
            {"email": self.email},
            {"$set":
                 {
                     "email": new_email if new_email else self.email,
                     "password": new_password if new_password else self.password
                 }}
        )

    def update_user(self,new_name ,new_email, new_password, new_sex, new_skills, new_school):
        Database.update(
            constants.STUDENT_COLLECTION,
            {"email": self.email},
            {"$set":
                 {
                     "name": new_name if new_name else self.name,
                     "email": new_email if new_email else self.email,
                     "password": new_password if new_password else self.password,
                     "sex": new_sex if new_sex else self.sex,
                     "skills": new_skills if new_skills else self.skills,
                     "school": new_school if new_school else self.school
                 }}
        )


