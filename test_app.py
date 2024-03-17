# import token
# import unittest
# from app import app, db, Customer, Book, Loan
# from datetime import datetime, timedelta
# from icecream import ic

# class AppTestCase(unittest.TestCase):

#     def setUp(self):
#         app.config['TESTING'] = True
#         app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
#         self.app = app.test_client()

#         # Create the application context
#         with app.app_context():
#             db.create_all()


#     def tearDown(self):
#         with app.app_context():
#             db.session.remove()
#             db.drop_all()

#     def register_customer(self, username, password, name, city, age):
#         return self.app.post('/register', json={
#             'username': username,
#             'password': password,
#             'name': name,
#             'city': city,
#             'age': age
#         })

#     def login_customer(self, username, password):
#         return self.app.post('/login', json={
#             'username': username,
#             'password': password
#         })

#     def add_book(self, name, author, year_published, book_type, token):
#         return self.app.post('/add_book', json={
#             'name': name,
#             'author': author,
#             'year_published': year_published,
#             'book_type': book_type
#         }, headers={'Authorization': f'Bearer {token}'})
        
#     def get_books(self, token):
#         return self.app.get('/all_books', headers={'Authorization': f'Bearer {token}', 'Accept': 'application/json'})



#     def test_register_and_login(self):
#         # Test customer registration and login
#         response = self.register_customer('test_user', 'test_password', 'Test User', 'Test City', 25)
#         print(ic(response.get_json()))  # Add this line to print the response content
#         self.assertEqual(response.status_code, 201)

#         response = self.login_customer('test_user', 'test_password')
#         self.assertEqual(response.status_code, 200)
#         self.assertIn('access_token', response.json)

#     def test_add_book(self):
#         # Test adding a book
#         response = self.register_customer('test_user', 'test_password', 'Test User', 'Test City', 25)
#         self.assertEqual(response.status_code, 201)
#         token = self.login_customer('test_user', 'test_password').json['access_token']

#         response = self.add_book('Test Book', 'Test Author', 2022, 1, token)
#         print(ic(response.get_json()))  # Add this line to print the response content
#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(response.json['message'], 'Book added successfully')
        
#     def test_borrow_and_return_book(self):
#         # Test borrowing and returning a book
#         response_register = self.register_customer('test_user', 'test_password', 'Test User', 'Test City', 25)
#         self.assertEqual(response_register.status_code, 201)
#         token = self.login_customer('test_user', 'test_password').json['access_token']

#         response_add_book = self.add_book('Test Book', 'Test Author', 2022, 1, token)
#         ic(response_add_book.get_json())  # Add this line to print the response content

#         self.assertIsNotNone(response_add_book.json, "Response JSON is None")
        
#         book_id = response_add_book.json.get('id')


#         ic(book_id)

#         self.assertIsNotNone(book_id, "Book ID not found in the response")

#         response_borrow = self.borrow_book(book_id, token)
#         ic(response_borrow.get_json())  # Add this line to print the response content
#         self.assertEqual(response_borrow.status_code, 200)
#         self.assertEqual(response_borrow.json['message'], 'Book borrowed successfully')

#         # Assume some time has passed (e.g., a day)
#         response_return = self.return_book(response_borrow.json['loan']['id'], token)
#         ic(response_return.get_json())  # Add this line to print the response content
#         self.assertEqual(response_return.status_code, 200)
#         self.assertEqual(response_return.json['message'], 'Book returned successfully')


#     def test_get_books(self):
#         response_get_books = self.get_books(token)


#         # Print the raw response content
#         print(response_get_books.data.decode('utf-8'))

#         # Check if the response has valid JSON content
#         self.assertTrue(response_get_books.is_json)

#         # Check for a 200 status code (assuming a successful response)
#         self.assertEqual(response_get_books.status_code, 200)

#         # Now you can perform assertions based on the expected structure of the response
#         # For example, if your response has a 'books' key, you can do:
#         self.assertIn('books', response_get_books.json)

#         # Add more specific assertions based on the structure of your expected response
#         # For example, if you expect a list of books, you can check the length:
#         self.assertGreater(len(response_get_books.json['books']), 0)



#         # Add assertions based on the expected structure of the response

#     # Add more tests for other functions...

# if __name__ == '__main__':
#     unittest.main()

from msilib.schema import SelfReg
import token
from typing import Self
import unittest
from app import app, db, Customer, Book, Loan
from datetime import datetime, timedelta
from icecream import ic
from app import app, db, Customer, Book, Loan
import token  # Import the token module if it's required


class AppTestCase(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app = app.test_client()

        # Create the application context
        with app.app_context():
            db.create_all()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def register_customer(self, username, password, name, city, age):
        return self.app.post('/register', json={
            'username': username,
            'password': password,
            'name': name,
            'city': city,
            'age': age
        })

    def login_customer(self, username, password):
        return self.app.post('/login', json={
            'username': username,
            'password': password
        })
        
    def borrow_book(self, book_id, token):
        # Implement the logic to borrow a book
        # Example: return self.app.post('/borrow_book', json={'book_id': book_id}, headers={'Authorization': f'Bearer {token}'})
        return self.app.post('/borrow_book', json={'book_id': book_id}, headers={'Authorization': f'Bearer {token}'})

    def return_book(self, loan_id, token):
        # Implement the logic to return a book
        # Example: return self.app.post('/return_book', json={'loan_id': loan_id}, headers={'Authorization': f'Bearer {token}'})
        return self.app.post('/return_book', json={'loan_id': loan_id}, headers={'Authorization': f'Bearer {token}'})




    def add_book(self, name, author, year_published, book_type, token):
        return self.app.post('/add_book', json={
            'name': name,
            'author': author,
            'year_published': year_published,
            'book_type': book_type
        }, headers={'Authorization': f'Bearer {token}'})

    def get_books(self, token):
        return self.app.get('/all_books', headers={'Authorization': f'Bearer {token}', 'Accept': 'application/json'})

    def test_register_and_login(self):
        response = self.register_customer('test_user', 'test_password', 'Test User', 'Test City', 25)
        self.assertEqual(response.status_code, 201)

        response = self.login_customer('test_user', 'test_password')
        self.assertEqual(response.status_code, 200)
        self.assertIn('access_token', response.json)

    def test_add_book(self):
        response = self.register_customer('test_user', 'test_password', 'Test User', 'Test City', 25)
        self.assertEqual(response.status_code, 201)
        token = self.login_customer('test_user', 'test_password').json['access_token']

        response = self.add_book('Test Book', 'Test Author', 2022, 1, token)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['message'], 'Book added successfully')

    def test_borrow_and_return_book(self):
        response_register = self.register_customer('test_user', 'test_password', 'Test User', 'Test City', 25)
        self.assertEqual(response_register.status_code, 201)
        token = self.login_customer('test_user', 'test_password').json['access_token']

        response_add_book = self.add_book('Test Book', 'Test Author', 2022, 1, token)
        self.assertEqual(response_add_book.status_code, 200)
        book_id = response_add_book.json.get('id')
        self.assertIsNotNone(book_id, "Book ID not found in the response")

        response_borrow = self.borrow_book(book_id, token)
        self.assertEqual(response_borrow.status_code, 200)
        self.assertEqual(response_borrow.json['message'], 'Book borrowed successfully')

        # Assume some time has passed (e.g., a day)
        response_return = self.return_book(response_add_book.json['loan']['id'], token)
        self.assertEqual(response_return.status_code, 200)
        self.assertEqual(response_return.json['message'], 'Book returned successfully')



    def test_get_books(self):
        response_get_books = self.get_books(token)
        self.assertTrue(response_get_books.is_json)
        self.assertEqual(response_get_books.status_code, 200)
        self.assertIn('books', response_get_books.json)
        self.assertGreater(len(response_get_books.json['books']), 0)


    # Add more tests for other functions...

if __name__ == '__main__':
    unittest.main()
