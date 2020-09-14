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
    CommentIdSchema,
    HackerNews_NewStories_Schema,
    PaginationSchema,
    StorySchema,
    HackerNewsCommentSchema,
    Add_Comment_Schema,
)
from sqlalchemy import desc
from sqlalchemy_pagination import paginate
from marshmallow import ValidationError
import time
from datetime import datetime

from api.models import hacker_news

comment_id_schema = CommentIdSchema()
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
add_comment_schema = HackerNewsTopStorySchema(
    exclude=[
        "id",
        "hn_id",
        "deleted",
        "type",
        # 'by',
        "time",
        # 'text',
        "dead",
        "parent",
        "poll",
        "kids",
        # 'url',
        "score",
        # 'title',
        "parts",
        "descendants",
        "comments",
        "origin",
    ],
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


class HackerNewsTopStoryResource(Resource):
    @classmethod
    def get(cls, story_id):
        """
        Getting GET requests on the
        '/api/hackernews/topstories/<story_id>'
        endpoint, and returning a hacker_news top_stories`s story with comments
        """
        try:
            story_id = {"story_id": story_id}
            incoming_story_id = story_id_schema.load(story_id)
        except ValidationError as err:
            return err.messages, 400
        if not HackerNewsTopStory.query.filter(
            HackerNewsTopStory.id == incoming_story_id["story_id"]
        ).first():
            return make_response(
                jsonify({"message": "Story not found", "code": 404}), 404
            )
        story = (
            HackerNewsTopStory.query.filter(
                HackerNewsTopStory.id == incoming_story_id["story_id"],
            )
            .order_by(HackerNewsTopStory.parsed_time)
            .first()
        )
        return make_response(jsonify(top_story_schema.dump(story)), 200)


class HackerNewsTopStoryCommentsResource(Resource):
    @classmethod
    def get(cls, story_id):
        """
        Getting GET requests on the
        '/api/hackernews/topstories/<story_id>/comments' endpoint
        and returning a list of hackernews topstories story`s comments
        """
        try:
            story_id = {"story_id": story_id}
            incoming_story_id = story_id_schema.load(story_id)
        except ValidationError as err:
            return err.messages, 400
        if not HackerNewsTopStory.query.filter(
            HackerNewsTopStory.id == incoming_story_id["story_id"]
        ).first():
            return make_response(
                jsonify({"message": "Story not found", "code": 404}), 404
            )
        comments = (
            HackerNewsTopStoryComment.query.filter(
                HackerNewsTopStoryComment.parent ==
                incoming_story_id["story_id"]
            )
            .order_by(desc(HackerNewsTopStoryComment.parsed_time))
            .all()
        )
        return make_response(jsonify(comments_schema.dump(comments)), 200)

    def post(cls, story_id):
        """
        Getting POST requests on the
        '/api/hackernews/topstories/<story_id>/comments'
        endpoint, and adding a comment to hackernews topstories`s story
        """
        try:
            story_id = {"story_id": story_id}
            incoming_story = story_id_schema.load(story_id)
        except ValidationError as err:
            return err.messages, 400
        if not HackerNewsTopStory.query.filter(
            HackerNewsTopStory.id == incoming_story["story_id"]
        ).first():
            return make_response(
                jsonify({"message": "Story not found", "code": 404}), 404
            )
        try:
            incoming_comment = add_coment_schema.load(request.get_json())
        except ValidationError as err:
            return err.messages, 400
        incoming_comment["dead"] = False
        incoming_comment["deleted"] = False
        incoming_comment["descendants"] = 0
        incoming_comment["kids"] = []
        incoming_comment["origin"] = "my_blog"
        incoming_comment["parent"] = incoming_story["story_id"]
        incoming_comment["time"] = int(time.time())
        incoming_comment["type"] = "comment"
        incoming_comment["parsed_time"] = datetime.strftime(
                                datetime.now(), "%Y-%m-%d %H:%M:%S.%f"
                            )[:-3]
        comment_data = HackerNewsTopStoryComment(**incoming_comment)
        hacker_news.Base.session.add(comment_data)
        hacker_news.Base.session.commit()
        return make_response(jsonify(
            {
                "message": "Comment added",
                "code": 201
            }
        ), 201,)


class HackerNewsTopStoryCommentResource(Resource):
    @classmethod
    def patch(cls, story_id, comment_id):
        """
        Getting PATCH requests on the
        '/api/hackernews/topstories/<story_id>/comments/<comment_id>' endpoint
        and updating hackernews topstories story`s comment
        """
        try:
            story_id = {"story_id": story_id}
            incoming_story = story_id_schema.load(story_id)
        except ValidationError as err:
            return err.messages, 400
        try:
            comment_id = {"comment_id": comment_id}
            incoming_comment_id = comment_id_schema.load(comment_id)
        except ValidationError as err:
            return err.messages, 400
        if not HackerNewsTopStory.query.filter(
            HackerNewsTopStory.id == incoming_story["story_id"]
        ).first():
            return make_response(
                jsonify({"message": "Story not found", "code": 404}), 404
            )
        if not HackerNewsTopStoryComment.query.filter(
            HackerNewsTopStoryComment.id == incoming_comment_id["comment_id"]
        ).first():
            return make_response(
                jsonify({"message": "Comment not found", "code": 404}), 404
            )
        try:
            incoming_comment = add_comment_schema.load(request.get_json())
        except ValidationError as err:
            return err.messages, 400
        HackerNewsTopStoryComment.query.filter(
            HackerNewsTopStoryComment.id == incoming_comment_id["comment_id"]
        ).update(
            {
                "parsed_time": datetime.strftime(
                    datetime.now(),
                    "%Y-%m-%d %H:%M:%S.%f"
                )[:-3],
                "text": incoming_comment["text"]
            }
        )
        hacker_news.Base.session.commit()
        return make_response(jsonify(
            {
                "message": "Comment updated",
                "code": 200
            }
        ), 200,)

    @classmethod
    def delete(cls, story_id, comment_id):
        """
        Getting DELETE requests on the
        '/api/hackernews/topstories/<story_id>/comments/<comment_id>' endpoint
        and deleting hackernews topstories story`s comment
        """
        try:
            story_id = {"story_id": story_id}
            incoming_story = story_id_schema.load(story_id)
        except ValidationError as err:
            return err.messages, 400
        try:
            comment_id = {"comment_id": comment_id}
            incoming_comment_id = comment_id_schema.load(comment_id)
        except ValidationError as err:
            return err.messages, 400
        if not HackerNewsTopStory.query.filter(
            HackerNewsTopStory.id == incoming_story["story_id"]
        ).first():
            return make_response(
                jsonify({"message": "Story not found", "code": 404}), 404
            )
        if not HackerNewsTopStoryComment.query.filter(
            HackerNewsTopStoryComment.id == incoming_comment_id["comment_id"]
        ).first():
            return make_response(
                jsonify({"message": "Comment not found", "code": 404}), 404
            )
        try:
            incoming_comment = add_comment_schema.load(request.get_json())
        except ValidationError as err:
            return err.messages, 400
        HackerNewsTopStoryComment.query.filter(
            HackerNewsTopStoryComment.id == incoming_comment_id["comment_id"]
        ).delete()
        hacker_news.Base.session.commit()
        return make_response(jsonify(
            {
                "message": "Comment deleted",
                "code": 200
            }
        ), 200,)


class HackerNewsNewStoriesResource(Resource):
    @classmethod
    def get(cls):
        """
        Getting GET requests on the
        '/api/hackernews/newstories/?pagenumber=N'
        endpoint, and returning a page with 30 hacker_news
        new_stories from database.
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
        if not HackerNewsNewStory.query.all():
            return make_response(
                jsonify(
                    {
                        "message": "No hackernews newstories found",
                        "code": 404
                    }
                ), 404,
            )
        page = paginate(
            HackerNewsNewStory.query.order_by(
                desc(HackerNewsNewStory.parsed_time)
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
            "items": new_stories_schema.dump(page.items),
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
