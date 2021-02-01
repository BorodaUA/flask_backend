# import os
# import sys
# import pytest
# import json
# import logging
# from sqlalchemy import create_engine
# from sqlalchemy.orm import scoped_session, sessionmaker
# from sqlalchemy.exc import ProgrammingError, OperationalError
# sys.path.append(os.getcwd())
# from flask_backend import create_app, db # noqa
# from api.models import user # noqa

# # pytest -s -o log_cli=true -o log_level=DEBUG


# @pytest.fixture(scope='function')
# def client(request):
#     app = create_app("testing")
#     db.init_app(app)
#     with app.test_client() as client:
#         with app.app_context():
#             logging.debug('Starting the test.')
#             db_name = db.get_engine(bind="flask_backend").url.database
#             create_db(test_db_name=db_name)
#             test_db_engine = db.get_engine(bind="flask_backend")
#             user.Base.session = scoped_session(
#                 sessionmaker(
#                     autocommit=False,
#                     autoflush=False,
#                     bind=test_db_engine,
#                 )
#             )
#             user.Base.query = user.Base.session.query_property()
#             user.Base.metadata.create_all(test_db_engine)

#         yield client

#         @app.teardown_appcontext
#         def shutdown_session_and_delete_db(exception=None):
#             logging.debug('Shutting down the test.')
#             user.Base.session.close()
#             test_db_engine.dispose()
#             delete_db(test_db_name=db_name)


# def create_db(test_db_name):
#     default_postgres_db_url = os.environ.get("POSTGRES_DATABASE_URI")
#     default_engine = create_engine(default_postgres_db_url)
#     default_engine = default_engine.execution_options(
#         isolation_level="AUTOCOMMIT"
#     )
#     conn = default_engine.connect()
#     # Try to delete Database
#     try:
#         conn.execute(
#             f"DROP DATABASE "
#             f"{test_db_name};"
#         )
#     except ProgrammingError as err:
#         logging.debug(err)
#         conn.execute("ROLLBACK")
#     except OperationalError as err:
#         logging.debug(err)
#         conn.execute("ROLLBACK")
#     # Try to create Database
#     try:
#         conn.execute(
#             f"CREATE DATABASE "
#             f"{test_db_name} "
#             f"ENCODING 'utf8' TEMPLATE template1"
#         )
#     except ProgrammingError as err:
#         logging.debug(err)
#         conn.execute("ROLLBACK")
#     except OperationalError as err:
#         logging.debug(err)
#         conn.execute("ROLLBACK")
#     conn.close()
#     default_engine.dispose()
#     return


# def delete_db(test_db_name):
#     default_postgres_db_url = os.environ.get("POSTGRES_DATABASE_URI")
#     default_engine = create_engine(default_postgres_db_url)
#     default_engine = default_engine.execution_options(
#         isolation_level="AUTOCOMMIT"
#     )
#     conn = default_engine.connect()
#     try:
#         conn.execute(
#             f"DROP DATABASE "
#             f"{test_db_name};"
#         )
#     except ProgrammingError as err:
#         logging.debug(err)
#         conn.execute("ROLLBACK")
#     except OperationalError as err:
#         logging.debug(err)
#         conn.execute("ROLLBACK")
#     conn.close()
#     default_engine.dispose()
#     return

# # # pytest -s -o log_cli=true -o log_level=INFO


# def test_signin_user_no_fields(client):
#     """
#     Test /api/users/signin endpoint with no required fields
#     """
#     request = client.post(
#         "/api/users/signin",
#         data=json.dumps({}),
#         content_type="application/json",
#     )
#     response = json.loads(request.data)
#     assert {
#         "username": ["Missing data for required field."],
#         "email_address": ["Missing data for required field."],
#         "password": ["Missing data for required field."],
#     } == response


# def test_signin_user_only_username_field(client):
#     """
#     Test /api/users/signin endpoint with only username field present
#     """
#     request = client.post(
#         "/api/users/signin",
#         data=json.dumps({"username": "bob_2"}),
#         content_type="application/json",
#     )
#     response = json.loads(request.data)
#     assert {
#         "password": ["Missing data for required field."],
#         "email_address": ["Missing data for required field."],
#     } == response


# def test_signin_user_username_and_password_fields(client):
#     """
#     Test /api/users/signin endpoint with username
#     and password fields present
#     """
#     request = client.post(
#         "/api/users/signin",
#         data=json.dumps(
#             {
#                 "username": "bob_2",
#                 "password": "123456"
#             }
#         ),
#         content_type="application/json",
#     )
#     response = json.loads(request.data)
#     assert {
#         "email_address": ["Missing data for required field."]
#     } == response


# def test_signin_all_fields_empty(client):
#     """
#     Test /api/users/signin endpoint with all fields present
#     but all of them empty
#     """
#     request = client.post(
#         "/api/users/signin",
#         data=json.dumps(
#             {
#                 "username": "",
#                 "password": "",
#                 "email_address": ""
#             }
#         ),
#         content_type="application/json",
#     )
#     response = json.loads(request.data)
#     assert (
#         {
#             "username": [
#                 "Length must be between 3 and 256.",
#             ],
#             "password": [
#                 "Length must be between 6 and 32.",
#                 "String does not match expected pattern."
#             ],
#             "email_address": [
#                 "Length must be between 3 and 256."
#             ],
#         }
#     ) == response


# def test_signin_user_username_valid_other_fields_empty(client):
#     """
#     Test /api/users/signin endpoint with valid username field
#     other fields empty
#     """
#     request = client.post(
#         "/api/users/signin",
#         data=json.dumps(
#             {
#                 "username": "bob_2",
#                 "password": "",
#                 "email_address": ""
#             }
#         ),
#         content_type="application/json",
#     )
#     response = json.loads(request.data)
#     assert (
#         {
#             "password": [
#                 "Length must be between 6 and 32.",
#                 "String does not match expected pattern."
#             ],
#             "email_address": [
#                 "Length must be between 3 and 256."
#             ],
#         }
#     ) == response


# def test_signin_valid_username_valid_email_other_fields_empty(client):
#     """
#     Test /api/users/signin endpoint with valid username,
#     email_address fields, password field are empty.
#     """
#     request = client.post(
#         "/api/users/signin",
#         data=json.dumps(
#             {
#                 "username": "bob_2",
#                 "email_address": "bob_2@gmail.com",
#                 "password": "",
#             }
#         ),
#         content_type="application/json",
#     )
#     response = json.loads(request.data)
#     assert (
#         {
#             "password": [
#                 "Length must be between 6 and 32.",
#                 "String does not match expected pattern."
#             ],
#         }
#     ) == response


# def test_signin_user_username_too_long(client):
#     """
#     Test /api/users/signin endpoint with username field
#     contain very long string. other fields are valid.
#     """
#     request = client.post(
#         "/api/users/signin",
#         data=json.dumps(
#             {
#                 "username": "bob_2" * 150,
#                 "email_address": "bob_2@gmail.com",
#                 "password": "123456",
#             }
#         ),
#         content_type="application/json",
#     )
#     response = json.loads(request.data)
#     assert (
#         {
#             "username": [
#                 "Length must be between 3 and 256.",
#             ],
#         }
#     ) == response


# def test_signin_user_username_email_addres_too_long(client):
#     """
#     Test /api/users/signin endpoint with username and email
#     fields contains very long string. other field is valid.
#     """
#     request = client.post(
#         "/api/users/signin",
#         data=json.dumps(
#             {
#                 "username": "bob_2" * 150,
#                 "email_address": "bob_2@gmail.com" * 150,
#                 "password": "123456",
#             }
#         ),
#         content_type="application/json",
#     )
#     response = json.loads(request.data)
#     assert (
#         {
#             "username": [
#                 "Length must be between 3 and 256.",
#             ],
#             "email_address": [
#                 "Length must be between 3 and 256."
#             ],
#         }
#     ) == response


# def test_signin_user_username_email_addres_password_too_long(client):
#     """
#     Test /api/users/signin endpoint with all fields
#     contains very long string.
#     """
#     request = client.post(
#         "/api/users/signin",
#         data=json.dumps(
#             {
#                 "username": "bob_2" * 150,
#                 "email_address": "bob_2@gmail.com" * 150,
#                 "password": "123456" * 150,
#             }
#         ),
#         content_type="application/json",
#     )
#     response = json.loads(request.data)
#     assert (
#         {
#             "username": [
#                 "Length must be between 3 and 256.",
#             ],
#             "email_address": [
#                 "Length must be between 3 and 256."
#             ],
#             "password": [
#                 "Length must be between 6 and 32.",
#             ],
#         }
#     ) == response
