from flask import request, jsonify, make_response, g
from flask_restful import Resource
from api.models.blog_news import BlogNewsStory, BlogNewsStoryComment
from api.schemas.blog_news import (
    BlogNewsStorySchema,
    BlogNewsCommentSchema,
    NewsPaginationSchema,
    StoryIdSchema,
    CommentIdSchema,
)
from sqlalchemy import desc
from sqlalchemy_pagination import paginate
from marshmallow import ValidationError
import time

news_pagination_schema = NewsPaginationSchema()
story_id_schema = StoryIdSchema()
comment_id_schema = CommentIdSchema()
story_schema = BlogNewsStorySchema()
stories_schema = BlogNewsStorySchema(many=True)
add_story_schema = BlogNewsStorySchema(
    exclude=[
        "id",
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
    ]
)
edit_story_schema = BlogNewsStorySchema(
    exclude=[
        "id",
        "deleted",
        "type",
        'by',
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
    ]
)
add_comment_schema = BlogNewsCommentSchema(
    exclude=[
        "id",
        "deleted",
        "type",
        # 'by',
        "time",
        # 'text',
        "dead",
        "parent",
        "poll",
        "kids",
        "url",
        "score",
        "title",
        "parts",
        "descendants",
        "origin",
    ]
)


class BlogNewsStoriesResource(Resource):
    @classmethod
    def get(cls):
        """
        Getting GET requests on the '/api/blognews/?pagenumber=N'
        endpoint, and returning a list of blognews stories
        """
        try:
            pagenumber = {"pagenumber": request.args.get("pagenumber")}
            incoming_pagination = news_pagination_schema.load(pagenumber)
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
        db_session = g.flask_backend_session
        blognews_stories = db_session.query(BlogNewsStory).all()
        if not blognews_stories:
            return make_response(
                jsonify(
                    {
                        "message": "No blog stories found",
                        "code": 404
                    }
                ), 404,
            )
        page = paginate(
            db_session.query(
                BlogNewsStory
            ).order_by(desc(BlogNewsStory.time))
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

    @classmethod
    def post(cls):
        """
        Getting POST requests on the '/api/blognews/' endpoint, and
        saving new story to the database.
        """
        try:
            story = add_story_schema.load(request.get_json())
        except ValidationError as err:
            return err.messages, 400
        db_session = g.flask_backend_session
        full_story = {
            "time": int(time.time()),
            "deleted": False,
            "type": "story",
            "by": story["by"],
            "text": story["text"],
            "url": story["url"],
            "dead": False,
            "parent": None,
            "poll": None,
            "score": 1,
            "title": story["title"],
            "parts": [],
            "descendants": None,
            "origin": "my_blog",
        }
        data = BlogNewsStory(**full_story)
        db_session.add(data)
        db_session.commit()
        return make_response(jsonify(
            {
                "message": "Story added",
                "code": 201
            }
        ), 201,)


class BlogNewsStoryResource(Resource):
    @classmethod
    def get(cls, story_id):
        """
        Getting GET requests on the '/api/blog_news/<story_id>'
        endpoint, and returning a blognews story
        """
        try:
            story_id = {"story_id": story_id}
            incoming_story_id = story_id_schema.load(story_id)
        except ValidationError as err:
            return err.messages, 400
        story = BlogNewsStory.query.filter(
            BlogNewsStory.id == incoming_story_id["story_id"]
        ).first()
        if not story:
            BlogNewsStory.session.close()
            return make_response(
                jsonify({"message": "Story not found", "code": 404}), 404
            )
        BlogNewsStory.session.close()
        return make_response(jsonify(story_schema.dump(story)), 200)

    @classmethod
    def delete(cls, story_id):
        """
        Getting DELETE requests on the '/api/blog_news/<story_id>'
        endpoint, and deleting a blognews story
        """
        try:
            story_id = {"story_id": story_id}
            incoming_story_id = story_id_schema.load(story_id)
        except ValidationError as err:
            return err.messages, 400
        story = BlogNewsStory.query.filter(
            BlogNewsStory.id == incoming_story_id["story_id"]
        ).first()
        if not story:
            BlogNewsStory.session.close()
            return make_response(
                jsonify({"message": "Story not found", "code": 404}), 404
            )
        BlogNewsStory.session.delete(story)
        BlogNewsStory.session.commit()
        return make_response(jsonify(
            {
                "message": "Story deleted",
                "code": 200
            }
        ), 200,)

    @classmethod
    def patch(self, story_id):
        """
        Getting PATCH requests on the '/api/blog_news/<story_id>'
        endpoint, and updating a blognews story
        """
        try:
            story_id = {"story_id": story_id}
            incoming_story_id = story_id_schema.load(story_id)
        except ValidationError as err:
            return err.messages, 400
        try:
            story = edit_story_schema.load(request.get_json())
        except ValidationError as err:
            return err.messages, 400
        blognews_story = BlogNewsStory.query.filter(
            BlogNewsStory.id == incoming_story_id["story_id"]
        ).first()
        if not blognews_story:
            BlogNewsStory.session.close()
            return make_response(
                jsonify({"message": "Story not found", "code": 404}), 404
            )
        BlogNewsStory.query.filter(
            BlogNewsStory.id == incoming_story_id["story_id"]
        ).update(
            {
                "text": story["text"],
                "url": story["url"],
                "title": story["title"],
                "time": int(time.time()),
            }
        )
        BlogNewsStory.session.commit()
        return make_response(
            jsonify({"message": "Story succesfully updated", "code": 200}), 200
        )


class BlogNewsStoryCommentsResource(Resource):
    @classmethod
    def get(cls, story_id):
        """
        Getting GET requests on the '/api/blognews/<story_id>/comments'
        endpoint, and returning a list of blognews story`s comments
        """
        try:
            story_id = {"story_id": story_id}
            incoming_story_id = story_id_schema.load(story_id)
        except ValidationError as err:
            return err.messages, 400
        story = BlogNewsStory.query.filter(
            BlogNewsStory.id == incoming_story_id["story_id"]
        ).first()
        if not story:
            BlogNewsStory.session.close()
            return make_response(
                jsonify({"message": "Story not found", "code": 404}), 404
            )
        comments = (
            BlogNewsStoryComment.query.filter(
                BlogNewsStoryComment.parent == incoming_story_id["story_id"]
            )
            .order_by(desc(BlogNewsStoryComment.time))
            .all()
        )
        BlogNewsStory.session.close()
        return jsonify(stories_schema.dump(comments))

    @classmethod
    def post(cls, story_id):
        """
        Getting POST requests on the '/api/blognews/<story_id>/comments'
        endpoint, and adding a comment to blognews story
        """
        try:
            story_id = {"story_id": story_id}
            incoming_story_id = story_id_schema.load(story_id)
        except ValidationError as err:
            return err.messages, 400
        try:
            incoming_comment = add_comment_schema.load(request.get_json())
        except ValidationError as err:
            return err.messages, 400
        story = BlogNewsStory.query.filter(
            BlogNewsStory.id == incoming_story_id["story_id"]
        ).first()
        if not story:
            BlogNewsStory.session.close()
            return make_response(
                jsonify({"message": "Story not found", "code": 404}), 404
            )
        incoming_comment["dead"] = False
        incoming_comment["deleted"] = False
        incoming_comment["descendants"] = 0
        incoming_comment["kids"] = []
        incoming_comment["origin"] = "my_blog"
        incoming_comment["parent"] = incoming_story_id["story_id"]
        incoming_comment["time"] = int(time.time())
        incoming_comment["type"] = "comment"
        comment_data = BlogNewsStoryComment(**incoming_comment)
        BlogNewsStoryComment.session.add(comment_data)
        BlogNewsStoryComment.session.commit()
        return make_response(jsonify(
            {
                "message": "Comment added",
                "code": 201
            }
        ), 201,)


class BlogNewsStoryCommentResource(Resource):
    @classmethod
    def get(cls, story_id, comment_id):
        """
        Getting GET requests on the
        '/api/blognews/<story_id>/comments/<comment_id>'
        endpoint, and returning a blognews story comment by id
        """
        try:
            story_id = {"story_id": story_id}
            incoming_story_id = story_id_schema.load(story_id)
        except ValidationError as err:
            return err.messages, 400
        try:
            comment_id = {"comment_id": comment_id}
            incoming_comment_id = comment_id_schema.load(comment_id)
        except ValidationError as err:
            return err.messages, 400
        story = BlogNewsStory.query.filter(
            BlogNewsStory.id == incoming_story_id["story_id"]
        ).first()
        comment = BlogNewsStoryComment.query.filter(
            BlogNewsStoryComment.id == incoming_comment_id["comment_id"]
        ).first()
        if not story:
            BlogNewsStory.session.close()
            return make_response(
                jsonify({"message": "Story not found", "code": 404}), 404
            )
        if not comment:
            BlogNewsStoryComment.session.close()
            return make_response(
                jsonify({"message": "Comment not found", "code": 404}), 404
            )
        BlogNewsStoryComment.session.close()
        return make_response(jsonify(story_schema.dump(comment)), 200)

    @classmethod
    def delete(cls, story_id, comment_id):
        """
        Getting DELETE requests on the
        '/api/blognews/<story_id>/comments/<comment_id>'
        endpoint, and deleting a blognews story comment by id
        """
        try:
            story_id = {"story_id": story_id}
            incoming_story_id = story_id_schema.load(story_id)
        except ValidationError as err:
            return err.messages, 400
        try:
            comment_id = {"comment_id": comment_id}
            incoming_comment_id = comment_id_schema.load(comment_id)
        except ValidationError as err:
            return err.messages, 400
        story = BlogNewsStory.query.filter(
            BlogNewsStory.id == incoming_story_id["story_id"]
        ).first()
        comment = BlogNewsStoryComment.query.filter(
            BlogNewsStoryComment.id == incoming_comment_id["comment_id"]
        ).first()
        if not story:
            BlogNewsStory.session.close()
            return make_response(
                jsonify({"message": "Story not found", "code": 404}), 404
            )
        if not comment:
            BlogNewsStoryComment.session.close()
            return make_response(
                jsonify({"message": "Comment not found", "code": 404}), 404
            )
        BlogNewsStoryComment.query.filter(
            BlogNewsStoryComment.id == incoming_comment_id["comment_id"]
        ).delete()
        BlogNewsStoryComment.session.commit()
        return make_response(jsonify(
            {
                "message": "Comment deleted",
                "code": 200
            }
        ), 200,)

    @classmethod
    def patch(cls, story_id, comment_id):
        """
        Getting PATCH requests on the
        '/api/blognews/<story_id>/comments/<comment_id>'
        endpoint, and updating a blognews story comment by id
        """
        try:
            story_id = {"story_id": story_id}
            incoming_story_id = story_id_schema.load(story_id)
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
        story = BlogNewsStory.query.filter(
            BlogNewsStory.id == incoming_story_id["story_id"]
        ).first()
        comment = BlogNewsStoryComment.query.filter(
            BlogNewsStoryComment.id == incoming_comment_id["comment_id"]
        ).first()
        if not story:
            BlogNewsStory.session.close()
            return make_response(
                jsonify({"message": "Story not found", "code": 404}), 404
            )
        if not comment:
            BlogNewsStoryComment.session.close()
            return make_response(
                jsonify({"message": "Comment not found", "code": 404}), 404
            )
        BlogNewsStoryComment.query.filter(
            BlogNewsStoryComment.id == incoming_comment_id["comment_id"]
        ).update({"text": incoming_comment["text"], "time": int(time.time())})
        BlogNewsStoryComment.session.commit()
        return make_response(jsonify(
            {
                "message": "Comment updated",
                "code": 200
            }
        ), 200,)
