from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
 
Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True,)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250))

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'name':     self.name,
            'email':    self.email,
            'picture':  self.picture,
            'id':       self.id,
        }


class Books(Base):
    __tablename__ = 'books'

    title = Column(String(80), nullable=False)
    id = Column(Integer, primary_key=True)
    author = Column(String(50), nullable=False)
    description = Column(String(500))

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
                'title':         self.title,
                'description':   self.description,
                'author':       self.author,
                'id':            self.id,
        }


class User_Books(Base):
    __tablename__ = 'user_books'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)
    book_id = Column(Integer, nullable=False)
    status = Column(String(20), nullable=False)
    notes = Column(String(200))

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'user_id':          self.user_id,
            'book_id':          self.book_id,
            'status':           self.status,
            'notes':            self.notes,
        }

# NYI
# class Genre(Base):
#     __tablename__ = 'genre'
#
#     id = Column(Integer, primary_key=True)
#     name = Column(String(250), nullable=False)
#
#     @property
#     def serialize(self):
#         """Return object data in easily serializeable format"""
#         return {
#             'name': self.name,
#             'id':   self.id,
#         }

# class Book_Genre(Base):
#     __tablename__ = 'book_genre'
#
#     book_id = Column(Integer, ForeignKey('books.id'), primary_key=True)
#     books = relationship(Books)
#     book_genre_id = Column(Integer, ForeignKey('genre.id'), nullable=False)
#     genre = relationship(Genre)
#
#     @property
#     def serialize(self):
#         """Return object data in easily serializeable format"""
#         return {
#             'book_id':          self.book_id,
#             'book_genre_id':    self.book_genre_id,
#         }

engine = create_engine('sqlite:///littleelibrary.db')
 

Base.metadata.create_all(engine)
