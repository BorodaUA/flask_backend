import os
import sys
import pytest
import json
import logging
from flask import g
from sqlalchemy import create_engine
from sqlalchemy.exc import ProgrammingError, OperationalError
from faker import Faker
import random
sys.path.append(os.getcwd())
from flask_backend import create_app # noqa
from api.models import blog_news # noqa

# pytest -s -o log_cli=true -o log_level=DEBUG


@pytest.fixture(scope='function')
def client(request):
    app = create_app(config_name="testing")
    app.config['test_data'] = generate_test_data()
    with app.test_client() as client:
        logging.debug('Starting the test.')
        default_postgres_db_uri = app.config['POSTGRES_DATABASE_URI']
        test_db_name = list(
            app.config['SQLALCHEMY_BINDS'].values()
        )[0].split('/')[-1]
        create_db(
            default_postgres_db_uri=default_postgres_db_uri,
            test_db_name=test_db_name,
        )

        @app.before_request
        def create_tables():
            engine = g.flask_backend_session.get_bind()
            blog_news.Base.metadata.create_all(engine)

        yield client

        @app.teardown_appcontext
        def shutdown_session_and_delete_db(exception=None):
            logging.debug('Shutting down the test.')
            if g.flask_backend_session:
                g.flask_backend_session.remove()
                engine = g.flask_backend_session.get_bind()
                engine.dispose()
            if g.hacker_news_session:
                g.hacker_news_session.remove()
                engine = g.hacker_news_session.get_bind()
                engine.dispose()
            delete_db(
                default_postgres_db_uri=default_postgres_db_uri,
                test_db_name=test_db_name,
            )


def create_db(default_postgres_db_uri, test_db_name):
    default_engine = create_engine(default_postgres_db_uri)
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


def delete_db(default_postgres_db_uri, test_db_name):
    default_engine = create_engine(default_postgres_db_uri)
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


def generate_test_data():
    '''
    return Faker's test data user
    '''
    fake = Faker()
    fake_user = fake.profile()
    fake_user['password'] = fake.password(
        length=random.randrange(6, 32)
    )
    return fake_user


def test_bn_comment_patch_story_id_comment_id_not_integer(client):
    """
    test PATCH /api/blognews/<story_id>/comments/<comment_id> endpoint
    with story_id and comment_id not integer
    """
    response = client.patch(
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


def test_bn_comment_patch_invalid_story_id_invalid_comment_id(client):
    """
    test PATCH /api/blognews/<story_id>/comments/<comment_id> endpoint
    with invalid story_id, invalid comment_id
    """
    test_user_data = client.application.config['test_data']
    response = client.post(
        "/api/blognews/",
        data=json.dumps(
            {
                'url': test_user_data['website'][0],
                'by': test_user_data['username'],
                'text': test_user_data['residence'],
                'title': test_user_data['address'],
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
                'by': test_user_data['username'],
                'text': test_user_data['residence'],
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
    response = client.patch(
        "/api/blognews/111222333/comments/111222333",
        data=json.dumps(
            {
                "text": test_user_data['address'],
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


def test_bn_comment_patch_valid_story_id_invalid_comment_id(client):
    """
    test PATCH /api/blognews/<story_id>/comments/<comment_id> endpoint
    with valid story_id, invalid comment_id
    """
    test_user_data = client.application.config['test_data']
    response = client.post(
        "/api/blognews/",
        data=json.dumps(
            {
                'url': test_user_data['website'][0],
                'by': test_user_data['username'],
                'text': test_user_data['residence'],
                'title': test_user_data['address'],
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
                'by': test_user_data['username'],
                'text': test_user_data['residence'],
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
    response = client.patch(
        "/api/blognews/1/comments/111222333",
        data=json.dumps(
            {
                "text": test_user_data['address'],
            }
        ),
        content_type="application/json",
    )
    response = json.loads(response.data)
    assert (
        {
            "code": 404,
            "message": "Comment not found"
        }
    ) == response


def test_bn_comment_patch_valid_no_json_data(client):
    """
    test PATCH /api/blognews/<story_id>/comments endpoint
    with valid story_id, valid comment_id
    """
    test_user_data = client.application.config['test_data']
    response = client.post(
        "/api/blognews/",
        data=json.dumps(
            {
                'url': test_user_data['website'][0],
                'by': test_user_data['username'],
                'text': test_user_data['residence'],
                'title': test_user_data['address'],
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
                'by': test_user_data['username'],
                'text': test_user_data['residence'],
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
    response = client.patch(
        "/api/blognews/1/comments/1",
    )
    response = json.loads(response.data)
    assert (
        {
            '_schema': ['Invalid input type.'],
        }
    ) == response


def test_bn_comment_patch_valid_no_required_fields(client):
    """
    test PATCH /api/blognews/<story_id>/comments endpoint
    with valid story_id, comment_id no required fields
    """
    test_user_data = client.application.config['test_data']
    response = client.post(
        "/api/blognews/",
        data=json.dumps(
            {
                'url': test_user_data['website'][0],
                'by': test_user_data['username'],
                'text': test_user_data['residence'],
                'title': test_user_data['address'],
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
                'by': test_user_data['username'],
                'text': test_user_data['residence'],
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
    response = client.patch(
        "/api/blognews/1/comments/1",
        data=json.dumps({}),
        content_type="application/json",
    )
    response = json.loads(response.data)
    assert (
        {
            'text': ['Missing data for required field.'],
        }
    ) == response


def test_bn_comment_patch_valid_required_fields_None(client):
    """
    test PATCH /api/blognews/<story_id>/comments endpoint
    with valid story_id, comment_id required fields are None
    """
    test_user_data = client.application.config['test_data']
    response = client.post(
        "/api/blognews/",
        data=json.dumps(
            {
                'url': test_user_data['website'][0],
                'by': test_user_data['username'],
                'text': test_user_data['residence'],
                'title': test_user_data['address'],
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
                'by': test_user_data['username'],
                'text': test_user_data['residence'],
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
    response = client.patch(
        "/api/blognews/1/comments/1",
        data=json.dumps(
            {
                "text": None
            }
        ),
        content_type="application/json",
    )
    response = json.loads(response.data)
    assert (
        {
            'text': ['Field may not be null.'],
        }
    ) == response


def test_bn_comment_patch_valid_required_fields_invalid_types(client):
    """
    test PATCH /api/blognews/<story_id>/comments endpoint
    with valid story_id, comment_id required fields are invalid types
    """
    test_user_data = client.application.config['test_data']
    response = client.post(
        "/api/blognews/",
        data=json.dumps(
            {
                'url': test_user_data['website'][0],
                'by': test_user_data['username'],
                'text': test_user_data['residence'],
                'title': test_user_data['address'],
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
                'by': test_user_data['username'],
                'text': test_user_data['residence'],
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
    response = client.patch(
        "/api/blognews/1/comments/1",
        data=json.dumps(
            {
                "text": ([1], {3: 4})
            }
        ),
        content_type="application/json",
    )
    response = json.loads(response.data)
    assert (
        {
            'text': ['Not a valid string.'],
        }
    ) == response


def test_bn_comment_patch_valid_empty_required_fields(client):
    """
    test PATCH /api/blognews/<story_id>/comments endpoint
    with valid story_id, comment_id required fields are empty
    """
    test_user_data = client.application.config['test_data']
    response = client.post(
        "/api/blognews/",
        data=json.dumps(
            {
                'url': test_user_data['website'][0],
                'by': test_user_data['username'],
                'text': test_user_data['residence'],
                'title': test_user_data['address'],
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
                'by': test_user_data['username'],
                'text': test_user_data['residence'],
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
    response = client.patch(
        "/api/blognews/1/comments/1",
        data=json.dumps(
            {
                "text": '',
            }
        ),
        content_type="application/json",
    )
    response = json.loads(response.data)
    assert (
        {
            'text': ['Shorter than minimum length 1.'],
        }
    ) == response


def test_bn_comment_patch_valid_required_fields(client):
    """
    test PATCH /api/blognews/<story_id>/comments endpoint
    with valid story_id, comment_id required fields are valid
    """
    test_user_data = client.application.config['test_data']
    response = client.post(
        "/api/blognews/",
        data=json.dumps(
            {
                'url': test_user_data['website'][0],
                'by': test_user_data['username'],
                'text': test_user_data['residence'],
                'title': test_user_data['address'],
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
                'by': test_user_data['username'],
                'text': test_user_data['residence'],
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
    response = client.patch(
        "/api/blognews/1/comments/1",
        data=json.dumps(
            {
                "text": test_user_data['address'],
            }
        ),
        content_type="application/json",
    )
    response = json.loads(response.data)
    assert (
        {
            "code": 200,
            "message": "Comment updated",
        }
    ) == response


def test_bn_comment_patch_extra_field(client):
    """
    test PATCH /api/blognews/<story_id>/comments endpoint
    with valid story_id, comment_id extra field
    """
    test_user_data = client.application.config['test_data']
    response = client.post(
        "/api/blognews/",
        data=json.dumps(
            {
                'url': test_user_data['website'][0],
                'by': test_user_data['username'],
                'text': test_user_data['residence'],
                'title': test_user_data['address'],
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
                'by': test_user_data['username'],
                'text': test_user_data['residence'],
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
    response = client.patch(
        "/api/blognews/1/comments/1",
        data=json.dumps(
            {
                "text": test_user_data['address'],
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
