from flask import request, jsonify, make_response, jsonify
from flask_restful import Resource
from api.models.hn_db import (
    HackerNews_TopStories,
    HackerNews_TopStories_Comments,
    HackerNews_NewStories,
    HackerNews_NewStories_Comments,
)
from api.schemas.hacker_news import (
    HackerNews_TopStories_Schema,
    HackerNews_NewStories_Schema,
    NewsPagination_Schema,
    Story_id_Schema,
    Comments_Schema,
    Add_Comment_Schema,
)
from sqlalchemy import desc
from sqlalchemy_pagination import paginate
from marshmallow import ValidationError

from api.models import hn_db


top_stories_schema = HackerNews_TopStories_Schema(
    many=True,
    exclude=[
        "id",
        "comments",
        "parse_dt",
        "deleted",
        "item_type",
        "time",
        "dead",
        "parent",
        "poll",
        "kids",
        "parts",
        "descendants",
    ],
)
top_story_schema = HackerNews_TopStories_Schema(
    exclude=[
        "id",
        "parse_dt",
        "deleted",
        "item_type",
        "time",
        "dead",
        "parent",
        "poll",
        "kids",
        "parts",
        "descendants",
    ],
)
#
new_stories_schema = HackerNews_NewStories_Schema(
    many=True,
    exclude=[
        "id",
        "comments",
        "parse_dt",
        "deleted",
        "item_type",
        "time",
        "dead",
        "parent",
        "poll",
        "kids",
        "parts",
        "descendants",
    ],
)
#
new_story_schema = HackerNews_NewStories_Schema(
    exclude=[
        "id",
        "parse_dt",
        "deleted",
        "item_type",
        "time",
        "dead",
        "parent",
        "poll",
        "kids",
        "parts",
        "descendants",
    ],
)
#
news_pagination = NewsPagination_Schema()
story_id_schema = Story_id_Schema()
comments_schema = Comments_Schema(many=True)
add_coment_schema = Add_Comment_Schema()


class HackerNews_TopStories_Resourse(Resource):
    @classmethod
    def post(cls, page_number):
        """
        Getting POST requests on the '/api/hacker_news/top_stories/<page_number>' 
        endpoint, and returning a page with 30 hacker_news top_stories in database.
        """
        try:
            incoming_pagination = news_pagination.load(request.get_json())
        except ValidationError as err:
            return err.messages, 400
        if incoming_pagination["page_number"] <= 0:
            return {"message": "pagination must be >= 1"}, 400
        if not HackerNews_TopStories.query.all():
            return {"message": "No top_stories in this table"}, 400
        page = paginate(
            HackerNews_TopStories.query.order_by(desc(HackerNews_TopStories.parse_dt))
            .limit(500)
            .from_self(),
            incoming_pagination["page_number"],
            30,
        )
        result_page = {
            "current_page": incoming_pagination["page_number"],
            "has_next": page.has_next,
            "has_previous": page.has_previous,
            "items": top_stories_schema.dump(page.items),
            "next_page": page.next_page,
            "previous_page": page.previous_page,
            "pages": page.pages,
            "total": page.total,
        }
        if incoming_pagination["page_number"] > result_page["pages"]:
            return {"message": "Pagination page not found"}, 400
        return jsonify(result_page)


class HackerNews_TopStories_Story_Resource(Resource):
    @classmethod
    def post(cls, story_id):
        """
        Getting POST requests on the '/api/hacker_news/top_stories/story/<story_id>' 
        endpoint, and returning a hacker_news top_stories`s story with comments
        """
        try:
            incoming_story_id = story_id_schema.load(request.get_json())
        except ValidationError as err:
            return err.messages, 400
        if not HackerNews_TopStories.query.filter(
            HackerNews_TopStories.item_id == incoming_story_id["story_id"]
        ).first():
            return {"message": "Story not found"}, 400
        story = (
            HackerNews_TopStories.query.filter(
                HackerNews_TopStories.item_id == incoming_story_id["story_id"],
            )
            .order_by(HackerNews_TopStories.parse_dt)
            .first()
        )

        return jsonify(top_story_schema.dump(story))


class HackerNews_TopStories_Story_Comments_Resource(Resource):
    @classmethod
    def get(cls, story_id):
        """
        Getting GET requests on the '/api/hacker_news/top_stories/story/<story_id>/comments' 
        endpoint, and returning a list of hacker_news top_stories`s story`s comments
        """
        try:
            incoming_story_id = story_id_schema.load(request.get_json())
        except ValidationError as err:
            return err.messages, 400
        if not HackerNews_TopStories.query.filter(
            HackerNews_TopStories.item_id == incoming_story_id["story_id"]
        ).first():
            return {"message": "Comments not found"}, 400
        comments = (
            HackerNews_TopStories_Comments.query.filter(
                HackerNews_TopStories_Comments.parent == incoming_story_id["story_id"]
            )
            .order_by(desc(HackerNews_TopStories_Comments.parse_dt))
            .all()
        )
        return jsonify(comments_schema.dump(comments))

    def post(cls, story_id):
        """
        Getting POST requests on the '/api/hacker_news/top_stories/story/<story_id>/comments' 
        endpoint, and adding hacker_news top_stories`s story`s comment
        """
        try:
            incoming_comment = add_coment_schema.load(request.get_json())
        except ValidationError as err:
            return err.messages, 400
        incoming_comment.pop("existed_comment_id")
        incoming_comment.pop("existed_comment_text")
        comment_data = HackerNews_TopStories_Comments(**incoming_comment)
        hn_db.Base.session.add(comment_data)
        hn_db.Base.session.commit()
        return make_response(jsonify({"message": "Comment added",}), 201,)

    def put(cls, story_id):
        """
        Getting PUT requests on the '/api/hacker_news/top_stories/story/<story_id>/comments' 
        endpoint, and updating hacker_news top_stories`s story`s comment
        """
        try:
            incoming_comment = add_coment_schema.load(request.get_json())
        except ValidationError as err:
            return err.messages, 400
        if HackerNews_TopStories_Comments.query.filter(
            HackerNews_TopStories_Comments.comment_id
            == incoming_comment["existed_comment_id"]
        ).first():
            HackerNews_TopStories_Comments.query.filter(
                HackerNews_TopStories_Comments.comment_id
                == incoming_comment["existed_comment_id"]
            ).update(
                {
                    "parse_dt": incoming_comment["parse_dt"],
                    "by": incoming_comment["by"],
                    "deleted": incoming_comment["deleted"],
                    "comment_id": int(incoming_comment["existed_comment_id"]),
                    "kids": incoming_comment["kids"],
                    "parent": incoming_comment["parent"],
                    "text": incoming_comment["text"],
                    "time": incoming_comment["time"],
                    "comment_type": incoming_comment["comment_type"],
                }
            )
            hn_db.Base.session.commit()
            return make_response(jsonify({"message": "Comment updated",}), 201,)
        else:
            return make_response(jsonify({"message": "Comment not found",}), 400,)

    def delete(cls, story_id):
        """
        Getting DELETE requests on the '/api/hacker_news/top_stories/story/<story_id>/comments' 
        endpoint, and deleting hacker_news top_stories`s story`s comment
        """
        try:
            incoming_comment = add_coment_schema.load(request.get_json())
        except ValidationError as err:
            return err.messages, 400
        if HackerNews_TopStories_Comments.query.filter(
            HackerNews_TopStories_Comments.comment_id
            == incoming_comment["existed_comment_id"]
        ).first():
            HackerNews_TopStories_Comments.query.filter(
                HackerNews_TopStories_Comments.comment_id
                == incoming_comment["existed_comment_id"]
            ).delete()
            hn_db.Base.session.commit()
            return make_response(jsonify({"message": "Comment deleted",}), 201,)
        else:
            return make_response(jsonify({"message": "Comment not found",}), 400,)


class HackerNews_NewStories_Resourse(Resource):
    @classmethod
    def post(cls, page_number):
        """
        Getting POST requests on the '/api/hacker_news/new_stories/<page_number>' 
        endpoint, and returning a page with 30 hacker_news new_stories in database.
        """
        try:
            incoming_pagination = news_pagination.load(request.get_json())
        except ValidationError as err:
            return err.messages, 400

        if not HackerNews_NewStories.query.all():
            return {"message": "No new_stories in this table"}, 400
        if incoming_pagination["page_number"] <= 0:
            return {"message": "pagination must be >= 1"}, 400
        page = paginate(
            HackerNews_NewStories.query.order_by(desc(HackerNews_NewStories.parse_dt))
            .limit(500)
            .from_self(),
            incoming_pagination["page_number"],
            30,
        )
        result_page = {
            "current_page": incoming_pagination["page_number"],
            "has_next": page.has_next,
            "has_previous": page.has_previous,
            "items": new_stories_schema.dump(page.items),
            "next_page": page.next_page,
            "previous_page": page.previous_page,
            "pages": page.pages,
            "total": page.total,
        }
        if incoming_pagination["page_number"] > result_page["pages"]:
            return {"message": "Pagination page not found"}, 400
        return jsonify(result_page)


class HackerNews_NewStories_Story_Resource(Resource):
    @classmethod
    def post(cls, story_id):
        """
        Getting POST requests on the '/api/hacker_news/new_stories/story/<story_id>' 
        endpoint, and returning a hacker_news new_stories`s story with comments
        """
        try:
            incoming_story_id = story_id_schema.load(request.get_json())
        except ValidationError as err:
            return err.messages, 400
        if not HackerNews_NewStories.query.filter(
            HackerNews_NewStories.item_id == incoming_story_id["story_id"]
        ).first():
            return {"message": "Story not found"}, 400
        story = (
            HackerNews_NewStories.query.filter(
                HackerNews_NewStories.item_id == incoming_story_id["story_id"],
            )
            .order_by(HackerNews_NewStories.parse_dt)
            .first()
        )

        return jsonify(new_story_schema.dump(story))
