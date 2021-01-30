from flask import request, jsonify, make_response, g
from flask_restful import Resource
from api.models.hacker_news import (
    HackerNewsNewStory,
    HackerNewsNewStoryComment,
)
from api.schemas.hacker_news import (
    HackerNewsStorySchema,
    HackerNewsCommentSchema,
    CommentIdSchema,
    PageNumberSchema,
    StoryIdSchema,
)
from sqlalchemy import desc
from sqlalchemy_pagination import paginate
from marshmallow import ValidationError
import time
from datetime import datetime

page_number_schema = PageNumberSchema()
comment_id_schema = CommentIdSchema()
story_id_schema = StoryIdSchema()
#
stories_schema = HackerNewsStorySchema(many=True)
story_schema = HackerNewsStorySchema()
#
comments_schema = HackerNewsCommentSchema(many=True)
add_comment_schema = HackerNewsStorySchema(
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
            incoming_pagination = page_number_schema.load(pagenumber)
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
        db_session = g.hacker_news_session
        stories = db_session.query(HackerNewsNewStory).all()
        if not stories:
            return make_response(
                jsonify(
                    {
                        "message": "No hackernews newstories found",
                        "code": 404
                    }
                ), 404,
            )
        page = paginate(
            db_session.query(HackerNewsNewStory).order_by(
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
            "items": stories_schema.dump(page.items),
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
        return jsonify(result_page)


class HackerNewsNewStoryResource(Resource):
    @classmethod
    def get(cls, story_id):
        """
        Getting GET requests on the
        '/api/hackernews/newstories/<story_id>'
        endpoint, and returning a hacker_news new_stories`s story with comments
        """
        try:
            story_id = {"story_id": story_id}
            incoming_story_id = story_id_schema.load(story_id)
        except ValidationError as err:
            return err.messages, 400
        db_session = g.hacker_news_session
        story = (
            db_session.query(HackerNewsNewStory).filter(
                HackerNewsNewStory.hn_id == incoming_story_id["story_id"],
            )
            .order_by(HackerNewsNewStory.parsed_time)
            .first()
        )
        if not story:
            return make_response(
                jsonify({"message": "Story not found", "code": 404}), 404
            )
        return make_response(jsonify(story_schema.dump(story)), 200)


class HackerNewsNewStoryCommentsResource(Resource):
    @classmethod
    def get(cls, story_id):
        """
        Getting GET requests on the
        '/api/hackernews/newstories/<story_id>/comments' endpoint
        and returning a list of hackernews newstories story`s comments
        """
        try:
            story_id = {"story_id": story_id}
            incoming_story_id = story_id_schema.load(story_id)
        except ValidationError as err:
            return err.messages, 400
        db_session = g.hacker_news_session
        story = db_session.query(HackerNewsNewStory).filter(
            HackerNewsNewStory.hn_id == incoming_story_id["story_id"]
        ).first()
        if not story:
            return make_response(
                jsonify({"message": "Story not found", "code": 404}), 404
            )
        comments = (
            db_session.query(HackerNewsNewStoryComment).filter(
                HackerNewsNewStoryComment.parent ==
                incoming_story_id["story_id"]
            )
            .order_by(desc(HackerNewsNewStoryComment.parsed_time))
            .all()
        )
        return make_response(jsonify(comments_schema.dump(comments)), 200)

    def post(cls, story_id):
        """
        Getting POST requests on the
        '/api/hackernews/newstories/<story_id>/comments'
        endpoint, and adding a comment to hackernews newstories`s story
        """
        try:
            story_id = {"story_id": story_id}
            incoming_story = story_id_schema.load(story_id)
        except ValidationError as err:
            return err.messages, 400
        try:
            incoming_comment = add_comment_schema.load(request.get_json())
        except ValidationError as err:
            return err.messages, 400
        db_session = g.hacker_news_session
        story = db_session.query(HackerNewsNewStory).filter(
            HackerNewsNewStory.hn_id == incoming_story["story_id"]
        ).first()
        if not story:
            return make_response(
                jsonify({"message": "Story not found", "code": 404}), 404
            )
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
        comment_data = HackerNewsNewStoryComment(**incoming_comment)
        db_session.add(comment_data)
        db_session.commit()
        return make_response(jsonify(
            {
                "message": "Comment added",
                "code": 201
            }
        ), 201,)


class HackerNewsNewStoryCommentResource(Resource):
    @classmethod
    def patch(cls, story_id, comment_id):
        """
        Getting PATCH requests on the
        '/api/hackernews/newstories/<story_id>/comments/<comment_id>' endpoint
        and updating hackernews newstories story`s comment
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
        try:
            incoming_comment = add_comment_schema.load(request.get_json())
        except ValidationError as err:
            return err.messages, 400
        db_session = g.hacker_news_session
        story = db_session.query(HackerNewsNewStory).filter(
            HackerNewsNewStory.hn_id == incoming_story["story_id"]
        ).first()
        comment = db_session.query(HackerNewsNewStoryComment).filter(
            HackerNewsNewStoryComment.id ==
            incoming_comment_id["comment_id"]
        ).first()
        if not story:
            return make_response(
                jsonify({"message": "Story not found", "code": 404}), 404
            )
        if not comment:
            return make_response(
                jsonify({"message": "Comment not found", "code": 404}), 404
            )
        db_session.query(HackerNewsNewStoryComment).filter(
            HackerNewsNewStoryComment.id ==
            incoming_comment_id["comment_id"]
        ).update(
            {
                "updated_time": datetime.strftime(
                    datetime.now(),
                    "%Y-%m-%d %H:%M:%S.%f"
                )[:-3],
                "text": incoming_comment["text"]
            }
        )
        db_session.commit()
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
        '/api/hackernews/newstories/<story_id>/comments/<comment_id>' endpoint
        and deleting hackernews newstories story`s comment
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
        story = HackerNewsNewStory.query.filter(
            HackerNewsNewStory.hn_id ==
            incoming_story["story_id"]
        ).first()
        comment = HackerNewsNewStoryComment.query.filter(
            HackerNewsNewStoryComment.id == incoming_comment_id["comment_id"]
        ).first()
        if not story:
            HackerNewsNewStory.session.close()
            return make_response(
                jsonify({"message": "Story not found", "code": 404}), 404
            )
        if not comment:
            HackerNewsNewStoryComment.session.close()
            return make_response(
                jsonify({"message": "Comment not found", "code": 404}), 404
            )
        HackerNewsNewStoryComment.query.filter(
            HackerNewsNewStoryComment.id ==
            incoming_comment_id["comment_id"]
        ).delete()
        HackerNewsNewStoryComment.session.commit()
        HackerNewsNewStoryComment.session.close()
        HackerNewsNewStory.session.close()
        return make_response(jsonify(
            {
                "message": "Comment deleted",
                "code": 200
            }
        ), 200,)
