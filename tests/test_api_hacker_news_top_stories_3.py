import os
import sys
import pytest
import json
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.exc import ProgrammingError, OperationalError
from sqlalchemy.ext.automap import automap_base
sys.path.append(os.getcwd())
from flask_backend import create_app, db # noqa
from api.models import hacker_news # noqa

# pytest -s -o log_cli=true -o log_level=DEBUG


@pytest.fixture(scope='function')
def client(request):
    app = create_app("testing")
    db.init_app(app)
    with app.test_client() as client:
        with app.app_context():
            logging.debug('Starting the test.')
            db_name = db.get_engine(bind="hacker_news").url.database
            create_db(test_db_name=db_name)
            test_db_engine = db.get_engine(bind="hacker_news")
            hacker_news.Base.session = scoped_session(
                sessionmaker(
                    autocommit=False,
                    autoflush=False,
                    bind=test_db_engine,
                )
            )
            hacker_news.Base.query = hacker_news.Base.session.query_property()
            hacker_news.Base.metadata.create_all(test_db_engine)

        yield client

        @app.teardown_appcontext
        def shutdown_session_and_delete_db(exception=None):
            logging.debug('Shutting down the test.')
            hacker_news.Base.session.close()
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


test_row = {
    "by": "pseudolus",
    "dead": None,
    "deleted": None,
    "descendants": 328,
    "hn_id": 24611558,
    "id": "2402",
    "kids": [
        24611767,
    ],
    "origin": "hacker_news",
    "parent": None,
    "parsed_time": "2020-09-28T08:20:23.918000",
    "parts": None,
    "poll": None,
    "score": 207,
    "text": None,
    "time": 1601253055,
    "title": (
        "Judge temporarily blocks U.S. ban on TikTok"
        "downloads from U.S. app stores"
    ),
    "type": "story",
    "url": (
        "https://www.reuters.com/article/us-usa-tiktok-ban-judge/"
        "judge-temporarily-blocks-u-s-ban-on-tiktok-downloads-"
        "from-u-s-app-stores-idUSKBN26J00R"
    )
}
test_comment_row = {
        "by": "localhost",
        "dead": None,
        "deleted": None,
        "descendants": None,
        "hn_id": "24611767",
        "id": "125",
        "kids": [
            24614360,
        ],
        "origin": "hacker_news",
        "parent": 24611558,
        "parsed_time": "2020-09-28T14:18:18.589000",
        "parts": None,
        "poll": None,
        "score": None,
        "text": (
            'Unlike some other commenters below, I don&#x27;t believe'
            'that this is a privacy issue. Instead, I believe that it is'
            'a national security issue because TikTok is controllable by'
            'the CCP which is ideologically opposed to the United States.'
            'The next global conflict will likely be one between the east'
            'and the west, with control of information being advantageous'
            'to both sides in the conflict. China already blocks the western'
            'Internet, so they have an advantage by default.<p>This position'
            'is covered much more eloquently than I put it above in'
            'Ben Thompson&#x27;s &quot;The TikTok War&quot; [1].<p>[1]'
            '<a href=\"https:&#x2F;&#x2F;stratechery.com&#x2F;2020&#x2F;the-'
            'tiktok-war&#x2F;\" rel=\"nofollow\">https:&#x2F;&#x2F;'
            'stratechery.com&#x2F;2020&#x2F;the-tiktok-war&#x2F;</a>"'
        ),
        "time": 1601255009,
        "title": None,
        "type": "comment",
        "url": None,
}


def insert_in_table(insert_data, db_address, table_name):
    Base = automap_base()
    engine = create_engine(db_address)
    ###
    Base.prepare(engine, reflect=True)
    table = Base.classes[table_name]
    Session = sessionmaker(bind=engine)
    session = Session()
    data = table(**insert_data)
    session.add(data)
    session.commit()
    session.close()
    engine.dispose()


def test_hackernews_patch_topstories_comments_required_fields_empty(client):
    """
    test PATCH /api/hackernews/topstories/<story_id>/comments
    with valid <story_id>, valid <comment_id> and required fields are empty.
    """
    insert_in_table(
        insert_data=test_row,
        db_address=os.environ.get('TEST_HACKER_NEWS_DATABASE_URI'),
        table_name="hacker_news_top_story"
    )
    insert_in_table(
        insert_data=test_comment_row,
        db_address=os.environ.get('TEST_HACKER_NEWS_DATABASE_URI'),
        table_name="hacker_news_top_story_comment"
    )
    response = client.patch(
        f"/api/hackernews/topstories/{test_row['hn_id']}/"
        f"comments/{test_comment_row['id']}",
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


def test_hackernews_patch_topstories_comments_required_fields_valid(client):
    """
    test PATCH /api/hackernews/topstories/<story_id>/comments
    with valid <story_id>, valid <comment_id> and required fields are valid.
    """
    insert_in_table(
        insert_data=test_row,
        db_address=os.environ.get('TEST_HACKER_NEWS_DATABASE_URI'),
        table_name="hacker_news_top_story"
    )
    insert_in_table(
        insert_data=test_comment_row,
        db_address=os.environ.get('TEST_HACKER_NEWS_DATABASE_URI'),
        table_name="hacker_news_top_story_comment"
    )
    response = client.patch(
        f"/api/hackernews/topstories/{test_row['hn_id']}/"
        f"comments/{test_comment_row['id']}",
        data=json.dumps(
            {
                'by': "localhost",
                'text': 'changed text from the test.'
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
    insert_in_table(
        insert_data=test_row,
        db_address=os.environ.get('TEST_HACKER_NEWS_DATABASE_URI'),
        table_name="hacker_news_top_story"
    )
    response = client.delete(
        f"/api/hackernews/topstories/{test_row['hn_id']}/comments/111222333",
        data=json.dumps(
            {
                'by': 'test_bob_2',
                'text': 'text from delete test'
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


def test_hackernews_delete_topstories_comments_required_fields_valid(client):
    """
    test DELETE /api/hackernews/topstories/<story_id>/comments/<comment_id>
    with valid <story_id>, valid <comment_id> and required fields are valid.
    """
    insert_in_table(
        insert_data=test_row,
        db_address=os.environ.get('TEST_HACKER_NEWS_DATABASE_URI'),
        table_name="hacker_news_top_story"
    )
    insert_in_table(
        insert_data=test_comment_row,
        db_address=os.environ.get('TEST_HACKER_NEWS_DATABASE_URI'),
        table_name="hacker_news_top_story_comment"
    )
    response = client.delete(
        f"/api/hackernews/topstories/{test_row['hn_id']}/"
        f"comments/{test_comment_row['id']}",
    )
    response = json.loads(response.data)
    assert (
        {
            'code': 200,
            'message': 'Comment deleted'
        }
    ) == response


def test_hackernews_delete_topstories_comments_valid_2_times(client):
    """
    test DELETE /api/hackernews/topstories/<story_id>/comments/<comment_id>
    with valid <story_id>, valid <comment_id> and required fields are valid.
    2 times in a row
    """
    insert_in_table(
        insert_data=test_row,
        db_address=os.environ.get('TEST_HACKER_NEWS_DATABASE_URI'),
        table_name="hacker_news_top_story"
    )
    insert_in_table(
        insert_data=test_comment_row,
        db_address=os.environ.get('TEST_HACKER_NEWS_DATABASE_URI'),
        table_name="hacker_news_top_story_comment"
    )
    response = client.delete(
        f"/api/hackernews/topstories/{test_row['hn_id']}/"
        f"comments/{test_comment_row['id']}",
    )
    response = json.loads(response.data)
    assert (
        {
            'code': 200,
            'message': 'Comment deleted'
        }
    ) == response
    response = client.delete(
        f"/api/hackernews/topstories/{test_row['hn_id']}/"
        f"comments/{test_comment_row['id']}",
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
    insert_in_table(
        insert_data=test_row,
        db_address=os.environ.get('TEST_HACKER_NEWS_DATABASE_URI'),
        table_name="hacker_news_top_story"
    )
    response = client.delete(
        f"/api/hackernews/topstories/111222333/comments/"
        f"{test_comment_row['id']}",
    )
    response = json.loads(response.data)
    assert (
        {
            "code": 404,
            "message": "Story not found"
        }
    ) == response


def test_api_hackernews_delete_topstories_comments_story_id_not_int(client):
    """
    test DELETE /api/hackernews/topstories/<story_id>/comments/<comment_id>
    with <story_id> not integer, and valid <comment_id>
    """
    insert_in_table(
        insert_data=test_row,
        db_address=os.environ.get('TEST_HACKER_NEWS_DATABASE_URI'),
        table_name="hacker_news_top_story"
    )
    insert_in_table(
        insert_data=test_comment_row,
        db_address=os.environ.get('TEST_HACKER_NEWS_DATABASE_URI'),
        table_name="hacker_news_top_story_comment"
    )
    response = client.delete(
        f"/api/hackernews/topstories/aa77##[]/"
        f"comments/{test_comment_row['id']}",
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


def test_hackernews_delete_topstories_comments_comment_id_invalid(client):
    """
    test DELETE /api/hackernews/topstories/<story_id>/comments/<comment_id>
    with valid <story_id>, invalid <comment_id> not present in the db
    """
    insert_in_table(
        insert_data=test_row,
        db_address=os.environ.get('TEST_HACKER_NEWS_DATABASE_URI'),
        table_name="hacker_news_top_story"
    )
    insert_in_table(
        insert_data=test_comment_row,
        db_address=os.environ.get('TEST_HACKER_NEWS_DATABASE_URI'),
        table_name="hacker_news_top_story_comment"
    )
    response = client.delete(
        f"/api/hackernews/topstories/{test_row['hn_id']}/"
        f"comments/111222333",
    )
    response = json.loads(response.data)
    assert (
        {
            "code": 404,
            "message": "Comment not found"
        }
    ) == response


def test_hackernews_delete_topstories_comments_comment_id_not_int(client):
    """
    test DELETE /api/hackernews/topstories/<story_id>/comments/<comment_id>
    with valid <story_id>, and <comment_id> not integer
    """
    insert_in_table(
        insert_data=test_row,
        db_address=os.environ.get('TEST_HACKER_NEWS_DATABASE_URI'),
        table_name="hacker_news_top_story"
    )
    insert_in_table(
        insert_data=test_comment_row,
        db_address=os.environ.get('TEST_HACKER_NEWS_DATABASE_URI'),
        table_name="hacker_news_top_story_comment"
    )
    response = client.delete(
        f"/api/hackernews/topstories/{test_row['hn_id']}/"
        f"comments/aa11[]@!*",
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
