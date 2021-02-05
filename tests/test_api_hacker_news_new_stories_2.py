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
                hacker_news.HackerNewsNewStory(**test_row)
            )
            db_session.add(
                hacker_news.HackerNewsNewStoryComment(**test_comment_row)
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


def test_api_hn_get_newstories_comments_invalid_story_id(client):
    """
    test GET /api/hackernews/newstories/<story_id>/comments
    with invalid <story_id>
    """
    response = client.get(
        "/api/hackernews/newstories/123456789/comments",
    )
    response = json.loads(response.data)
    assert (
        {
            "code": 404,
            "message": "Story not found"
        }
    ) == response


def test_api_hn_get_newstories_comments_valid_story_id(client):
    """
    test GET /api/hackernews/newstories/<story_id>/comments
    with valid <story_id>
    """
    test_data = client.application.config['test_data']
    test_comment_data = client.application.config['test_comment_data']
    response = client.get(
        f"/api/hackernews/newstories/{test_data['hn_id']}/comments",
    )
    response = json.loads(response.data)
    assert test_comment_data['by'] == response[0]['by']


def test_api_hackernews_post_newstories_comments_invalid_story_id(client):
    """
    test POST /api/hackernews/newstories/<story_id>/comments
    with invalid <story_id>
    """
    test_data = client.application.config['test_data']
    test_comment_data = client.application.config['test_comment_data']
    response = client.post(
        "/api/hackernews/newstories/123456789/comments",
        data=json.dumps(
            {
                'by': test_data['by'],
                'text': test_comment_data['text']
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


def test_api_hn_post_newstories_comments_no_json_data(client):
    """
    test POST /api/hackernews/newstories/<story_id>/comments
    with valid <story_id>, and no json data at all.
    """
    test_data = client.application.config['test_data']
    response = client.post(
        f"/api/hackernews/newstories/{test_data['hn_id']}/comments",
    )
    response = json.loads(response.data)
    assert (
        {
            '_schema': ['Invalid input type.'],

        }
    ) == response


def test_api_hn_post_newstories_comments_no_required_fields(client):
    """
    test POST /api/hackernews/newstories/<story_id>/comments
    with valid <story_id>, and no required fields
    """
    test_data = client.application.config['test_data']
    response = client.post(
        f"/api/hackernews/newstories/{test_data['hn_id']}/comments",
        data=json.dumps({}),
        content_type="application/json",
    )
    response = json.loads(response.data)
    assert (
        {
            'by': ['Missing data for required field.'],
            'text': ['Missing data for required field.']
        }
    ) == response


def test_api_hn_post_newstories_comments_empty_required_fields(client):
    """
    test POST /api/hackernews/newstories/<story_id>/comments
    with valid <story_id>, and empty json data
    """
    test_data = client.application.config['test_data']
    response = client.post(
        f"/api/hackernews/newstories/{test_data['hn_id']}/comments",
        data=json.dumps(
            {
                'by': '',
                'text': ''
            }
        ),
        content_type="application/json",
    )
    response = json.loads(response.data)
    assert (
        {
            'by': ['Shorter than minimum length 1.'],
            'text': ['Shorter than minimum length 1.']
        }
    ) == response


def test_api_hn_post_newstories_comments_valid_required_fields(client):
    """
    test POST /api/hackernews/newstories/<story_id>/comments
    with valid <story_id>, and valid required fields.
    """
    test_data = client.application.config['test_data']
    test_comment_data = client.application.config['test_comment_data']
    response = client.post(
        f"/api/hackernews/newstories/{test_data['hn_id']}/comments",
        data=json.dumps(
            {
                'by': test_data['by'],
                'text': test_comment_data['text']
            }
        ),
        content_type="application/json",
    )
    response = json.loads(response.data)
    assert (
        {
            'code': 201,
            'message': 'Comment added'
        }
    ) == response


def test_api_hn_patch_newstories_comments_invalid_story_id(client):
    """
    test PATCH /api/hackernews/newstories/<story_id>/comments
    with invalid <story_id>, and invalid <comment_id>
    """
    response = client.patch(
        "/api/hackernews/newstories/111222333/comments/111222333",
        data=json.dumps(
            {
                'by': 'test_bob_2',
                'text': 'test bob_2 comment updated from test'
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


def test_api_hn_patch_newstories_comments_valid_story_id(client):
    """
    test PATCH /api/hackernews/newstories/<story_id>/comments
    with valid <story_id>, and invalid <comment_id>
    """
    test_data = client.application.config['test_data']
    response = client.patch(
        f"/api/hackernews/newstories/{test_data['hn_id']}/comments/111222333",
        data=json.dumps(
            {
                'by': 'test_bob_2',
                'text': 'test bob_2 comment updated from test'
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


def test_api_hn_patch_newstories_comments_no_json_data(client):
    """
    test PATCH /api/hackernews/newstories/<story_id>/comments
    with valid <story_id>, valid <comment_id> and no json data.
    """
    test_data = client.application.config['test_data']
    test_comment_data = client.application.config['test_comment_data']
    response = client.patch(
        f"/api/hackernews/newstories/{test_data['hn_id']}/"
        f"comments/{test_comment_data['id']}",
    )
    response = json.loads(response.data)
    assert (
        {
            '_schema': ['Invalid input type.'],
        }
    ) == response


def test_api_hn_patch_newstories_comments_no_required_fields(client):
    """
    test PATCH /api/hackernews/newstories/<story_id>/comments
    with valid <story_id>, valid <comment_id> and no required fields.
    """
    test_data = client.application.config['test_data']
    test_comment_data = client.application.config['test_comment_data']
    response = client.patch(
        f"/api/hackernews/newstories/{test_data['hn_id']}/"
        f"comments/{test_comment_data['id']}",
        data=json.dumps({}),
        content_type="application/json",
    )
    response = json.loads(response.data)
    assert (
        {
            'by': ['Missing data for required field.'],
            'text': ['Missing data for required field.']
        }
    ) == response
