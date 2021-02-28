import os
import sys
import pytest
import json
import logging
from flask import g
from sqlalchemy import create_engine
from sqlalchemy.exc import ProgrammingError, OperationalError
from tests.hacker_news_test_data import test_row, test_comment_row
sys.path.append(os.getcwd())
from flask_backend import create_app # noqa
from api.models import hacker_news # noqa


# pytest -s -o log_cli=true -o log_level=DEBUG


@pytest.fixture(scope='function')
def client(request):
    app = create_app(config_name="testing")
    app.config['test_data'] = test_row
    app.config['test_comment_data'] = test_comment_row
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
                hacker_news.HackerNewsTopStory(**test_row)
            )
            db_session.add(
                hacker_news.HackerNewsTopStoryComment(**test_comment_row)
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


def test_hackernews_patch_topstories_comments_required_fields_empty(client):
    """
    test PATCH /api/hackernews/topstories/<story_id>/comments
    with valid <story_id>, valid <comment_id> and required fields are empty.
    """
    test_data = client.application.config['test_data']
    test_comment_data = client.application.config['test_comment_data']
    response = client.patch(
        f"/api/hackernews/topstories/{test_data['hn_id']}/"
        f"comments/{test_comment_data['id']}",
        data=json.dumps(
            {
                'text': ''
            }
        ),
        content_type="application/json",
    )
    response = json.loads(response.data)
    assert (
        {
            'text': ['Shorter than minimum length 1.']
        }
    ) == response


def test_hackernews_patch_topstories_comments_required_fields_valid(client):
    """
    test PATCH /api/hackernews/topstories/<story_id>/comments
    with valid <story_id>, valid <comment_id> and required fields are valid.
    """
    test_data = client.application.config['test_data']
    test_comment_data = client.application.config['test_comment_data']
    response = client.patch(
        f"/api/hackernews/topstories/{test_data['hn_id']}/"
        f"comments/{test_comment_data['id']}",
        data=json.dumps(
            {
                'text': test_data['title']
            }
        ),
        content_type="application/json",
    )
    response = json.loads(response.data)
    assert (
        {
            'code': 200,
            'message': 'Comment updated'
        }
    ) == response


def test_api_hackernews_delete_topstories_comments_valid_story_id(client):
    """
    test DELETE /api/hackernews/topstories/<story_id>/comments
    with valid <story_id>, and invalid <comment_id>
    """
    test_data = client.application.config['test_data']
    response = client.delete(
        f"/api/hackernews/topstories/{test_data['hn_id']}/comments/111222333",
    )
    response = json.loads(response.data)
    assert (
        {
            "code": 404,
            "message": "Comment not found"
        }
    ) == response


def test_api_hackernews_delete_topstories_comments_invalid_story_id(client):
    """
    test DELETE /api/hackernews/topstories/<story_id>/comments/<comment_id>
    with invalid <story_id>, and valid <comment_id>
    """
    test_comment_data = client.application.config['test_comment_data']
    response = client.delete(
        f"/api/hackernews/topstories/111222333/comments/"
        f"{test_comment_data['id']}",
    )
    response = json.loads(response.data)
    assert (
        {
            "code": 404,
            "message": "Story not found"
        }
    ) == response


def test_hackernews_delete_topstories_comments_required_fields_valid(client):
    """
    test DELETE /api/hackernews/topstories/<story_id>/comments/<comment_id>
    with valid <story_id>, valid <comment_id>
    """
    test_data = client.application.config['test_data']
    test_comment_data = client.application.config['test_comment_data']
    response = client.delete(
        f"/api/hackernews/topstories/{test_data['hn_id']}/"
        f"comments/{test_comment_data['id']}",
    )
    response = json.loads(response.data)
    assert (
        {
            'code': 200,
            'message': 'Comment deleted'
        }
    ) == response
