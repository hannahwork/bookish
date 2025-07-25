import azure.functions as func
import logging
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
import os
from datetime import date
from models.models import Base, User, Book, BookCopy
import json
from books_controller import book_endpoints
from users_controller import user_endpoints
from checkouts_controller import checkout_endpoints

app = func.FunctionApp()
book_endpoints(app)
user_endpoints(app)
checkout_endpoints(app)

engine = create_engine(os.environ["DB_URL"], echo=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)