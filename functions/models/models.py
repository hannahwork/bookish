from datetime import date

from sqlalchemy import Column, Integer, String, Date, ForeignKey, Boolean
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    date_of_birth = Column(Date)

    borrows = relationship("Borrow", back_populates="user")

class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, nullable=False)
    author = Column(String, nullable=False)
    copies = Column(Integer, nullable=False)

    book_copies = relationship("BookCopy", back_populates="book")

class BookCopy(Base):

    __tablename__ = "book_copies"
    id = Column(Integer, primary_key=True, autoincrement=True)
    book_id = Column(Integer, ForeignKey("books.id"))
    available = Column(Boolean, nullable=False)

    book = relationship("Book", back_populates="book_copies")
    borrow = relationship("Borrow", back_populates="copy")

class Borrow(Base):
    __tablename__ = "borrows"
    id = Column(Integer, primary_key=True, autoincrement=True)
    book_id = Column(Integer, ForeignKey("books.id"))
    book_copies_id = Column(Integer, ForeignKey("book_copies.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    borrow_date = Column(Date)
    return_date = Column(Date)

    user = relationship("User", back_populates="borrows")
    copy = relationship("BookCopy", back_populates="borrow")

