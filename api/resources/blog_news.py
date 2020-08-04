from flask import request, jsonify, make_response, jsonify
from flask_restful import Resource
from api.models.blog_news import BlogNewsStory, BlogNewsStoryComment
from api.schemas.blog_news import (
    BlogNews_Stories_Schema,
    Comments_Schema,
    NewsPagination_Schema,
    Story_id_Schema,
    Comments_Schema,
    Add_Comment_Schema,
)
from sqlalchemy import desc
from sqlalchemy_pagination import paginate
from marshmallow import ValidationError
from api.models import blog_news
from datetime import datetime

news_pagination = NewsPagination_Schema()
story_id_schema = Story_id_Schema()
comments_schema = Comments_Schema(many=True)
add_coment_schema = Add_Comment_Schema()


blog_stories_schema = BlogNews_Stories_Schema(
    many=True,
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

blog_story_schema = BlogNews_Stories_Schema(
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
class BlogNews_Stories_Resource(Resource):
    @classmethod
    def post(cls):
        """
        Getting POST requests on the '/api/submit' endpoint, and
        saving new story to the database.
        """
        try:
            story = blog_story_schema.load(request.get_json())
        except ValidationError as err:
            return err.messages, 400
        full_story = {
            "time": datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S.%f")[:-3],
            "deleted": False,
            "item_type": "story",
            "by": story["by"],
            "text": story["text"],
            "dead": False,
            "parent": 0,
            "poll": 0,
            "score": 1,
            "title": story["title"],
            "parts": [],
            "descendants": 1,
            "origin": "blog_story",
        }
        data = BlogNews_Stories(**full_story)
        blog_news.Base.session.add(data)
        blog_news.Base.session.commit()
        return make_response(jsonify({"message": "Story added",}), 201,)


class BlogNews_StoriesPages_Resource(Resource):
    @classmethod
    def get(cls, page_number):
        """
        Getting GET requests on the '/api/blog_news/<page_number>' 
        endpoint, and returning a list of blog_news top_stories
        """
        try:
            incoming_pagination = news_pagination.load(request.get_json())
        except ValidationError as err:
            return err.messages, 400
        if incoming_pagination["page_number"] <= 0:
            return {"message": "pagination must be >= 1"}, 400
        if not blog_news.BlogNews_Stories.query.all():
            return {"message": "No blog stories found"}, 400
        page = paginate(
            BlogNews_Stories.query.order_by(desc(BlogNews_Stories.time))
            .limit(500)
            .from_self(),
            incoming_pagination["page_number"],
            30,
        )
        result_page = {
            "current_page": incoming_pagination["page_number"],
            "has_next": page.has_next,
            "has_previous": page.has_previous,
            "items": blog_stories_schema.dump(page.items),
            "next_page": page.next_page,
            "previous_page": page.previous_page,
            "pages": page.pages,
            "total": page.total,
        }
        if incoming_pagination["page_number"] > result_page["pages"]:
            return {"message": "Pagination page not found"}, 400
        return jsonify(result_page)


class BlogNews_Stories_Comments_Resource(Resource):
    @classmethod
    def get(cls, story_id):
        """
        Getting GET requests on the '/api/blog_news/stories/<story_id>/comments' 
        endpoint, and returning a list of blog_news stories`s story`s comments
        """
        try:
            incoming_story_id = story_id_schema.load(request.get_json())
        except ValidationError as err:
            return err.messages, 400
        if not BlogNews_Stories.query.filter(
            BlogNews_Stories.item_id == incoming_story_id["story_id"]
        ).first():
            return make_response(jsonify({"message": "Comments not found"}), 400)
        comments = (
            BlogNews_Stories_Comments.query.filter(
                BlogNews_Stories_Comments.parent == incoming_story_id["story_id"]
            )
            .order_by(desc(BlogNews_Stories_Comments.parse_dt))
            .all()
        )
        return jsonify(comments_schema.dump(comments))

    def post(cls, story_id):
        """
        Getting POST requests on the '/api/blog_news/stories/<story_id>/comments' 
        endpoint, and adding hacker_news top_stories`s story`s comment
        """
        try:
            incoming_comment = add_coment_schema.load(request.get_json())
        except ValidationError as err:
            return err.messages, 400
        if not BlogNews_Stories.query.filter(
            BlogNews_Stories.item_id == incoming_comment["parent"]
        ).first():
            return make_response(jsonify({"message": "Story not found"}), 400)
        incoming_comment.pop("existed_comment_id")
        incoming_comment.pop("existed_comment_text")
        comment_data = BlogNews_Stories_Comments(**incoming_comment)
        blog_news.Base.session.add(comment_data)
        blog_news.Base.session.commit()
        return make_response(jsonify({"message": "Comment added",}), 201,)
