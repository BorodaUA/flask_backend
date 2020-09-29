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
        24611659,
        24612195,
        24612606,
        24611805,
        24613796,
        24611815,
        24611647,
        24612078,
        24612723,
        24612080,
        24611878,
        24612556,
        24611930,
        24612156,
        24611661,
        24611837,
        24612653,
        24611712
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


def test_api_home_page(client):
    """
    Test /api/ endpont
    """
    response = client.get("/api/")
    response = json.loads(response.data)
    assert "Api Home page" == response["message"]


def test_hn_top_stories_get_no_pagenumber(client):
    """
    test /api/hackernews/topstories/?pagenumber=N endpoint
    with no pagenumber data
    """
    insert_in_table(
        insert_data=test_row,
        db_address=os.environ.get('TEST_HACKER_NEWS_DATABASE_URI'),
        table_name="hacker_news_top_story"
    )
    response = client.get("/api/hackernews/topstories/",)
    response = json.loads(response.data)
    assert {"pagenumber": ["Field may not be null."]} == response


def test_hn_top_stories_get_pagenumber_not_integer(client):
    """
    test /api/hackernews/topstories/?pagenumber=N endpoint
    with pagenumber not an integer
    """
    insert_in_table(
        insert_data=test_row,
        db_address=os.environ.get('TEST_HACKER_NEWS_DATABASE_URI'),
        table_name="hacker_news_top_story"
    )
    response = client.get("/api/hackernews/topstories/?pagenumber=A",)
    response = json.loads(response.data)
    assert {"pagenumber": ["Not a valid integer."]} == response


def test_hn_top_stories_get_pagenumber_is_zero(client):
    """
    test /api/hackernews/topstories/?pagenumber=N endpoint
    with pagenumber equal to 0
    """
    insert_in_table(
        insert_data=test_row,
        db_address=os.environ.get('TEST_HACKER_NEWS_DATABASE_URI'),
        table_name="hacker_news_top_story"
    )
    response = client.get("/api/hackernews/topstories/?pagenumber=0",)
    response = json.loads(response.data)
    assert (
        {
            "code": 400,
            "message": "pagenumber must be greater then 0"
        }
    ) == response


def test_hn_top_stories_get_pagenumber_is_negative_number(client):
    """
    test /api/hackernews/topstories/?pagenumber=N endpoint
    with pagenumber is a negative number
    """
    insert_in_table(
        insert_data=test_row,
        db_address=os.environ.get('TEST_HACKER_NEWS_DATABASE_URI'),
        table_name="hacker_news_top_story"
    )
    response = client.get("/api/hackernews/topstories/?pagenumber=-1",)
    response = json.loads(response.data)
    assert (
        {
            "code": 400,
            "message": "pagenumber must be greater then 0"
        }
    ) == response


def test_hn_top_stories_get_pagenumber_is_big_number(client):
    """
    test /api/hackernews/topstories/?pagenumber=N endpoint
    with pagenumber is a big number, more then pages
    """
    insert_in_table(
        insert_data=test_row,
        db_address=os.environ.get('TEST_HACKER_NEWS_DATABASE_URI'),
        table_name="hacker_news_top_story"
    )
    response = client.get("/api/hackernews/topstories/?pagenumber=100",)
    response = json.loads(response.data)
    assert (
        {
            "code": 404,
            "message": "Pagination page not found"
        }
    ) == response


def test_hn_top_stories_no_story_id_data(client):
    """
    test /api/hackernews/topstories/<story_id> endpoint
    with no <story_id> data
    """
    insert_in_table(
        insert_data=test_row,
        db_address=os.environ.get('TEST_HACKER_NEWS_DATABASE_URI'),
        table_name="hacker_news_top_story"
    )
    response = client.get("/api/hackernews/topstories/",)
    response = json.loads(response.data)
    assert {"pagenumber": ["Field may not be null."]} == response


def test_hn_top_stories_story_id_not_iteger(client):
    """
    test /api/hackernews/topstories/<story_id> endpoint
    with <story_id> not iteger
    """
    insert_in_table(
        insert_data=test_row,
        db_address=os.environ.get('TEST_HACKER_NEWS_DATABASE_URI'),
        table_name="hacker_news_top_story"
    )
    response = client.get("/api/hackernews/topstories/aaabbbccc",)
    error_response = (
        b'<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">\n'
        b'<title>404 Not Found</title>\n'
        b'<h1>Not Found</h1>\n'
        b'<p>The requested URL was not found on the server. '
        b'If you entered the URL manually please check your '
        b'spelling and try again.</p>\n'
    )
    assert error_response == response.data


def test_hn_top_stories_story_id_not_valid(client):
    """
    test /api/hackernews/topstories/<story_id> endpoint
    with <story_id> not present in database
    """
    insert_in_table(
        insert_data=test_row,
        db_address=os.environ.get('TEST_HACKER_NEWS_DATABASE_URI'),
        table_name="hacker_news_top_story"
    )
    response = client.get("/api/hackernews/topstories/11124611558",)
    response = json.loads(response.data)
    assert (
        {
            "code": 404,
            "message": "Story not found"
        }
    ) == response


def test_hn_top_stories_story_id_valid(client):
    """
    test /api/hackernews/topstories/<story_id> endpoint
    with valid <story_id>
    """
    insert_in_table(
        insert_data=test_row,
        db_address=os.environ.get('TEST_HACKER_NEWS_DATABASE_URI'),
        table_name="hacker_news_top_story"
    )
    response = client.get(f"/api/hackernews/topstories/{test_row['hn_id']}",)
    response = json.loads(response.data)
    assert test_row['hn_id'] == response["hn_id"]
