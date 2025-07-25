import datetime
import azure.functions as func
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
import json
import os
from datetime import date, timedelta
from models.models import User, Book, BookCopy, Borrow

engine = create_engine(os.environ["DB_URL"], echo=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

def checkout_endpoints(app: func.FunctionApp):

    @app.route(route="checkouts", methods=["GET"])
    def all_checkouts(req: func.HttpRequest) -> func.HttpResponse:
        try:
            with SessionLocal() as session:
                checkouts = session.query(Borrow).order_by(Borrow.return_date.asc()).all()

                if not checkouts:
                    return func.HttpResponse("No Active Checkouts", status_code=200)
                else:
                    borrows_list = [{
                        "iD": checkout.id,
                        "Book": f"{checkout.book.title} by {checkout.book.author}",
                        "Copy": checkout.book_copies_id,
                        "Checkout Date": checkout.borrow_date.isoformat(),
                        "Return Date": checkout.return_date.isoformat(),
                        "User Name": checkout.user.name
                    } for checkout in checkouts]
                    return func.HttpResponse(json.dumps(borrows_list), mimetype="application/json", status_code=200)

        except Exception as e:
            return func.HttpResponse(f"Internal server error: {str(e)}", status_code=500)

    @app.route(route="checkouts", methods=["POST"])
    def create_checkout(req: func.HttpRequest) -> func.HttpResponse:

        try:
            req_body = req.get_json()
            book_id = req_body.get('book_id')
            book_copies_id = req_body.get('book_copies_id')
            user_id = req_body.get('user_id')
            borrow_date = date.today()
            return_date = borrow_date + timedelta(days=30)
        except ValueError:
            return func.HttpResponse("Invalid JSON in request body", status_code=400)

        if not all([book_id, book_copies_id, user_id]):
            return func.HttpResponse("Book iD, Copy iD, User iD, and Borrow Date are required", status_code=400)

        with SessionLocal() as session:
            new_checkout = Borrow(book_id=book_id, book_copies_id=book_copies_id, user_id=user_id, borrow_date=borrow_date, return_date=return_date)
            session.add(new_checkout)
            book_copy = session.query(BookCopy).get(book_copies_id)

            if book_copy:
                book_copy.available = False

            session.commit()

        return func.HttpResponse(f"Created a checkout for, User:{user_id} borrowing Copy:{book_copies_id}. Book is due back: {return_date}.", status_code=200)