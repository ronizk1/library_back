
from collections import UserDict
from datetime import datetime, timedelta  # Add this line
from datetime import timedelta

import json, time, os
from functools import wraps
from flask import Flask, Request, jsonify, request, send_from_directory, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS, cross_origin
import jwt
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, get_jwt_identity, jwt_required
from flask_jwt_extended import jwt_required, get_jwt_identity
import requests
from datetime import datetime, timedelta
from icecream import ic
from functools import wraps

# import traceback




app = Flask(__name__)
CORS(app)


# SQLite database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key_here'  # Keep this as is
app.config['JWT_SECRET_KEY'] = 'secret_secret_key'  # Keep this as is
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

# Define Customer class (serving as both user and customer)
class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    city = db.Column(db.String(255), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='user')  # Default role is 'user'
    loans = db.relationship('Loan', backref='customer', lazy=True)

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    author = db.Column(db.String(255), nullable=False)
    year_published = db.Column(db.Integer, nullable=False)
    book_type = db.Column(db.Integer, nullable=False)
    loans = db.relationship('Loan', backref='book', lazy=True)

class Loan(db.Model):
    cust_id = db.Column(db.Integer, db.ForeignKey('customer.id'), primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), primary_key=True)
    loan_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    return_date = db.Column(db.DateTime)

# Create tables in the database
with app.app_context():
    db.create_all()

# Routes for the RESTful API

def get_jerusalem_time():
    # Set the base time in UTC
    utc_time = datetime.utcnow()

    # Check if daylight saving time is in effect (Jerusalem's daylight saving time is typically from the last Sunday in March to the last Sunday in October)
    dst_start = datetime(utc_time.year, 3, 25)
    dst_end = datetime(utc_time.year, 10, 25)

    is_dst = dst_start <= utc_time <= dst_end

    # Define the time difference for Jerusalem (UTC+2 during standard time, UTC+3 during daylight saving time)
    jerusalem_offset = 3 if is_dst else 2

    # Calculate Jerusalem time
    jerusalem_time = utc_time + timedelta(hours=jerusalem_offset)

    return jerusalem_time

def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        current_user_id = get_jwt_identity()
        current_user = Customer.query.get(current_user_id)
        
        if current_user.role == 'admin':
            return fn(*args, **kwargs)
        else:
            return jsonify({'error': 'Permission denied'}), 403

    return wrapper

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    username = data.get('username')
    password = data.get('password')
    name = data.get('name')
    city = data.get('city')
    age = data.get('age')
    role = data.get('role', 'user')  # Default role is 'user' if not provided

    # Check if the username is already taken
    existing_user = Customer.query.filter_by(username=username).first()
    if existing_user:
        return jsonify({'error': 'Username is already taken'}), 400

    # Hash and salt the password using Bcrypt
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

    # Create a new customer and add to the database
    new_customer = Customer(username=username, password=hashed_password, name=name, city=city, age=age, role=role)
    db.session.add(new_customer)
    db.session.commit()

    return jsonify({'message': 'Customer registered successfully'}), 201



@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    username = data.get('username')
    password = data.get('password')

    # Check if the user exists
    user = Customer.query.filter_by(username=username).first()
    user_name = user.username
    # customer = Customer.query.filter(Customer.username == username)
    
    if user and bcrypt.check_password_hash(user.password, password):
        # Generate an access token with an expiration time
        expires = timedelta(hours=1)
        access_token = create_access_token(identity=user.id, expires_delta=expires)

        # Use ic from icecream for logging with star emojis
        ic('✨✨✨✨', access_token)

        return jsonify({
            'message': 'Login successful',
            'user_id': user.id,
            'username': user.username,
            'customer_name': user.name,  # Include the user's name in the response
            'access_token': access_token
        }), 200
    else:
        return jsonify({'message': 'Invalid username or password'}), 401






@app.route('/add_book', methods=['POST'])
@jwt_required()
@admin_required
def add_book():
    current_user_id = get_jwt_identity()
    
    # Access the current user's information if needed
    current_user = Customer.query.get(current_user_id)
    print(f"User {current_user.username} is adding a book.")

    try:
        data = request.get_json()

        name = data.get('name')
        author = data.get('author')
        year_published = data.get('year_published')
        book_type = data.get('book_type')

        new_book = Book(name=name, author=author, year_published=year_published, book_type=book_type)
        db.session.add(new_book)
        db.session.commit()

        return jsonify({'message': 'Book added successfully'})
    except Exception as e:
        
        print(f"Error adding book: {e}")
        return jsonify({'error': 'Failed to add book'}), 500






@app.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    current_user_id = get_jwt_identity()
    current_user = db.session.query(Customer).get(current_user_id)

    # Check if the current_user is not None to avoid potential errors
    if current_user:
        # Convert set to list (or any other serializable format)
        current_user_serializable = {
            'username': current_user.username,
            'role': current_user.role  # Add the role attribute
            # Add more attributes as needed
        }

        return jsonify({'current_user': current_user_serializable}), 200
    else:
        return jsonify({'message': 'User not found'}), 404



# Loan a book
@app.route('/loan_book', methods=['POST'])
@jwt_required()

def loan_book():
    current_user_id = get_jwt_identity()

    data = request.get_json()
    book_id = data.get('book_id')  # Send the book ID instead of the book name

    # Search for the book by ID in the database
    book = Book.query.get(book_id)

    if book:
        # Check if the book is already on loan
        existing_loan = Loan.query.filter_by(cust_id=current_user_id, book_id=book.id, return_date=None).first()
        if existing_loan:
            return jsonify({'error': 'This book is already on loan'})

        # Get Jerusalem time for loan_date
        jerusalem_time = get_jerusalem_time()

        # Perform necessary operations (e.g., update database)
        new_loan = Loan(cust_id=current_user_id, book_id=book.id, loan_date=jerusalem_time)
        db.session.add(new_loan)
        db.session.commit()

        return jsonify({'message': 'Book loaned successfully'})
    else:
        return jsonify({'error': 'Book not found'})


# Get all books
@app.route('/all_books', methods=['GET'])
@jwt_required()
def get_all_books():
    books = Book.query.all()
    book_list = [{'id': book.id, 'name': book.name} for book in books]
    return jsonify({'books': book_list})




@app.route('/loans', methods=['GET'])
@jwt_required()
@admin_required
def get_loans():
    
    
    loans = Loan.query.all()
    loan_list = [{'customer_name': Customer.query.get(loan.cust_id).name,
                  'book_name': Book.query.get(loan.book_id).name,
                  'loan_date': loan.loan_date.strftime('%Y-%m-%d %H:%M:%S'),
                  'return_date': loan.return_date.strftime('%Y-%m-%d %H:%M:%S') if loan.return_date else None}
                 for loan in loans]
    return jsonify({'loans': loan_list})





# Return a book
@app.route('/return_book', methods=['POST'])
@jwt_required()
def return_book():
    data = request.form  # Use request.form to access form data

    book_id_return = data.get('book_id_return')

    # Search for the book by ID in the database
    book_return = Book.query.get(book_id_return)

    if book_return:
        # Check if the book is currently on loan
        existing_loan = Loan.query.filter_by(book_id=book_return.id, return_date=None).first()

        if existing_loan:
            # Get Jerusalem time for return_date
            jerusalem_time = get_jerusalem_time()

            # Perform necessary operations (e.g., update database)
            existing_loan.return_date = jerusalem_time
            db.session.commit()

            return jsonify({'message': 'Book returned successfully'})
        else:
            return jsonify({'error': 'This book is not currently on loan'})
    else:
        return jsonify({'error': 'Book not found'})


    
    
# Late Loans Function
@app.route('/late_loans', methods=['GET'])
@jwt_required()
@admin_required
def get_late_loans():
    current_date = datetime.utcnow()

    # Get all loans where return_date is None (i.e., not returned yet)
    active_loans = Loan.query.filter_by(return_date=None).all()

    late_loans_list = []

    for loan in active_loans:
        book = Book.query.get(loan.book_id)
        loan_duration = get_loan_duration(book.book_type)

        if loan_duration is not None:
            due_date = loan.loan_date + timedelta(days=loan_duration)
            if current_date > due_date:
                late_loans_list.append({
                    'customer_name': Customer.query.get(loan.cust_id).name,
                    'book_name': book.name,
                    'loan_date': loan.loan_date.strftime('%Y-%m-%d %H:%M:%S'),
                    'due_date': due_date.strftime('%Y-%m-%d %H:%M:%S')
                })

    return jsonify({'late_loans': late_loans_list})

def get_loan_status(book_id):
    # Check if the book is currently on loan
    active_loan = Loan.query.filter_by(book_id=book_id, return_date=None).first()
    
    if active_loan:
        return 'On Loan'
    else:
        return 'Available'


def get_loan_duration(book_type):
    
    # Map book types to loan durations
    loan_durations = {1: 10, 2: 5, 3: 2}
    return loan_durations.get(book_type)

# Get all customers
@app.route('/customers', methods=['GET'])
@jwt_required()
@admin_required
def get_customers():
    customers = Customer.query.all()
    customer_list = [{'id': customer.id, 'name': customer.name, 'city': customer.city,
                      'age': customer.age} for customer in customers]
    return jsonify({'customers': customer_list})

# Get all books
@app.route('/books', methods=['GET'])
@jwt_required()
def get_books():
    books = Book.query.all()
    book_list = [{'id': book.id, 'name': book.name, 'author': book.author,
                  'year_published': book.year_published, 'book_type': book.book_type}
                 for book in books]
    return jsonify({'books': book_list})




# Find a book by name
@app.route('/find_book', methods=['POST'])
@jwt_required()
def find_book():
    data = request.get_json()

    book_name = data.get('book_name')

    # Search for the book by name in the database
    book = Book.query.filter_by(name=book_name).first()

    if book:
        # Check if the book is currently on loan
        loan_status = get_loan_status(book.id)
        return jsonify({'book_name': book.name, 'author': book.author, 'loan_status': loan_status})
    else:
        return jsonify({'error': 'Book not found'})



# Find a customer by name
@app.route('/find_customer', methods=['POST'])
@jwt_required()
@admin_required
def find_customer():
    data = request.get_json()

    customer_name = data.get('customer_name')

    # Search for the customer by name in the database
    customer = Customer.query.filter_by(name=customer_name).first()

    if customer:
        # Get all loans associated with the customer
        loans = Loan.query.filter_by(cust_id=customer.id).all()
        
        # Format loan information
        loan_info = []
        for loan in loans:
            book = Book.query.get(loan.book_id)
            loan_info.append({
                'book_name': book.name,
                'loan_date': loan.loan_date.strftime('%Y-%m-%d %H:%M:%S'),
                'return_date': loan.return_date.strftime('%Y-%m-%d %H:%M:%S') if loan.return_date else 'Not returned'
            })

        return jsonify({
            'customer_name': customer.name,
            'city': customer.city,
            'age': customer.age,
            'loan_info': loan_info
        })
    else:
        return jsonify({'error': 'Customer not found'})
    
    
    
# Get all loans for the current user
@app.route('/user_loans', methods=['GET'])
@jwt_required()
def get_user_loans():
    current_user_id = get_jwt_identity()

    # Get all loans for the current user
    user_loans = Loan.query.filter_by(cust_id=current_user_id).all()

    # Format loan information
    loan_info = []
    for loan in user_loans:
        book = Book.query.get(loan.book_id)
        loan_info.append({
            'book_name': book.name,
            'loan_date': loan.loan_date.strftime('%Y-%m-%d %H:%M:%S'),
            'return_date': loan.return_date.strftime('%Y-%m-%d %H:%M:%S') if loan.return_date else 'Not returned'
        })

    return jsonify({'user_loans': loan_info})



# Run the application
if __name__ == '__main__':
    app.run(debug=True)