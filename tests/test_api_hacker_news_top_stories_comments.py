import os
import sys
import pytest
import flask
import json
from uuid import uuid4

topdir = os.path.join(os.path.dirname(__file__), "..")
sys.path.append(topdir)

from flask_back_1 import create_app, db
from api.models import hn_db
from sqlalchemy.orm import scoped_session, sessionmaker

from sqlalchemy.ext.automap import automap_base
from sqlalchemy import create_engine


@pytest.fixture()
def client():
    app = create_app("testing")
    with app.test_client() as client:
        db.init_app(app)

        with app.app_context():
            hn_db.Base.session = scoped_session(
                sessionmaker(
                    autocommit=False,
                    autoflush=False,
                    bind=db.get_engine(bind="hacker_news"),
                )
            )
            hn_db.Base.query = hn_db.Base.session.query_property()
            hn_db.Base.metadata.drop_all(db.get_engine(bind="hacker_news"))
            hn_db.Base.metadata.create_all(db.get_engine(bind="hacker_news"))

        yield client

        @app.teardown_appcontext
        def shutdown_session_and_delete_table(exception=None):
            hn_db.Base.session.remove()
            hn_db.Base.metadata.drop_all(db.get_engine(bind="hacker_news"))


test_row = {
    "hn_url": "https://news.ycombinator.com/item?id=23345788",
    "item_id": 23345788,
    "deleted": None,
    "item_type": "story",
    "by": "zanter",
    "time": 1590720430,
    "text": None,
    "dead": None,
    "parent": None,
    "poll": None,
    "kids": None,
    "url": "https://pandayoo.com/mutual-blocking-list-of-chinese-internet-companies-commercial-competition",
    "score": 5,
    "title": "Mutual blocking list of Chinese Internet companies (commercial competition)",
    "parts": None,
    "descendants": 0,
    "parse_dt": "2020-05-30 22:19:53.811",
}
# test_comment_row = {
#     "by": "dmayle",
#     "comment_id": 23349721,
#     "comment_type": "comment",
#     "deleted": None,
#     "id": 27,
#     "kids": [23350128, 23349816, 23350299],
#     "parent": 23345788,
#     "parse_dt": "2020-05-29T17:42:45.354050",
#     "text": "I use Airflow, and am a big fan.  I don&#x27;t think it&#x27;s particularly clear, however, as to <i>when</i> to use airflow.<p>The single best reason to use airflow is that you have some data source with a time-based axis that you want to transfer or process.  For example, you might want to ingest daily web logs into a database.  Or maybe you want weekly statistics generated on your database, etc.<p>The next best reason to use airflow is that you have a recurring job that you want not only to happen, but to track it&#x27;s successes and failures.  For example, maybe you want to garbage-collect some files on a remote server with spotty connectivity, and you want to be emailed if it fails for more than two days in a row.<p>Beyond those two, Airflow might be very useful, but you&#x27;ll be shoehorning your use case into Airflow&#x27;s capabilities.<p>Airflow is basically a distributed cron daemon with support for reruns and SLAs.  If you&#x27;re using Python for your tasks, it also includes a large collection of data abstraction layers such that Airflow can manage the named connections to the different sources, and you only have to code the transfer or transform rules.",
#     "time": 1590758861,
# }


def insert_in_table(row, table_name):
    db_address = (
        "postgresql+psycopg2://postgres:qazwsx99@localhost:5432/test_hacker_news"
    )
    Base = automap_base()
    engine = create_engine(db_address)
    ###
    Base.prepare(engine, reflect=True)
    table = Base.classes[table_name]
    Session = sessionmaker(bind=engine)
    session = Session()
    data = table(**row)
    session.add(data)
    session.commit()
    session.close()


def test_hacker_news_top_stories_add_comment(client):
    """
    test add story's comment
    """
    insert_in_table(test_row, "hacker_news_top_stories")
    add_comment = client.post(
        f"/api/hacker_news/top_stories/story/{test_row['item_id']}/comments",
        content_type="application/json",
        data=json.dumps(
            {
                "parse_dt": "2020-06-12 12:05:22.637",
                "by": "test_user",
                "deleted": False,
                "existed_comment_id": 0,
                "existed_comment_text": "",
                "comment_id": "11111",
                "kids": [],
                "parent": test_row["item_id"],
                "text": "flask test comment v1",
                "time": 12112412,
                "comment_type": "comment",
            }
        ),
    )
    response = client.get(
        f"/api/hacker_news/top_stories/story/{test_row['item_id']}/comments",
        data=json.dumps({"story_id": test_row["item_id"]}),
        content_type="application/json",
    )
    response = json.loads(response.data)
    assert "flask test comment v1" == response[0]["text"]


def test_hacker_news_top_stories_add_comment_parse_dt_wrong_type(client):
    """
    test parse_dt not a datetime
    """
    insert_in_table(test_row, "hacker_news_top_stories")
    add_comment = client.post(
        f"/api/hacker_news/top_stories/story/{test_row['item_id']}/comments",
        content_type="application/json",
        data=json.dumps(
            {
                "parse_dt": [1111111111111111111111111111111111111111],
                "by": "test_user",
                "deleted": False,
                "existed_comment_id": 0,
                "existed_comment_text": "",
                "comment_id": "11111",
                "kids": [],
                "parent": test_row["item_id"],
                "text": "flask test comment v1",
                "time": 12112412,
                "comment_type": "comment",
            }
        ),
    )
    response = json.loads(add_comment.data)
    assert ["Not a valid datetime."] == response["parse_dt"]


def test_hacker_news_top_stories_add_comment_by_wrong_type(client):
    """
    test by not a str
    """
    insert_in_table(test_row, "hacker_news_top_stories")
    add_comment = client.post(
        f"/api/hacker_news/top_stories/story/{test_row['item_id']}/comments",
        content_type="application/json",
        data=json.dumps(
            {
                "parse_dt": "2020-06-12 12:05:22.637",
                "by": ["test_user"],
                "deleted": False,
                "existed_comment_id": 0,
                "existed_comment_text": "",
                "comment_id": "11111",
                "kids": [],
                "parent": test_row["item_id"],
                "text": "flask test comment v1",
                "time": 12112412,
                "comment_type": "comment",
            }
        ),
    )
    response = json.loads(add_comment.data)
    assert ["Not a valid string."] == response["by"]


def test_hacker_news_top_stories_add_comment_deleted_wrong_type(client):
    """
    test deleted not a Bool
    """
    insert_in_table(test_row, "hacker_news_top_stories")
    add_comment = client.post(
        f"/api/hacker_news/top_stories/story/{test_row['item_id']}/comments",
        content_type="application/json",
        data=json.dumps(
            {
                "parse_dt": "2020-06-12 12:05:22.637",
                "by": "test_user",
                "deleted": 11111,
                "existed_comment_id": 0,
                "existed_comment_text": "",
                "comment_id": "11111",
                "kids": [],
                "parent": test_row["item_id"],
                "text": "flask test comment v1",
                "time": 12112412,
                "comment_type": "comment",
            }
        ),
    )
    response = json.loads(add_comment.data)
    assert ["Not a valid boolean."] == response["deleted"]


def test_hacker_news_top_stories_add_comment_existed_comment_id_wrong_type(client):
    """
    test existed_comment_id not a int
    """
    insert_in_table(test_row, "hacker_news_top_stories")
    add_comment = client.post(
        f"/api/hacker_news/top_stories/story/{test_row['item_id']}/comments",
        content_type="application/json",
        data=json.dumps(
            {
                "parse_dt": "2020-06-12 12:05:22.637",
                "by": "test_user",
                "deleted": False,
                "existed_comment_id": {"wrong": "type"},
                "existed_comment_text": "",
                "comment_id": "11111",
                "kids": [],
                "parent": test_row["item_id"],
                "text": "flask test comment v1",
                "time": 12112412,
                "comment_type": "comment",
            }
        ),
    )
    response = json.loads(add_comment.data)
    assert ["Not a valid integer."] == response["existed_comment_id"]


def test_hacker_news_top_stories_add_comment_existed_comment_text_wrong_type(client):
    """
    test existed_comment_text not a str
    """
    insert_in_table(test_row, "hacker_news_top_stories")
    add_comment = client.post(
        f"/api/hacker_news/top_stories/story/{test_row['item_id']}/comments",
        content_type="application/json",
        data=json.dumps(
            {
                "parse_dt": "2020-06-12 12:05:22.637",
                "by": "test_user",
                "deleted": False,
                "existed_comment_id": 0,
                "existed_comment_text": False,
                "comment_id": "11111",
                "kids": [],
                "parent": test_row["item_id"],
                "text": "flask test comment v1",
                "time": 12112412,
                "comment_type": "comment",
            }
        ),
    )
    response = json.loads(add_comment.data)
    assert ["Not a valid string."] == response["existed_comment_text"]


def test_hacker_news_top_stories_add_comment_comment_id_wrong_type(client):
    """
    test comment_id not a int
    """
    insert_in_table(test_row, "hacker_news_top_stories")
    add_comment = client.post(
        f"/api/hacker_news/top_stories/story/{test_row['item_id']}/comments",
        content_type="application/json",
        data=json.dumps(
            {
                "parse_dt": "2020-06-12 12:05:22.637",
                "by": "test_user",
                "deleted": False,
                "existed_comment_id": 0,
                "existed_comment_text": "",
                "comment_id": {"11111": 1111},
                "kids": [],
                "parent": test_row["item_id"],
                "text": "flask test comment v1",
                "time": 12112412,
                "comment_type": "comment",
            }
        ),
    )
    response = json.loads(add_comment.data)
    assert ["Not a valid integer."] == response["comment_id"]


def test_hacker_news_top_stories_add_comment_kids_wrong_type(client):
    """
    test kids not a list
    """
    insert_in_table(test_row, "hacker_news_top_stories")
    add_comment = client.post(
        f"/api/hacker_news/top_stories/story/{test_row['item_id']}/comments",
        content_type="application/json",
        data=json.dumps(
            {
                "parse_dt": "2020-06-12 12:05:22.637",
                "by": "test_user",
                "deleted": False,
                "existed_comment_id": 0,
                "existed_comment_text": "",
                "comment_id": 11111,
                "kids": {"wrong_type": True},
                "parent": test_row["item_id"],
                "text": "flask test comment v1",
                "time": 12112412,
                "comment_type": "comment",
            }
        ),
    )
    response = json.loads(add_comment.data)
    assert ["Not a valid list."] == response["kids"]


def test_hacker_news_top_stories_add_comment_parent_wrong_type(client):
    """
    test parent not a int
    """
    insert_in_table(test_row, "hacker_news_top_stories")
    add_comment = client.post(
        f"/api/hacker_news/top_stories/story/{test_row['item_id']}/comments",
        content_type="application/json",
        data=json.dumps(
            {
                "parse_dt": "2020-06-12 12:05:22.637",
                "by": "test_user",
                "deleted": False,
                "existed_comment_id": 0,
                "existed_comment_text": "",
                "comment_id": 11111,
                "kids": [],
                "parent": {"wrong_type": True},
                "text": "flask test comment v1",
                "time": 12112412,
                "comment_type": "comment",
            }
        ),
    )
    response = json.loads(add_comment.data)
    assert ["Not a valid integer."] == response["parent"]


def test_hacker_news_top_stories_add_comment_text_wrong_type(client):
    """
    test text not a str
    """
    insert_in_table(test_row, "hacker_news_top_stories")
    add_comment = client.post(
        f"/api/hacker_news/top_stories/story/{test_row['item_id']}/comments",
        content_type="application/json",
        data=json.dumps(
            {
                "parse_dt": "2020-06-12 12:05:22.637",
                "by": "test_user",
                "deleted": False,
                "existed_comment_id": 0,
                "existed_comment_text": "",
                "comment_id": 11111,
                "kids": [],
                "parent": test_row["item_id"],
                "text": ["wrong", "type"],
                "time": 12112412,
                "comment_type": "comment",
            }
        ),
    )
    response = json.loads(add_comment.data)
    assert ["Not a valid string."] == response["text"]


def test_hacker_news_top_stories_add_comment_time_wrong_type(client):
    """
    test time not a int
    """
    insert_in_table(test_row, "hacker_news_top_stories")
    add_comment = client.post(
        f"/api/hacker_news/top_stories/story/{test_row['item_id']}/comments",
        content_type="application/json",
        data=json.dumps(
            {
                "parse_dt": "2020-06-12 12:05:22.637",
                "by": "test_user",
                "deleted": False,
                "existed_comment_id": 0,
                "existed_comment_text": "",
                "comment_id": 11111,
                "kids": [],
                "parent": test_row["item_id"],
                "text": "test comment text",
                "time": ["wrong", "type"],
                "comment_type": "comment",
            }
        ),
    )
    response = json.loads(add_comment.data)
    assert ["Not a valid integer."] == response["time"]


def test_hacker_news_top_stories_add_comment_comment_type_wrong_type(client):
    """
    test comment_type not a str
    """
    insert_in_table(test_row, "hacker_news_top_stories")
    add_comment = client.post(
        f"/api/hacker_news/top_stories/story/{test_row['item_id']}/comments",
        content_type="application/json",
        data=json.dumps(
            {
                "parse_dt": "2020-06-12 12:05:22.637",
                "by": "test_user",
                "deleted": False,
                "existed_comment_id": 0,
                "existed_comment_text": "",
                "comment_id": 11111,
                "kids": [],
                "parent": test_row["item_id"],
                "text": "test comment text",
                "time": 12345657,
                "comment_type": ["wrong", "type"],
            }
        ),
    )
    response = json.loads(add_comment.data)
    assert ["Not a valid string."] == response["comment_type"]


def test_hacker_news_top_stories_edit_comment(client):
    """
    test edit story's comment
    """
    insert_in_table(test_row, "hacker_news_top_stories")
    add_comment = client.post(
        f"/api/hacker_news/top_stories/story/{test_row['item_id']}/comments",
        content_type="application/json",
        data=json.dumps(
            {
                "parse_dt": "2020-06-12 12:05:22.637",
                "by": "test_user",
                "deleted": False,
                "existed_comment_id": 0,
                "existed_comment_text": "",
                "comment_id": "11111",
                "kids": [],
                "parent": test_row["item_id"],
                "text": "flask test comment v1",
                "time": 12112412,
                "comment_type": "comment",
            }
        ),
    )
    edit_comment = client.put(
        f"/api/hacker_news/top_stories/story/{test_row['item_id']}/comments",
        content_type="application/json",
        data=json.dumps(
            {
                "parse_dt": "2020-06-12 12:05:22.637",
                "by": "test_user",
                "deleted": False,
                "existed_comment_id": 11111,
                "existed_comment_text": "",
                "comment_id": "11111",
                "kids": [],
                "parent": test_row["item_id"],
                "text": "edited flask test comment v1",
                "time": 12112412,
                "comment_type": "comment",
            }
        ),
    )
    response = client.get(
        f"/api/hacker_news/top_stories/story/{test_row['item_id']}/comments",
        data=json.dumps({"story_id": test_row["item_id"]}),
        content_type="application/json",
    )
    response = json.loads(response.data)
    assert "edited flask test comment v1" == response[0]["text"]


def test_hacker_news_top_stories_edit_comment_wrong_existed_comment_id(client):
    """
    test edit story's comment wrong existed_comment_id
    """
    insert_in_table(test_row, "hacker_news_top_stories")
    add_comment = client.post(
        f"/api/hacker_news/top_stories/story/{test_row['item_id']}/comments",
        content_type="application/json",
        data=json.dumps(
            {
                "parse_dt": "2020-06-12 12:05:22.637",
                "by": "test_user",
                "deleted": False,
                "existed_comment_id": 0,
                "existed_comment_text": "",
                "comment_id": "11111",
                "kids": [],
                "parent": test_row["item_id"],
                "text": "flask test comment v1",
                "time": 12112412,
                "comment_type": "comment",
            }
        ),
    )
    edit_comment = client.put(
        f"/api/hacker_news/top_stories/story/{test_row['item_id']}/comments",
        content_type="application/json",
        data=json.dumps(
            {
                "parse_dt": "2020-06-12 12:05:22.637",
                "by": "test_user",
                "deleted": False,
                "existed_comment_id": 22222,
                "existed_comment_text": "",
                "comment_id": "11111",
                "kids": [],
                "parent": test_row["item_id"],
                "text": "edited flask test comment v1",
                "time": 12112412,
                "comment_type": "comment",
            }
        ),
    )
    response = json.loads(edit_comment.data)
    assert "Comment not found" == response["message"]


def test_hacker_news_top_stories_delete_comment(client):
    """
    test delete story's comment wrong comment_id
    """
    insert_in_table(test_row, "hacker_news_top_stories")
    add_comment = client.post(
        f"/api/hacker_news/top_stories/story/{test_row['item_id']}/comments",
        content_type="application/json",
        data=json.dumps(
            {
                "parse_dt": "2020-06-12 12:05:22.637",
                "by": "test_user",
                "deleted": False,
                "existed_comment_id": 0,
                "existed_comment_text": "",
                "comment_id": "11111",
                "kids": [],
                "parent": test_row["item_id"],
                "text": "flask test comment v1",
                "time": 12112412,
                "comment_type": "comment",
            }
        ),
    )
    delete_comment = client.delete(
        f"/api/hacker_news/top_stories/story/{test_row['item_id']}/comments",
        content_type="application/json",
        data=json.dumps(
            {
                "parse_dt": "2020-06-12 12:05:22.637",
                "by": "test_user",
                "deleted": False,
                "existed_comment_id": 11111,
                "existed_comment_text": "",
                "comment_id": "11111",
                "kids": [],
                "parent": test_row["item_id"],
                "text": "edited flask test comment v1",
                "time": 12112412,
                "comment_type": "comment",
            }
        ),
    )
    response = json.loads(delete_comment.data)
    no_comment = client.get(
        f"/api/hacker_news/top_stories/story/{test_row['item_id']}/comments",
        data=json.dumps({"story_id": test_row["item_id"]}),
        content_type="application/json",
    )
    no_comment = json.loads(no_comment.data)
    assert "Comment deleted" == response["message"] and [] == no_comment


def test_hacker_news_top_stories_delete_comment_wrong_existed_comment_id(client):
    """
    test delete story's comment wrong existed_comment_id
    """
    insert_in_table(test_row, "hacker_news_top_stories")
    add_comment = client.post(
        f"/api/hacker_news/top_stories/story/{test_row['item_id']}/comments",
        content_type="application/json",
        data=json.dumps(
            {
                "parse_dt": "2020-06-12 12:05:22.637",
                "by": "test_user",
                "deleted": False,
                "existed_comment_id": 0,
                "existed_comment_text": "",
                "comment_id": "11111",
                "kids": [],
                "parent": test_row["item_id"],
                "text": "flask test comment v1",
                "time": 12112412,
                "comment_type": "comment",
            }
        ),
    )
    delete_comment = client.delete(
        f"/api/hacker_news/top_stories/story/{test_row['item_id']}/comments",
        content_type="application/json",
        data=json.dumps(
            {
                "parse_dt": "2020-06-12 12:05:22.637",
                "by": "test_user",
                "deleted": False,
                "existed_comment_id": 22222,
                "existed_comment_text": "",
                "comment_id": "11111",
                "kids": [],
                "parent": test_row["item_id"],
                "text": "edited flask test comment v1",
                "time": 12112412,
                "comment_type": "comment",
            }
        ),
    )
    response = json.loads(delete_comment.data)
    assert "Comment not found" == response["message"]
