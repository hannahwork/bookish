import azure.functions as func
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
import os
from models.models import Book, BookCopy
import json

engine = create_engine(os.environ["DB_URL"], echo=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

def book_endpoints(app: func.FunctionApp):

    @app.route(route="books", methods=["GET"])
    def all_books(req: func.HttpRequest) -> func.HttpResponse:
        with SessionLocal() as session:
            view = select(Book).order_by(Book.title.asc())
            books = session.execute(view).scalars().all()

            books_list = [{"Title": book.title, "Author": book.author} for book in books]
        return func.HttpResponse(json.dumps(books_list), mimetype="application/json", status_code=200)


    @app.route(route="books", methods=["POST"])
    def create_book(req: func.HttpRequest) -> func.HttpResponse:
        try:
            req_body = req.get_json()
            title = req_body.get('title')
            author = req_body.get('author')
            copies = int(req_body.get('copies', 1))

        except ValueError:
            return func.HttpResponse("Invalid JSON in request body", status_code=400)

        if not all([title, author, copies]):
            return func.HttpResponse("Title, author and copies are required", status_code=400)

        with SessionLocal() as session:
            new_book = Book(title=title, author=author, copies=copies)
            session.add(new_book)
            session.flush()

            for i in range(copies):
                session.add(BookCopy(book_id=new_book.id, available=True))

            session.commit()


        return func.HttpResponse(f"Added, {copies} available copies of {title} by {author}.", status_code=200)

    @app.route(route="books/{book_id}", methods=["GET"])
    def get_books_by_id(req: func.HttpRequest) -> func.HttpResponse:
        book_id = req.route_params.get("book_id")
        try:
            book_id = int(book_id)
        except (ValueError, TypeError):
            return func.HttpResponse("Invalid Book ID", status_code=400)

        with SessionLocal() as session:
            book = session.get(Book, book_id)
            if not book:
                return func.HttpResponse("Book not found", status_code=404)

            copies = session.query(BookCopy).filter(BookCopy.book_id == book_id).all()
            available_copies =len( [copy for copy in copies if copy.available])

            result = {
                "id": book_id,
                "title": book.title,
                "author": book.author,
                "available": available_copies,
                "total_copies": len(copies)
            }
        return func.HttpResponse(json.dumps(result), mimetype="application/json", status_code=200)