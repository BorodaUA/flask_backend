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


def test_blognews_comments_get_story_id_not_integer(client):
    """
    test GET /api/blognews/<story_id>/comments endpoint
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
    response = client.get(
        "/api/blognews/AAABBBCCC/comments",
    )
    error_response = (
        b'<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">\n'
        b'<title>404 Not Found</title>\n'
        b'<h1>Not Found</h1>\n'
        b'<p>The requested URL was not found on the server. '
        b'If you entered the URL manually please check your '
        b'spelling and try again.</p>\n'
    )
    assert error_response == response.data


def test_blognews_comments_get_invalid_story_id(client):
    """
    test GET /api/blognews/<story_id>/comments endpoint
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
    response = client.get(
        "/api/blognews/111222333/comments",
    )
    response = json.loads(response.data)
    assert (
        {
            "code": 404,
            "message": "Story not found"
        }
    ) == response


def test_blognews_comments_get_valid_story_id(client):
    """
    test GET /api/blognews/<story_id>/comments endpoint
    with valid story_id
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
    response = client.get(
        "/api/blognews/1/comments",
    )
    response = json.loads(response.data)
    assert "test_bob_2" == response[0]['by']


def test_bn_comment_get_story_id_comment_id_not_integer(client):
    """
    test GET /api/blognews/<story_id>/comments/<comment_id> endpoint
    with story_id and comment_id not integer
    """
    response = client.get(
        "/api/blognews/AAABBBCCC/comments/AAABBBCCC",
    )
    error_response = (
        b'<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">\n'
        b'<title>404 Not Found</title>\n'
        b'<h1>Not Found</h1>\n'
        b'<p>The requested URL was not found on the server. '
        b'If you entered the URL manually please check your '
        b'spelling and try again.</p>\n'
    )
    assert error_response == response.data


def test_bn_comment_get_invalid_story_id_invalid_comment_id(client):
    """
    test GET /api/blognews/<story_id>/comments endpoint
    with invalid story_id, invalid comment_id
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
    response = client.get(
        "/api/blognews/111222333/comments/111222333",
    )
    response = json.loads(response.data)
    assert (
        {
            "code": 404,
            "message": "Story not found"
        }
    ) == response


def test_bn_comment_get_valid_story_id_invalid_comment_id(client):
    """
    test GET /api/blognews/<story_id>/comments endpoint
    with valid story_id, invalid comment_id
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
    response = client.get(
        "/api/blognews/1/comments/111222333",
    )
    response = json.loads(response.data)
    assert (
        {
            "code": 404,
            "message": "Comment not found"
        }
    ) == response


def test_bn_comment_get_valid_story_id_valid_comment_id(client):
    """
    test GET /api/blognews/<story_id>/comments endpoint
    with valid story_id, valid comment_id
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
    response = client.get(
        "/api/blognews/1/comments/1",
    )
    response = json.loads(response.data)
    assert 'test comment text' == response['text']


def test_bn_comment_delete_story_id_comment_id_not_integer(client):
    """
    test DELETE /api/blognews/<story_id>/comments/<comment_id> endpoint
    with story_id and comment_id not integer
    """
    response = client.delete(
        "/api/blognews/AAABBBCCC/comments/AAABBBCCC",
    )
    error_response = (
        b'<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">\n'
        b'<title>404 Not Found</title>\n'
        b'<h1>Not Found</h1>\n'
        b'<p>The requested URL was not found on the server. '
        b'If you entered the URL manually please check your '
        b'spelling and try again.</p>\n'
    )
    assert error_response == response.data


def test_bn_comment_delete_invalid_story_id_invalid_comment_id(client):
    """
    test DELETE /api/blognews/<story_id>/comments endpoint
    with invalid story_id, invalid comment_id
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
    response = client.delete(
        "/api/blognews/111222333/comments/111222333",
    )
    response = json.loads(response.data)
    assert (
        {
            "code": 404,
            "message": "Story not found"
        }
    ) == response


def test_bn_comment_delete_valid_story_id_invalid_comment_id(client):
    """
    test DELETE /api/blognews/<story_id>/comments endpoint
    with valid story_id, invalid comment_id
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
    response = client.delete(
        "/api/blognews/1/comments/111222333",
    )
    response = json.loads(response.data)
    assert (
        {
            "code": 404,
            "message": "Comment not found"
        }
    ) == response


def test_bn_comment_delete_valid_story_id_valid_comment_id(client):
    """
    test DELETE /api/blognews/<story_id>/comments endpoint
    with valid story_id, valid comment_id
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
    response = client.delete(
        "/api/blognews/1/comments/1",
    )
    response = json.loads(response.data)
    assert (
        {
            'code': 200,
            'message': 'Comment deleted',
        }
    ) == response
