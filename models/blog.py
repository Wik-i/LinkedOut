import uuid
from datetime import datetime
from controller import constants
from controller.database import Database
from models.comment import Comment



class Blog(object):
    def __init__(self, author_id, author, title, description,  _id=None):
        self._id = uuid.uuid4().hex if _id is None else _id
        self.author = author
        self.author_id = author_id
        self.title = title
        self.description = description
        self.likes = 0
        self.dislikes = 0
        self.comment = None

    def new_comment(self, title, content, author, date=datetime.utcnow()):
        self.comment = Comment(
            blog_id=self._id,
            title=title,
            content=content,
            created_at=date,
            author=author
        )
        self.comment.save_to_mongo()
        return self.comment.json()

    def save_to_mongo(self):
        Database.insert(collection=constants.BLOG_COLLECTION,
                        data=self.json())

    def json(self):
        return {
            '_id': self._id,
            'author_id': self.author_id,
            'author': self.author,
            'title': self.title,
            'description': self.description
        }

    @classmethod
    def from_mongo(cls, __i):
        blog = Database.find_one(
            collection=constants.BLOG_COLLECTION,
            query={"_id": __i}
        )
        return cls(**blog)

    def get_comments(self):
        return Comment.from_blog(self._id)

    @classmethod
    def delete_from_mongo_viaId(cls, _id):
        Database.delete(collection=constants.BLOG_COLLECTION,
                        query={'_id': _id})
    @classmethod
    def delete_all_from_mongo_viaQuery(cls, query):
        Database.deletemany(collection=constants.BLOG_COLLECTION,
                        query=query)

    @classmethod
    def find_by_author_id(cls, author_id):
        all_blog = Database.find(
            constants.BLOG_COLLECTION,
            {"author_id": author_id}
        )
        return [cls(**blog) for blog in all_blog]

    @classmethod
    def get_by_id(cls, blog_id):
        blog = Database.find_one(collection=constants.BLOG_COLLECTION,
                                 query={"_id": blog_id})
        if blog:
            return cls(**blog)
        return None


    @classmethod
    def get_by_title(cls, blog_id):
        blog = Database.find_one(collection=constants.BLOG_COLLECTION,
                                 query={"title": blog_id})
        if blog:
            return cls(**blog)
        return None

    @classmethod
    def get_by_title_re(cls, blog_id):
        blog = Database.find(collection=constants.BLOG_COLLECTION,
                                 query={"title": {'$regex': blog_id}})
        if blog:
            #print(blog)
            return blog
        return None

    @classmethod
    def get_all_blogs(cls):
        blogs = Database.find(
            constants.BLOG_COLLECTION,
            {}
        )
        return blogs

    def like(self):
        self.likes = self.likes + 1

    def cancel_like(self):
        if self.likes == 0:
            return

        self.likes = self.likes - 1

    def dislike(self):
        self.dislikes = self.dislikes + 1

    def cancel_dislikes(self):
        if self.dislikes == 0:
            return

        self.dislikes = self.dislikes - 1






