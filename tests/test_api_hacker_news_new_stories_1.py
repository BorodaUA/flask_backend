# import os
# import sys
# import pytest
# import flask
# import json
# from uuid import uuid4

# topdir = os.path.join(os.path.dirname(__file__), "..")
# sys.path.append(topdir)

# from flask_backend import create_app, db
# from api.models import hn_db
# from sqlalchemy.orm import scoped_session, sessionmaker

# from sqlalchemy.ext.automap import automap_base
# from sqlalchemy import create_engine


# @pytest.fixture()
# def client():
#     app = create_app("testing")
#     with app.test_client() as client:
#         db.init_app(app)

#         with app.app_context():
#             hn_db.Base.session = scoped_session(
#                 sessionmaker(
#                     autocommit=False,
#                     autoflush=False,
#                     bind=db.get_engine(bind="hacker_news"),
#                 )
#             )
#             hn_db.Base.query = hn_db.Base.session.query_property()
#             hn_db.Base.metadata.drop_all(db.get_engine(bind="hacker_news"))
#             hn_db.Base.metadata.create_all(db.get_engine(bind="hacker_news"))

#         yield client

#         @app.teardown_appcontext
#         def shutdown_session_and_delete_table(exception=None):
#             hn_db.Base.session.remove()
#             hn_db.Base.metadata.drop_all(db.get_engine(bind="hacker_news"))


# test_row = {
#     "hn_url": "https://news.ycombinator.com/item?id=23345788",
#     "item_id": 23345788,
#     "deleted": None,
#     "item_type": "story",
#     "by": "zanter",
#     "time": 1590720430,
#     "text": None,
#     "dead": None,
#     "parent": None,
#     "poll": None,
#     "kids": None,
#     "url": "https://pandayoo.com/mutual-blocking-list-of-chinese-internet-companies-commercial-competition",
#     "score": 5,
#     "title": "Mutual blocking list of Chinese Internet companies (commercial competition)",
#     "parts": None,
#     "descendants": 0,
#     "parse_dt": "2020-05-30 22:19:53.811",
# }
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


# def insert_in_table(row, table_name):
#     db_address = (
#         "postgresql+psycopg2://postgres:qazwsx99@localhost:5432/test_hacker_news"
#     )
#     Base = automap_base()
#     engine = create_engine(db_address)
#     ###
#     Base.prepare(engine, reflect=True)
#     table = Base.classes[table_name]
#     Session = sessionmaker(bind=engine)
#     session = Session()
#     data = table(**row)
#     session.add(data)
#     session.commit()
#     session.close()


# def test_api_home_page(client):
#     """
#     test /api/
#     """
#     response = client.get("/api/")
#     response = json.loads(response.data)
#     assert "Api Home page" == response["message"]


# def test_no_json_data_and_content_type_pagination_hacker_news_new_stories(client):
#     """
#     test pagination 1
#     """
#     insert_in_table(test_row, "hacker_news_new_stories")
#     response = client.post("/api/hacker_news/new_stories/1",)
#     response = json.loads(response.data)
#     assert {"_schema": ["Invalid input type."]} == response


# def test_no_json_data_hacker_news_new_stories(client):
#     """
#     test pagination 2
#     """
#     response = client.post(
#         "/api/hacker_news/new_stories/1",
#         data=json.dumps({}),
#         content_type="application/json",
#     )
#     response = json.loads(response.data)
#     assert {"page_number": ["Missing data for required field."]} == response


# def test_empty_table_hacker_news_new_stories(client):
#     """
#     test pagination 3
#     """
#     response = client.post(
#         "/api/hacker_news/new_stories/1",
#         data=json.dumps({"page_number": 1}),
#         content_type="application/json",
#     )
#     response = json.loads(response.data)
#     assert "No new_stories in this table" == response["message"]


# def test_pagination_hacker_news_new_stories(client):
#     """
#     test pagination 4
#     """
#     insert_in_table(test_row, "hacker_news_new_stories")
#     response = client.post(
#         "/api/hacker_news/new_stories/1",
#         data=json.dumps({"page_number": 1}),
#         content_type="application/json",
#     )
#     response = json.loads(response.data)
#     assert "zanter" == response["items"][0]["by"]


# def test_no_data_story_page_hacker_news_new_stories(client):
#     """
#     test story 1
#     """
#     insert_in_table(test_row, "hacker_news_new_stories")
#     response = client.post(f"/api/hacker_news/new_stories/story/{test_row['item_id']}",)
#     response = json.loads(response.data)
#     assert {"_schema": ["Invalid input type."]} == response


# def test_no_story_id_story_page_hacker_news_new_stories(client):
#     """
#     test story 2
#     """
#     insert_in_table(test_row, "hacker_news_new_stories")
#     response = client.post(
#         f"/api/hacker_news/new_stories/story/{test_row['item_id']}",
#         data=json.dumps({}),
#         content_type="application/json",
#     )
#     response = json.loads(response.data)
#     assert {"story_id": ["Missing data for required field."]} == response


# def test_story_page_hacker_news_new_stories(client):
#     """
#     test story 3
#     """
#     insert_in_table(test_row, "hacker_news_new_stories")
#     response = client.post(
#         f"/api/hacker_news/new_stories/story/{test_row['item_id']}",
#         data=json.dumps({"story_id": test_row["item_id"]}),
#         content_type="application/json",
#     )
#     response = json.loads(response.data)
#     assert "zanter" == response["by"]
