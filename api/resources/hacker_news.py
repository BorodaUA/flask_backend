from flask import request, jsonify, make_response, jsonify
from flask_restful import Resource
from api.models.hacker_news import (
    HackerNewsTopStory,
    HackerNewsTopStoryComment,
    HackerNewsNewStory,
    HackerNewsNewStoryComment,
)
from api.schemas.hacker_news import (
    HackerNewsTopStorySchema,
    HackerNews_NewStories_Schema,
    PaginationSchema,
    StorySchema,
    HackerNewsCommentSchema,
    Add_Comment_Schema,
)
from sqlalchemy import desc
from sqlalchemy_pagination import paginate
from marshmallow import ValidationError

from api.models import hacker_news


top_stories_schema = HackerNewsTopStorySchema(
    many=True,
    # exclude=[
    #     "id",
    #     "comments",
    #     "parsed_time",
    #     "deleted",
    #     "type",
    #     "time",
    #     "dead",
    #     "parent",
    #     "poll",
    #     "kids",
    #     "parts",
    #     "descendants",
    # ],
)
top_story_schema = HackerNewsTopStorySchema(
    # exclude=[
    #     "id",
    #     "parsed_time",
    #     "deleted",
    #     "type",
    #     "time",
    #     "dead",
    #     "parent",
    #     "poll",
    #     "kids",
    #     "parts",
    #     "descendants",
    # ],
)
#
new_stories_schema = HackerNews_NewStories_Schema(
    many=True,
    # exclude=[
    #     "id",
    #     "comments",
    #     "parse_dt",
    #     "deleted",
    #     "item_type",
    #     "time",
    #     "dead",
    #     "parent",
    #     "poll",
    #     "kids",
    #     "parts",
    #     "descendants",
    # ],
)
#
new_story_schema = HackerNews_NewStories_Schema(
    # exclude=[
    #     "id",
    #     "parse_dt",
    #     "deleted",
    #     "item_type",
    #     "time",
    #     "dead",
    #     "parent",
    #     "poll",
    #     "kids",
    #     "parts",
    #     "descendants",
    # ],
)
#
news_pagination = PaginationSchema()
story_id_schema = StorySchema()
comments_schema = HackerNewsCommentSchema(many=True)
add_coment_schema = Add_Comment_Schema()


class HackerNewsTopStoriesResourse(Resource):
    @classmethod
    def get(cls):
        """
        Getting GET requests on the
        '/api/hackernews/topstories/?pagenumber=N'
        endpoint, and returning a page with 30 hacker_news
        top_stories from database.
        """
        try:
            pagenumber = {"pagenumber": request.args.get("pagenumber")}
            incoming_pagination = news_pagination.load(pagenumber)
        except ValidationError as err:
            return err.messages, 400
        if incoming_pagination["pagenumber"] <= 0:
            return make_response(
                jsonify(
                    {
                        "message": "pagenumber must be greater then 0",
                        "code": 400
                    }
                ),
                400,
            )
        if not HackerNewsTopStory.query.all():
            return make_response(
                jsonify(
                    {
                        "message": "No hackernews topstories found",
                        "code": 404
                    }
                ), 404,
            )
        page = paginate(
            HackerNewsTopStory.query.order_by(
                desc(HackerNewsTopStory.parsed_time)
            )
            .limit(500)
            .from_self(),
            incoming_pagination["pagenumber"],
            30,
        )
        result_page = {
            "current_page": incoming_pagination["pagenumber"],
            "has_next": page.has_next,
            "has_previous": page.has_previous,
            "items": top_stories_schema.dump(page.items),
            "next_page": page.next_page,
            "previous_page": page.previous_page,
            "pages": page.pages,
            "total": page.total,
        }
        if incoming_pagination["pagenumber"] > result_page["pages"]:
            return make_response(
                jsonify(
                    {
                        "message": "Pagination page not found",
                        "code": 404
                    }
                ), 404,
            )
        hacker_news.Base.session.commit()
        hacker_news.Base.session.close()
        return jsonify(result_page)


class HackerNews_TopStories_Story_Resource(Resource):
    @classmethod
    def get(cls, story_id):
        """
        Getting GET requests on the '/api/hacker_news/top_stories/story/<story_id>' 
        endpoint, and returning a hacker_news top_stories`s story with comments
        """
        try:
            incoming_story_id = story_id_schema.load(request.get_json())
        except ValidationError as err:
            return err.messages, 400
        if not HackerNewsTopStory.query.filter(
            HackerNewsTopStory.id == incoming_story_id["story_id"]
        ).first():
            return {"message": "Story not found"}, 400
        story = (
            HackerNewsTopStory.query.filter(
                HackerNewsTopStory.id == incoming_story_id["story_id"],
            )
            .order_by(HackerNewsTopStory.parsed_time)
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
        if not HackerNewsTopStory.query.filter(
            HackerNewsTopStory.id == incoming_story_id["story_id"]
        ).first():
            return {"message": "Comments not found"}, 400
        comments = (
            HackerNewsTopStoryComment.query.filter(
                HackerNewsTopStoryComment.parent == incoming_story_id["story_id"]
            )
            .order_by(desc(HackerNewsTopStoryComment.parsed_time))
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
        if not HackerNewsTopStory.query.filter(
            HackerNewsTopStory.id == incoming_comment["parent"]
        ).first():
            return make_response(jsonify({"message": "Story not found"}), 400)
        incoming_comment.pop("existed_comment_id")
        incoming_comment.pop("existed_comment_text")
        comment_data = HackerNewsTopStoryComment(**incoming_comment)
        hn_db.Base.session.add(comment_data)
        hn_db.Base.session.commit()
        return make_response(jsonify({"message": "Comment added"}), 201,)

    def put(cls, story_id):
        """
        Getting PUT requests on the '/api/hacker_news/top_stories/story/<story_id>/comments' 
        endpoint, and updating hacker_news top_stories`s story`s comment
        """
        try:
            incoming_comment = add_coment_schema.load(request.get_json())
        except ValidationError as err:
            return err.messages, 400
        if not HackerNewsTopStory.query.filter(
            HackerNewsTopStory.id == incoming_comment["parent"]
        ).first():
            return make_response(jsonify({"message": "Story not found"}), 400)
        if HackerNewsTopStoryComment.query.filter(
            HackerNewsTopStoryComment.id
            == incoming_comment["existed_comment_id"]
        ).first():
            HackerNewsTopStoryComment.query.filter(
                HackerNewsTopStoryComment.id
                == incoming_comment["existed_comment_id"]
            ).update(
                {
                    "parsed_time": incoming_comment["parsed_time"],
                    "by": incoming_comment["by"],
                    "deleted": incoming_comment["deleted"],
                    "id": int(incoming_comment["existed_comment_id"]),
                    "kids": incoming_comment["kids"],
                    "parent": incoming_comment["parent"],
                    "text": incoming_comment["text"],
                    "time": incoming_comment["time"],
                    "type": incoming_comment["type"],
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
        if not HackerNewsTopStory.query.filter(
            HackerNewsTopStory.id == incoming_comment["parent"]
        ).first():
            return make_response(jsonify({"message": "Story not found"}), 400)
        if HackerNewsTopStoryComment.query.filter(
            HackerNewsTopStoryComment.id
            == incoming_comment["existed_comment_id"]
        ).first():
            HackerNewsTopStoryComment.query.filter(
                HackerNewsTopStoryComment.id
                == incoming_comment["existed_comment_id"]
            ).delete()
            hn_db.Base.session.commit()
            return make_response(jsonify({"message": "Comment deleted",}), 201,)
        else:
            return make_response(jsonify({"message": "Comment not found",}), 400,)


class HackerNews_NewStories_Resource(Resource):
    @classmethod
    def get(cls, page_number):
        """
        Getting GET requests on the '/api/hacker_news/new_stories/<page_number>' 
        endpoint, and returning a page with 30 hacker_news new_stories in database.
        """
        try:
            incoming_pagination = news_pagination.load(request.get_json())
        except ValidationError as err:
            return err.messages, 400

        if not HackerNewsNewStory.query.all():
            return (
                {"message": "HackerNewsTopStoryComment new_stories in this table"},
                400,
            )
        if incoming_pagination["page_number"] <= 0:
            return {"message": "pagination must be >= 1"}, 400
        page = paginate(
            HackerNewsNewStory.query.order_by(desc(HackerNewsNewStory.parsed_time))
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
    def get(cls, story_id):
        """
        Getting GET requests on the '/api/hacker_news/new_stories/story/<story_id>' 
        endpoint, and returning a hacker_news new_stories`s story with comments
        """
        try:
            incoming_story_id = story_id_schema.load(request.get_json())
        except ValidationError as err:
            return err.messages, 400
        if not HackerNewsNewStory.query.filter(
            HackerNewsNewStory.id == incoming_story_id["story_id"]
        ).first():
            return {"message": "Story not found"}, 400
        story = (
            HackerNewsNewStory.query.filter(
                HackerNewsNewStory.id == incoming_story_id["story_id"],
            )
            .order_by(HackerNewsNewStory.parsed_time)
            .first()
        )

        return jsonify(new_story_schema.dump(story))
