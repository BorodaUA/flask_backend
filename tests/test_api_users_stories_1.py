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


def test_users_stories_valid_data(client):
    '''
    test GET /api/users/<username>/stories/?pagenumber=N , getting up to 500
    user's stories, valid data
    '''
    # add story
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
    response = client.get(
        f"/api/users/{test_user_data['username']}/stories/?pagenumber=1",
    )
    response = json.loads(response.data)
    assert test_user_data['username'] == response['items'][0]['by']


def test_users_stories_no_pagenumber(client):
    '''
    test GET /api/users/<username>/stories , getting up to 500
    user's stories, no ?pagenumber=N parameter
    '''
    # add story
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
    response = client.get(
        f"/api/users/{test_user_data['username']}/stories/",
    )
    response = json.loads(response.data)
    assert (
        {"pagenumber": ["Field may not be null."]} == response
    )


def test_users_stories_pagenumber_not_int(client):
    '''
    test GET /api/users/<username>/stories , getting up to 500
    user's stories, ?pagenumber=not_integer
    '''
    # add story
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
    response = client.get(
        f"/api/users/{test_user_data['username']}/stories/?pagenumber=not_int",
    )
    response = json.loads(response.data)
    assert (
        {"pagenumber": ["Not a valid integer."]} == response
    )


def test_users_stories_pagenumber_is_zero(client):
    '''
    test GET /api/users/<username>/stories , getting up to 500
    user's stories, ?pagenumber=0 , is zero
    '''
    # add story
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
    response = client.get(
        f"/api/users/{test_user_data['username']}/stories/?pagenumber=0",
    )
    response = json.loads(response.data)
    assert (
        {
            "code": 400,
            "message": "pagenumber must be greater then 0"
        }
    ) == response


def test_users_stories_pagenumber_is_more_than_pages_available(client):
    '''
    test GET /api/users/<username>/stories , getting up to 500
    user's stories, ?pagenumber=100 , more than pages available
    '''
    # add story
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
    response = client.get(
        f"/api/users/{test_user_data['username']}/stories/?pagenumber=100",
    )
    response = json.loads(response.data)
    assert (
        {
            "code": 404,
            "message": "Pagination page not found"
        }
    ) == response


def test_users_story_id_valid(client):
    '''
    test GET /api/users/<username>/stories/<story_id> , user's story
    <story_id> valid
    '''
    # add story
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
    response = client.get(
        f"/api/users/{test_user_data['username']}/stories/1",
    )
    response = json.loads(response.data)
    assert test_user_data['username'] == response['by']


def test_users_story_id_not_int(client):
    '''
    test GET /api/users/<username>/stories/<story_id> , user's story
    <story_id> not integer
    '''
    # add story
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
    response = client.get(
        f"/api/users/{test_user_data['username']}/stories/not_int",
    )
    response = json.loads(response.data)
    assert {"story_id": ["Not a valid integer."]} == response


def test_users_story_not_in_db(client):
    '''
    test GET /api/users/<username>/stories/<story_id> , user's story
    <story_id> not in the database
    '''
    # add story
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
    response = client.get(
        f"/api/users/{test_user_data['username']}/stories/111222333",
    )
    response = json.loads(response.data)
    assert (
        {
            "code": 404,
            "message": "story not found"
        }
    ) == response


def test_users_comments_valid_data(client):
    '''
    test GET /api/users/<username>/comments , getting up to 500
    user's comments, valid data
    '''
    # add story
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
    # add comment
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
    # get user's comments
    response = client.get(
        f"/api/users/{test_user_data['username']}/comments/?pagenumber=1",
    )
    response = json.loads(response.data)
    assert test_user_data['username'] == response['items'][0]['by']


def test_users_comments_no_pagenumber(client):
    '''
    test GET /api/users/<username>/comments/?pagenumber=N , getting up to 500
    user's comments, no ?pagenumber=N parameter
    '''
    # add story
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
    # add comment
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
    # get user's comments
    response = client.get(
        f"/api/users/{test_user_data['username']}/comments/",
    )
    response = json.loads(response.data)
    assert (
        {"pagenumber": ["Field may not be null."]} == response
    )


def test_users_comments_pagenumber_not_int(client):
    '''
    test GET /api/users/<username>/comments/?pagenumber=N , getting up to 500
    user's comments, ?pagenumber=not_integer
    '''
    # add story
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
    # add comment
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
    # get user's comments
    response = client.get(
        f"/api/users/{test_user_data['username']}/comments"
        "/?pagenumber=not_int",

    )
    response = json.loads(response.data)
    assert (
        {"pagenumber": ["Not a valid integer."]} == response
    )


def test_users_comments_pagenumber_is_zero(client):
    '''
    test GET /api/users/<username>/comments/?pagenumber=N , getting up to 500
    user's comments, ?pagenumber=0 is zero
    '''
    # add story
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
    # add comment
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
    # get user's comments
    response = client.get(
        f"/api/users/{test_user_data['username']}/comments"
        "/?pagenumber=0",

    )
    response = json.loads(response.data)
    assert (
        {
            "code": 400,
            "message": "pagenumber must be greater then 0"
        }
    ) == response


def test_users_comments_pagenumber_is_more_than_pages_available(client):
    '''
    test GET /api/users/<username>/comments/?pagenumber=N , getting up to 500
    user's comments, ?pagenumber=100 is more that pages available
    '''
    # add story
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
    # add comment
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
    # get user's comments
    response = client.get(
        f"/api/users/{test_user_data['username']}/comments"
        "/?pagenumber=100",

    )
    response = json.loads(response.data)
    assert (
        {
            "code": 404,
            "message": "Pagination page not found"
        }
    ) == response
