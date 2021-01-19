import os
import sys
import pytest
import json
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.exc import ProgrammingError, OperationalError
sys.path.append(os.getcwd())
from flask_backend import create_app, db # noqa
from api.models import blog_news # noqa

# pytest -s -o log_cli=true -o log_level=DEBUG


@pytest.fixture(scope='function')
def client(request):
    app = create_app("testing")
    db.init_app(app)
    with app.test_client() as client:
        with app.app_context():
            logging.debug('Starting the test.')
            db_name = db.get_engine(bind="flask_backend").url.database
            create_db(test_db_name=db_name)
            test_db_engine = db.get_engine(bind="flask_backend")
            blog_news.Base.session = scoped_session(
                sessionmaker(
                    autocommit=False,
                    autoflush=False,
                    bind=test_db_engine,
                )
            )
            blog_news.Base.query = blog_news.Base.session.query_property()
            blog_news.Base.metadata.create_all(test_db_engine)

        yield client

        @app.teardown_appcontext
        def shutdown_session_and_delete_db(exception=None):
            logging.debug('Shutting down the test.')
            blog_news.Base.session.close()
            test_db_engine.dispose()
            delete_db(test_db_name=db_name)


def create_db(test_db_name):
    default_postgres_db_url = os.environ.get("POSTGRES_DATABASE_URI")
    default_engine = create_engine(default_postgres_db_url)
    default_engine = default_engine.execution_options(
        isolation_level="AUTOCOMMIT"
    )
    conn = default_engine.connect()
    # Try to delete Database
    try:
        conn.execute(
            f"DROP DATABASE "
            f"{test_db_name};"
        )
    except ProgrammingError as err:
        logging.debug(err)
        conn.execute("ROLLBACK")
    except OperationalError as err:
        logging.debug(err)
        conn.execute("ROLLBACK")
    # Try to create Database
    try:
        conn.execute(
            f"CREATE DATABASE "
            f"{test_db_name} "
            f"ENCODING 'utf8' TEMPLATE template1"
        )
    except ProgrammingError as err:
        logging.debug(err)
        conn.execute("ROLLBACK")
    except OperationalError as err:
        logging.debug(err)
        conn.execute("ROLLBACK")
    conn.close()
    default_engine.dispose()
    return


def delete_db(test_db_name):
    default_postgres_db_url = os.environ.get("POSTGRES_DATABASE_URI")
    default_engine = create_engine(default_postgres_db_url)
    default_engine = default_engine.execution_options(
        isolation_level="AUTOCOMMIT"
    )
    conn = default_engine.connect()
    try:
        conn.execute(
            f"DROP DATABASE "
            f"{test_db_name};"
        )
    except ProgrammingError as err:
        logging.debug(err)
        conn.execute("ROLLBACK")
    except OperationalError as err:
        logging.debug(err)
        conn.execute("ROLLBACK")
    conn.close()
    default_engine.dispose()
    return


def test_blognews_delete_no_story_id(client):
    """
    test DELETE /api/blognews/<story_id> endpoint
    with no story_id data
    """
    response = client.post(
        "/api/blognews/",
        data=json.dumps(
            {
                'url': 'https://www.google.com/',
                'by': 'test_bob_2',
                'text': 'text from test',
                'title': 'title from test',
            }
        ),
        content_type="application/json",
    )
    response = json.loads(response.data)
    assert (
        {
            'code': 201,
            'message': 'Story added'
        }
    ) == response
    response = client.delete("/api/blognews/")
    response = json.loads(response.data)
    assert (
        {
            "message": 'The method is not allowed for the requested URL.'
        }
    ) == response


def test_blognews_delete_story_id_not_integer(client):
    """
    test DELETE /api/blognews/<story_id> endpoint
    with story_id not integer
    """
    response = client.post(
        "/api/blognews/",
        data=json.dumps(
            {
                'url': 'https://www.google.com/',
                'by': 'test_bob_2',
                'text': 'text from test',
                'title': 'title from test',
            }
        ),
        content_type="application/json",
    )
    response = json.loads(response.data)
    assert (
        {
            'code': 201,
            'message': 'Story added'
        }
    ) == response
    response = client.delete("/api/blognews/not_integer")
    response = json.loads(response.data)
    assert {"story_id": ["Not a valid integer."]} == response


def test_blognews_delete_story_id_not_in_db(client):
    """
    test DELETE /api/blognews/<story_id> endpoint
    with story_id not present in the database
    """
    response = client.post(
        "/api/blognews/",
        data=json.dumps(
            {
                'url': 'https://www.google.com/',
                'by': 'test_bob_2',
                'text': 'text from test',
                'title': 'title from test',
            }
        ),
        content_type="application/json",
    )
    response = json.loads(response.data)
    assert (
        {
            'code': 201,
            'message': 'Story added'
        }
    ) == response
    response = client.delete("/api/blognews/111222333")
    response = json.loads(response.data)
    assert (
        {
            "code": 404,
            "message": "Story not found"
        }
    ) == response


def test_blognews_delete_valid_story_id(client):
    """
    test DELETE /api/blognews/<story_id> endpoint
    with valid story_id, no json data
    """
    response = client.post(
        "/api/blognews/",
        data=json.dumps(
            {
                'url': 'https://www.google.com/',
                'by': 'test_bob_2',
                'text': 'text from test',
                'title': 'title from test',
            }
        ),
        content_type="application/json",
    )
    response = json.loads(response.data)
    assert (
        {
            'code': 201,
            'message': 'Story added'
        }
    ) == response
    response = client.delete("/api/blognews/1")
    response = json.loads(response.data)
    assert (
        {
            "code": 200,
            "message": "Story deleted"
        }
    ) == response


def test_blognews_comments_post_invalid_story_id(client):
    """
    test POST /api/blognews/<story_id>/comments endpoint
    with invalid story_id
    """
    response = client.post(
        "/api/blognews/",
        data=json.dumps(
            {
                'url': 'https://www.google.com/',
                'by': 'test_bob_2',
                'text': 'text from test',
                'title': 'title from test',
            }
        ),
        content_type="application/json",
    )
    response = json.loads(response.data)
    assert (
        {
            'code': 201,
            'message': 'Story added'
        }
    ) == response
    response = client.post(
        "/api/blognews/111222333/comments",
        data=json.dumps(
            {
                'by': 'test_bob_2',
                'text': 'test comment text',
            }
        ),
        content_type="application/json",
    )
    response = json.loads(response.data)
    assert (
        {
            "code": 404,
            "message": "Story not found"
        }
    ) == response


def test_blognews_comments_post_no_json_data(client):
    """
    test POST /api/blognews/<story_id>/comments endpoint
    with valid story_id, and no json data
    """
    response = client.post(
        "/api/blognews/",
        data=json.dumps(
            {
                'url': 'https://www.google.com/',
                'by': 'test_bob_2',
                'text': 'text from test',
                'title': 'title from test',
            }
        ),
        content_type="application/json",
    )
    response = json.loads(response.data)
    assert (
        {
            'code': 201,
            'message': 'Story added'
        }
    ) == response
    response = client.post(
        "/api/blognews/1/comments",
    )
    response = json.loads(response.data)
    assert (
        {
            '_schema': ['Invalid input type.'],
        }
    ) == response


def test_blognews_comments_post_no_required_fields(client):
    """
    test POST /api/blognews/<story_id>/comments endpoint
    with valid story_id and no required fields
    """
    response = client.post(
        "/api/blognews/",
        data=json.dumps(
            {
                'url': 'https://www.google.com/',
                'by': 'test_bob_2',
                'text': 'text from test',
                'title': 'title from test',
            }
        ),
        content_type="application/json",
    )
    response = json.loads(response.data)
    assert (
        {
            'code': 201,
            'message': 'Story added'
        }
    ) == response
    response = client.post(
        "/api/blognews/1/comments",
        data=json.dumps({}),
        content_type="application/json",
    )
    response = json.loads(response.data)
    assert (
        {
            'by': ['Missing data for required field.'],
            'text': ['Missing data for required field.'],
        }
    ) == response


def test_blognews_comments_post_required_fields_None(client):
    """
    test POST /api/blognews/<story_id>/comments endpoint
    with valid story_id and required fields values is None
    """
    response = client.post(
        "/api/blognews/",
        data=json.dumps(
            {
                'url': 'https://www.google.com/',
                'by': 'test_bob_2',
                'text': 'text from test',
                'title': 'title from test',
            }
        ),
        content_type="application/json",
    )
    response = json.loads(response.data)
    assert (
        {
            'code': 201,
            'message': 'Story added'
        }
    ) == response
    response = client.post(
        "/api/blognews/1/comments",
        data=json.dumps(
            {
                'by': None,
                'text': None,
            }
        ),
        content_type="application/json",
    )
    response = json.loads(response.data)
    assert (
        {
            'by': ['Field may not be null.'],
            'text': ['Field may not be null.'],
        }
    ) == response


def test_blognews_comments_post_required_fields_invalid_types(client):
    """
    test POST /api/blognews/<story_id>/comments endpoint
    with valid story_id and required fields are invalid types
    """
    response = client.post(
        "/api/blognews/",
        data=json.dumps(
            {
                'url': 'https://www.google.com/',
                'by': 'test_bob_2',
                'text': 'text from test',
                'title': 'title from test',
            }
        ),
        content_type="application/json",
    )
    response = json.loads(response.data)
    assert (
        {
            'code': 201,
            'message': 'Story added'
        }
    ) == response
    response = client.post(
        "/api/blognews/1/comments",
        data=json.dumps(
            {
                'by': [[1]],
                'text': {2: 'second'},
            }
        ),
        content_type="application/json",
    )
    response = json.loads(response.data)
    assert (
        {
            'by': ['Not a valid string.'],
            'text': ['Not a valid string.'],
        }
    ) == response


def test_blognews_comments_post_empty_required_fields(client):
    """
    test POST /api/blognews/<story_id>/comments endpoint
    with valid story_id and required fields are empty
    """
    response = client.post(
        "/api/blognews/",
        data=json.dumps(
            {
                'url': 'https://www.google.com/',
                'by': 'test_bob_2',
                'text': 'text from test',
                'title': 'title from test',
            }
        ),
        content_type="application/json",
    )
    response = json.loads(response.data)
    assert (
        {
            'code': 201,
            'message': 'Story added'
        }
    ) == response
    response = client.post(
        "/api/blognews/1/comments",
        data=json.dumps(
            {
                'by': '',
                'text': '',
            }
        ),
        content_type="application/json",
    )
    response = json.loads(response.data)
    assert (
        {
            'by': ['Shorter than minimum length 2.'],
            'text': ['Shorter than minimum length 1.'],
        }
    ) == response


def test_blognews_comments_post_valid_required_fields(client):
    """
    test POST /api/blognews/<story_id>/comments endpoint
    with valid story_id and required fields are valid
    """
    response = client.post(
        "/api/blognews/",
        data=json.dumps(
            {
                'url': 'https://www.google.com/',
                'by': 'test_bob_2',
                'text': 'text from test',
                'title': 'title from test',
            }
        ),
        content_type="application/json",
    )
    response = json.loads(response.data)
    assert (
        {
            'code': 201,
            'message': 'Story added'
        }
    ) == response
    response = client.post(
        "/api/blognews/1/comments",
        data=json.dumps(
            {
                'by': 'test_bob_2',
                'text': 'test comment text',
            }
        ),
        content_type="application/json",
    )
    response = json.loads(response.data)
    assert (
        {
            'code': 201,
            'message': 'Comment added',
        }
    ) == response


def test_blognews_comments_post_extra_field(client):
    """
    test POST /api/blognews/<story_id>/comments endpoint
    with valid story_id and extra field
    """
    response = client.post(
        "/api/blognews/",
        data=json.dumps(
            {
                'url': 'https://www.google.com/',
                'by': 'test_bob_2',
                'text': 'text from test',
                'title': 'title from test',
            }
        ),
        content_type="application/json",
    )
    response = json.loads(response.data)
    assert (
        {
            'code': 201,
            'message': 'Story added'
        }
    ) == response
    response = client.post(
        "/api/blognews/1/comments",
        data=json.dumps(
            {
                'by': 'test_bob_2',
                'text': 'test comment text',
                'new_field': 'new field outside the schema'
            }
        ),
        content_type="application/json",
    )
    response = json.loads(response.data)
    assert (
        {
            'new_field': ['Unknown field.']
        }
    ) == response
