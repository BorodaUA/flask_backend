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
            story = story_schema.load(request.get_json())
        except ValidationError as err:
            return err.messages, 400
        full_story = {
            "time": int(time.time()),
            "deleted": False,
            "type": "story",
            "by": story["by"],
            "text": story["text"],
            "dead": False,
            "parent": None,
            "poll": None,
            "score": 1,
            "title": story["title"],
            "parts": [],
            "descendants": None,
            "origin": "blogstory",
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


# class BlogNews_Stories_Comments_Resource(Resource):
#     @classmethod
#     def get(cls, story_id):
#         """
#         Getting GET requests on the '/api/blog_news/stories/<story_id>/comments' 
#         endpoint, and returning a list of blog_news stories`s story`s comments
#         """
#         try:
#             incoming_story_id = story_id_schema.load(request.get_json())
#         except ValidationError as err:
#             return err.messages, 400
#         if not BlogNews_Stories.query.filter(
#             BlogNews_Stories.item_id == incoming_story_id["story_id"]
#         ).first():
#             return make_response(jsonify({"message": "Comments not found"}), 400)
#         comments = (
#             BlogNews_Stories_Comments.query.filter(
#                 BlogNews_Stories_Comments.parent == incoming_story_id["story_id"]
#             )
#             .order_by(desc(BlogNews_Stories_Comments.parse_dt))
#             .all()
#         )
#         return jsonify(comments_schema.dump(comments))

#     def post(cls, story_id):
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
