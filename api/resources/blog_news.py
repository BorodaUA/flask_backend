from flask import request, jsonify, make_response, jsonify
from flask_restful import Resource
from api.models.blog_news import BlogNewsStory, BlogNewsStoryComment
from api.schemas.blog_news import (
    BlogNewsStorySchema,
    BlogNewsCommentSchema,
    NewsPaginationSchema,
    StoryIdSchema,
)
from sqlalchemy import desc
from sqlalchemy_pagination import paginate
from marshmallow import ValidationError
from api.models import blog_news
from datetime import datetime
import time

news_pagination_schema = NewsPaginationSchema()
story_id_schema = StoryIdSchema()
story_schema = BlogNewsStorySchema()
stories_schema = BlogNewsStorySchema(many=True)
add_story_schema = BlogNewsStorySchema(
    exclude=[
    'id',
    'deleted',
    'type',
    # 'by',
    'time',
    # 'text',
    'dead',
    'parent',
    'poll',
    'kids',
    # 'url',
    'score',
    # 'title',
    'parts',
    'descendants',
    'comments',
    'origin',
    ]
)
add_comment_schema = BlogNewsStorySchema(
    exclude=[
    'id',
    'deleted',
    'type',
    # 'by',
    'time',
    # 'text',
    'dead',
    'parent',
    'poll',
    'kids',
    'url',
    'score',
    'title',
    'parts',
    'descendants',
    'comments',
    'origin',
    ]
)
# comments_schema = Comments_Schema(many=True)
# add_coment_schema = Add_Comment_Schema()


# blog_stories_schema = BlogNews_Stories_Schema(
#     many=True,
#     # exclude=[
#     #     "id",
#     #     "parse_dt",
#     #     "deleted",
#     #     "item_type",
#     #     "time",
#     #     "dead",
#     #     "parent",
#     #     "poll",
#     #     "kids",
#     #     "parts",
#     #     "descendants",
#     # ],
# )

# blog_story_schema = BlogNews_Stories_Schema(
#     # exclude=[
#     #     "id",
#     #     "parse_dt",
#     #     "deleted",
#     #     "item_type",
#     #     "time",
#     #     "dead",
#     #     "parent",
#     #     "poll",
#     #     "kids",
#     #     "parts",
#     #     "descendants",
#     # ],
# )

# {
# "parse_dt": "2020-06-12 12:05:22.637",
# "blog_url": "111",
# "item_id": 1,
# "deleted": false,
# "item_type": "news",
# "by":"bob_2",
# "time": "11111",
# "text": [],
# "dead": false,
# "text": "postman test comment",
# "parent": 12112412,
# "poll": 0,
# "url": "user_url",
# "score": 0,
# "title": "story_title",
# "parts": [],
# "descendants": 0,
# "comments": [],
# "origin": "blog_news"
# }
class BlogNewsStoriesResource(Resource):
    @classmethod
    def get(cls):
        """
        Getting GET requests on the '/api/blog_news/?pagenumber=N' 
        endpoint, and returning a list of blognews stories
        """
        try:
            pagenumber = {"pagenumber": request.args.get("pagenumber")}
            incoming_pagination = news_pagination_schema.load(pagenumber)
        except ValidationError as err:
            return err.messages, 400
        if incoming_pagination["pagenumber"] <= 0:
            return make_response(
                jsonify({"message": "pagenumber must be greater then 0", "code": 400}),
                400,
            )
        if not blog_news.BlogNewsStory.query.all():
            return make_response(
                jsonify({"message": "No blog stories found", "code": 404}),
                404,
            )
        page = paginate(
            BlogNewsStory.query.order_by(desc(BlogNewsStory.time))
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
                jsonify({"message": "Pagination page not found", "code": 404}),
                404,
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
        blog_news.Base.session.add(data)
        blog_news.Base.session.commit()
        return make_response(jsonify({"message": "Story added", "code": 201}), 201,)


class BlogNewsStoryResource(Resource):
    @classmethod
    def get(cls, story_id):
        """
        Getting GET requests on the '/api/blog_news/<story_id>' 
        endpoint, and returning a blognews story
        """
        try:
            story_id = {'story_id': story_id}
            incoming_story_id = story_id_schema.load(story_id)
        except ValidationError as err:
            return err.messages, 400
        if not BlogNewsStory.query.filter(
            BlogNewsStory.id == incoming_story_id["story_id"]
        ).first():
            return make_response(jsonify({"message": "Story not found", "code": 404}), 404)
        story = BlogNewsStory.query.filter(
            BlogNewsStory.id == incoming_story_id["story_id"]
        ).first()
        return make_response(jsonify(story_schema.dump(story)), 200)

    @classmethod
    def delete(cls, story_id):
        """
        Getting DELETE requests on the '/api/blog_news/<story_id>' 
        endpoint, and deleating a blognews story
        """
        try:
            story_id = {'story_id': story_id}
            incoming_story_id = story_id_schema.load(story_id)
        except ValidationError as err:
            return err.messages, 400
        if not BlogNewsStory.query.filter(
            BlogNewsStory.id == incoming_story_id["story_id"]
        ).first():
            return make_response(jsonify({"message": "Story not found", "code": 404}), 404)
        story = BlogNewsStory.query.filter(
            BlogNewsStory.id == incoming_story_id["story_id"]
        ).first()
        blog_news.Base.session.delete(story)
        blog_news.Base.session.commit()
        return make_response(jsonify({"message": "Story deleted", "code": 200}), 200,)

    @classmethod
    def patch(self, story_id):
        """
        Getting PATCH requests on the '/api/blog_news/<story_id>' 
        endpoint, and updating a blognews story
        """
        try:
            story_id = {'story_id': story_id}
            incoming_story_id = story_id_schema.load(story_id)
        except ValidationError as err:
            return err.messages, 400
        if not BlogNewsStory.query.filter(
            BlogNewsStory.id == incoming_story_id["story_id"]
        ).first():
            return make_response(jsonify({"message": "Story not found", "code": 404}), 404)
        try:
            story = add_story_schema.load(request.get_json())
        except ValidationError as err:
            return err.messages, 400
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
        blog_news.Base.session.commit()
        return make_response(jsonify({"message": "Story succesfully updated", "code": 200}), 200)









class BlogNewsStoryCommentsResource(Resource):
    @classmethod
    def get(cls, story_id):
        """
        Getting GET requests on the '/api/blognews/<story_id>/comments' 
        endpoint, and returning a list of blognews story`s comments
        """
        try:
            story_id = {'story_id': story_id}
            incoming_story_id = story_id_schema.load(story_id)
        except ValidationError as err:
            return err.messages, 400
        if not BlogNewsStory.query.filter(
            BlogNewsStory.id == incoming_story_id["story_id"]
        ).first():
            return make_response(jsonify({"message": "Story not found", "code": 404}), 404)
        comments = (
            BlogNewsStoryComment.query.filter(
                BlogNewsStoryComment.parent == incoming_story_id["story_id"]
            )
            .order_by(desc(BlogNewsStoryComment.time))
            .all()
        )
        return jsonify(stories_schema.dump(comments))

    @classmethod
    def post(cls, story_id):
        """
        Getting POST requests on the '/api/blognews/<story_id>/comments' 
        endpoint, and adding a comment to blognews story
        """
        try:
            story_id = {'story_id': story_id}
            incoming_story_id = story_id_schema.load(story_id)
        except ValidationError as err:
            return err.messages, 400
        if not BlogNewsStory.query.filter(
            BlogNewsStory.id == incoming_story_id["story_id"]
        ).first():
            return make_response(jsonify({"message": "Story not found", "code": 404}), 404)
        try:
            incoming_comment = add_comment_schema.load(request.get_json())
        except ValidationError as err:
            return err.messages, 400
        incoming_comment["dead"] = False
        incoming_comment["deleted"] = False
        incoming_comment["descendants"] = 0
        incoming_comment["kids"] = []
        incoming_comment["origin"] = 'my_blog'
        incoming_comment['parent'] = incoming_story_id["story_id"]
        incoming_comment["time"] = int(time.time())
        incoming_comment["type"] = 'comment'
        comment_data = BlogNewsStoryComment(**incoming_comment)
        blog_news.Base.session.add(comment_data)
        blog_news.Base.session.commit()
        return make_response(jsonify({"message": "Comment added", "code": 201}), 201,)


# def post(cls, story_id):
#         """
#         Getting POST requests on the '/api/blog_news/stories/<story_id>/comments' 
#         endpoint, and adding hacker_news top_stories`s story`s comment
#         """
#         try:
#             incoming_comment = add_coment_schema.load(request.get_json())
#         except ValidationError as err:
#             return err.messages, 400
#         if not BlogNews_Stories.query.filter(
#             BlogNews_Stories.item_id == incoming_comment["parent"]
#         ).first():
#             return make_response(jsonify({"message": "Story not found"}), 400)
#         incoming_comment.pop("existed_comment_id")
#         incoming_comment.pop("existed_comment_text")
#         comment_data = BlogNews_Stories_Comments(**incoming_comment)
#         blog_news.Base.session.add(comment_data)
#         blog_news.Base.session.commit()
#         return make_response(jsonify({"message": "Comment added",}), 201,)
