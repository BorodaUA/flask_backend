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


test_row = {
    "by": "pseudolus",
    "dead": None,
    "deleted": None,
    "descendants": 328,
    "id": "1",
    "kids": [
        24611767,
    ],
    "origin": "hacker_news",
    "parent": None,
    # "parsed_time": "2020-09-28T08:20:23.918000",
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


def test_api_home_page(client):
    """
    Test /api/ endpont
    """
    response = client.get("/api/")
    response = json.loads(response.data)
    assert "Api Home page" == response["message"]


def test_blognews_get_no_pagenumber(client):
    """
    test GET /api/blognews/?pagenumber=N endpoint
    with no pagenumber data
    """
    insert_in_table(
        insert_data=test_row,
        db_address=os.environ.get('TEST_FLASK_BACKEND_DATABASE_URI'),
        table_name="blog_news_story"
    )
    response = client.get("/api/blognews/",)
    response = json.loads(response.data)
    assert {"pagenumber": ["Field may not be null."]} == response


def test_blognews_get_pagenumber_not_integer(client):
    """
    test GET /api/blognews/?pagenumber=N endpoint
    with pagenumber not an integer
    """
    insert_in_table(
        insert_data=test_row,
        db_address=os.environ.get('TEST_FLASK_BACKEND_DATABASE_URI'),
        table_name="blog_news_story"
    )
    response = client.get("/api/blognews/?pagenumber=A",)
    response = json.loads(response.data)
    assert {"pagenumber": ["Not a valid integer."]} == response


def test_blognews_get_pagenumber_is_zero(client):
    """
    test GET /api/blognews/?pagenumber=N endpoint
    with pagenumber equal to 0
    """
    insert_in_table(
        insert_data=test_row,
        db_address=os.environ.get('TEST_FLASK_BACKEND_DATABASE_URI'),
        table_name="blog_news_story"
    )
    response = client.get("/api/blognews/?pagenumber=0",)
    response = json.loads(response.data)
    assert (
        {
            "code": 400,
            "message": "pagenumber must be greater then 0"
        }
    ) == response


def test_blognews_get_pagenumber_is_negative_number(client):
    """
    test GET /api/blognews/?pagenumber=N endpoint
    with pagenumber is a negative number
    """
    insert_in_table(
        insert_data=test_row,
        db_address=os.environ.get('TEST_FLASK_BACKEND_DATABASE_URI'),
        table_name="blog_news_story"
    )
    response = client.get("/api/blognews/?pagenumber=-1",)
    response = json.loads(response.data)
    assert (
        {
            "code": 400,
            "message": "pagenumber must be greater then 0"
        }
    ) == response


def test_blognews_get_pagenumber_is_big_number(client):
    """
    test GET /api/blognews/?pagenumber=N endpoint
    with pagenumber is a big number, more then pages
    """
    insert_in_table(
        insert_data=test_row,
        db_address=os.environ.get('TEST_FLASK_BACKEND_DATABASE_URI'),
        table_name="blog_news_story"
    )
    response = client.get("/api/blognews/?pagenumber=100",)
    response = json.loads(response.data)
    assert (
        {
            "code": 404,
            "message": "Pagination page not found"
        }
    ) == response


def test_blognews_get_pagenumber_valid_1(client):
    """
    test GET /api/blognews/?pagenumber=N endpoint
    with pagenumber valid number 1
    """
    insert_in_table(
        insert_data=test_row,
        db_address=os.environ.get('TEST_FLASK_BACKEND_DATABASE_URI'),
        table_name="blog_news_story"
    )
    response = client.get("/api/blognews/?pagenumber=1",)
    response = json.loads(response.data)
    assert "pseudolus" == response['items'][0]['by']


def test_blognews_post_no_json_data(client):
    """
    test POST /api/blognews/ endpoint
    with no json data
    """
    response = client.post(
        "/api/blognews/",
        # data=json.dumps(
        #     {
        #         # 'by': 'test_bob_2',
        #         # 'text': 'delete tests text'
        #     }
        # ),
        # content_type="application/json",
    )
    response = json.loads(response.data)
    assert (
        {
            '_schema': ['Invalid input type.'],

        }
    ) == response


def test_blognews_post_no_required_fields(client):
    """
    test POST /api/blognews/ endpoint
    with no required fields
    """
    response = client.post(
        "/api/blognews/",
        data=json.dumps({}),
        content_type="application/json",
    )
    response = json.loads(response.data)
    assert (
        {
            'url': ['Missing data for required field.'],
            'by': ['Missing data for required field.'],
            'text': ['Missing data for required field.'],
            'title': ['Missing data for required field.'],
        }
    ) == response


def test_blognews_post_empty_required_fields(client):
    """
    test POST /api/blognews/ endpoint
    with empty required fields
    """
    response = client.post(
        "/api/blognews/",
        data=json.dumps(
            {
                'url': '',
                'by': '',
                'text': '',
                'title': '',
            }
        ),
        content_type="application/json",
    )
    response = json.loads(response.data)
    assert (
        {
            'url': ['Shorter than minimum length 1.'],
            'by': ['Shorter than minimum length 2.'],
            'text': ['Shorter than minimum length 1.'],
            'title': ['Shorter than minimum length 1.'],
        }
    ) == response


def test_blognews_post_valid_required_fields(client):
    """
    test POST /api/blognews/ endpoint
    with valid required fields
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


def test_blognews_post_invalid_required_fields_types(client):
    """
    test POST /api/blognews/ endpoint
    with invalid required fields types
    """
    response = client.post(
        "/api/blognews/",
        data=json.dumps(
            {
                'url': [111],
                'by': 222,
                'text': {'text from test': 333},
                'title': 4.4,
            }
        ),
        content_type="application/json",
    )
    response = json.loads(response.data)
    assert (
        {
            'url': ['Not a valid string.'],
            'by': ['Not a valid string.'],
            'text': ['Not a valid string.'],
            'title': ['Not a valid string.'],
        }
    ) == response


def test_blognews_post_extra_field(client):
    """
    test POST /api/blognews/ endpoint
    with extra field in the request
    """
    response = client.post(
        "/api/blognews/",
        data=json.dumps(
            {
                'url': 'https://www.google.com/',
                'by': 'test_bob_2',
                'text': 'text from test',
                'title': 'title from test',
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
