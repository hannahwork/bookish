import azure.functions as func
import logging
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
import os
from datetime import date
from models.models import Base, User, Book

app = func.FunctionApp()

engine = create_engine(os.environ["DB_URL"], echo=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

# Helper to calculate age from a date of birth
def _calculate_age(dob: date) -> int:
    today = date.today()
    return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

@app.route(route="httpget", methods=["GET"])
def http_get(req: func.HttpRequest) -> func.HttpResponse:
    name = req.params.get("name", "World")
    with SessionLocal() as session:
        selection = select(User).where(User.name == name).order_by(User.id.desc())
        user = session.execute(selection).scalar()
        if user and user.date_of_birth:
            age = _calculate_age(user.date_of_birth)
            return func.HttpResponse(f"Hello, {name}! You are {age} years old!")
        return func.HttpResponse(f"Hello, {name}! User record not found.")

@app.route(route="httppost", methods=["POST"])
def http_post(req: func.HttpRequest) -> func.HttpResponse:
    try:
        req_body = req.get_json()
        name = req_body.get('name')
        dob_str = req_body.get('dob')

        try:
            dob = date.fromisoformat(dob_str)
        except Exception:
            return func.HttpResponse("'dob' must be in YYYY-MM-DD format", status_code=400)

        with SessionLocal() as session:
            session.add(User(name=name, date_of_birth=dob))
            session.commit()

        logging.info(f"Processing POST request. Name: {name}")

        if name and isinstance(name, str):
            age = _calculate_age(dob)
            return func.HttpResponse(f"Hello, {name}! You are {age} years old!")
        return func.HttpResponse("Please provide both 'name' and 'dob' in the request body.", status_code=400)
    except ValueError:
        return func.HttpResponse(
            "Invalid JSON in request body",
            status_code=400
        )

@app.route(route="all-books", methods=["GET"])
def all_books(req: func.HttpRequest) -> func.HttpResponse:
    with SessionLocal() as session:
        view = select(Book).order_by(Book.title.asc())
        books = session.execute(view).scalars().all()

        books_list = [{"Title": book.title, "Author": book.author} for book in books]
        import json
    return func.HttpResponse(json.dumps(books_list), mimetype="application/json", status_code=200)

@app.route(route="all-books", methods=["POST"])
def create_book(req: func.HttpRequest) -> func.HttpResponse:
    try:
        req_body = req.get_json()
        title = req_body.get('title')
        author = req_body.get('author')
        copies = req_body.get('copies')
    except ValueError:
        return func.HttpResponse("Invalid JSON in request body", status_code=400)

    if not all([title, author]):
        return func.HttpResponse("Title and author are required", status_code=400)
    with SessionLocal() as session:
        book = Book(title=title, author=author, copies=copies)
        session.add(book)
        session.commit()

    logging.info(f"Processing POST request. Title: {title}")
    return func.HttpResponse(f"Added, {copies} copies of {title} by {author}.", status_code=200)