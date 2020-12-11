from flask import session
from controller import constants
from controller.database import Database
from .user import User
from .blog import Blog

class Commuter(User):
    def __init__(self, email, password, sex, name, company, _id=None):
        User.__init__(self, email, password, sex, name, _id=None)
        self.company = company

    @classmethod
    def get_by_email(cls, email):
        user = Database.find_one(collection=constants.COMMUTER_COLLECTION,
                                 query={"email": email})
        if user:
            return cls(**user)
        return None

    @classmethod
    def get_by_id(cls, _id):
        user = Database.find_one(collection=constants.COMMUTER_COLLECTION,
                                 query={"_id": _id})
        if user:
            return cls(**user)
        return None

    @classmethod
    def register(cls, email, password, sex, name, company):
        if not len(email) or not len(password):
            return False
        user = cls.get_by_email(email)
        if not user:
            new_user = cls(email, password, sex, name, company)
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
            'name': self.name,
            'company': self.company
        }

    def save_to_mongo(self):
        Database.insert(
            constants.COMMUTER_COLLECTION,
            self.json()
        )

    def update_password(self, new_email, new_password=None):
        Database.update(
            constants.COMMUTER_COLLECTION,
            {"email": self.email},
            {"$set":
                 {
                     "email": new_email if new_email else self.email,
                     "password": new_password if new_password else self.password
                 }}
        )

    def update_user(self, new_name, new_email, new_password, new_sex, new_company):
        Database.update(
            constants.COMMUTER_COLLECTION,
            {"email": self.email},
            {"$set":
                 {
                     "name": new_name if new_name else self.name,
                     "email": new_email if new_email else self.email,
                     "password": new_password if new_password else self.password,
                     "sex": new_sex if new_sex else self.sex,
                     "company": new_company if new_company else self.company
                 }}
        )



