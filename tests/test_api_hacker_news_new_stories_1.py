import os
import sys
import pytest
import json
import logging
from flask import g
from sqlalchemy import create_engine
from sqlalchemy.exc import ProgrammingError, OperationalError
from tests.hacker_news_test_data import test_row
sys.path.append(os.getcwd())
from flask_backend import create_app # noqa
from api.models import hacker_news # noqa


# pytest -s -o log_cli=true -o log_level=DEBUG


@pytest.fixture(scope='function')
def client(request):
    app = create_app(config_name="testing")
    app.config['test_data'] = test_row
    with app.test_client() as client:
        logging.debug('Starting the test.')
        default_postgres_db_uri = app.config['POSTGRES_DATABASE_URI']
        test_db_name = list(
            app.config['SQLALCHEMY_BINDS'].values()
        )[1].split('/')[-1]
        create_db(
            default_postgres_db_uri=default_postgres_db_uri,
            test_db_name=test_db_name,
        )

        @app.before_request
        def create_tables():
            engine = g.hacker_news_session.get_bind()
            hacker_news.Base.metadata.create_all(engine)
            db_session = g.hacker_news_session
            db_session.add(
                hacker_news.HackerNewsNewStory(**test_row)
            )
            db_session.commit()

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


def test_hn_new_stories_get_no_pagenumber(client):
    """
    test /api/hackernews/newstories/?pagenumber=N endpoint
    with no pagenumber data
    """
    response = client.get("/api/hackernews/newstories/",)
    response = json.loads(response.data)
    assert {"pagenumber": ["Field may not be null."]} == response


def test_hn_new_stories_get_pagenumber_not_integer(client):
    """
    test /api/hackernews/newstories/?pagenumber=N endpoint
    with no pagenumber not an integer
    """
    response = client.get("/api/hackernews/newstories/?pagenumber=A",)
    response = json.loads(response.data)
    assert {"pagenumber": ["Not a valid integer."]} == response


def test_hn_new_stories_get_pagenumber_is_zero(client):
    """
    test /api/hackernews/newstories/?pagenumber=N endpoint
    with pagenumber equal to 0
    """
    response = client.get("/api/hackernews/newstories/?pagenumber=0",)
    response = json.loads(response.data)
    assert (
        {
            "code": 400,
            "message": "pagenumber must be greater then 0"
        }
    ) == response


def test_hn_new_stories_get_pagenumber_is_negative_number(client):
    """
    test /api/hackernews/newstories/?pagenumber=N endpoint
    with pagenumber is a negative number
    """
    response = client.get("/api/hackernews/newstories/?pagenumber=-1",)
    response = json.loads(response.data)
    assert (
        {
            "code": 400,
            "message": "pagenumber must be greater then 0"
        }
    ) == response


def test_hn_new_stories_get_pagenumber_is_big_number(client):
    """
    test /api/hackernews/newstories/?pagenumber=N endpoint
    with pagenumber is a big number, more then pages
    """
    response = client.get("/api/hackernews/newstories/?pagenumber=100",)
    response = json.loads(response.data)
    assert (
        {
            "code": 404,
            "message": "Pagination page not found"
        }
    ) == response


def test_hn_new_stories_get_pagenumber_valid_1(client):
    """
    test /api/hackernews/newstories/?pagenumber=N endpoint
    with pagenumber valid number 1
    """
    test_data = client.application.config['test_data']
    response = client.get("/api/hackernews/newstories/?pagenumber=1",)
    response = json.loads(response.data)
    assert test_data['by'] == response['items'][0]['by']


def test_hn_new_stories_no_story_id_data(client):
    """
    test /api/hackernews/newstories/<story_id> endpoint
    with no <story_id> data
    """
    response = client.get("/api/hackernews/newstories/",)
    response = json.loads(response.data)
    assert {"pagenumber": ["Field may not be null."]} == response


def test_hn_new_stories_story_id_not_iteger(client):
    """
    test /api/hackernews/newstories/<story_id> endpoint
    with <story_id> not iteger
    """
    response = client.get("/api/hackernews/newstories/aaabbbccc",)
    error_response = (
        b'<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">\n'
        b'<title>404 Not Found</title>\n'
        b'<h1>Not Found</h1>\n'
        b'<p>The requested URL was not found on the server. '
        b'If you entered the URL manually please check your '
        b'spelling and try again.</p>\n'
    )
    assert error_response == response.data


def test_hn_new_stories_story_id_not_valid(client):
    """
    test /api/hackernews/newstories/<story_id> endpoint
    with <story_id> not present in database
    """
    response = client.get("/api/hackernews/newstories/11124611558",)
    response = json.loads(response.data)
    assert (
        {
            "code": 404,
            "message": "Story not found"
        }
    ) == response


def test_hn_new_stories_story_id_valid(client):
    """
    test /api/hackernews/newstories/<story_id> endpoint
    with valid <story_id>
    """
    test_data = client.application.config['test_data']
    response = client.get(f"/api/hackernews/newstories/{test_data['hn_id']}",)
    response = json.loads(response.data)
    assert test_data['hn_id'] == response["hn_id"]
