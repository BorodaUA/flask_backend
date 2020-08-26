from flask import Blueprint, make_response, jsonify
from flask_restful import Api, Resource
from .resources.user import UserRegistration, UserList, UserLogin
from .resources.hacker_news import (
    HackerNews_TopStories_Resourse,
    HackerNews_TopStories_Story_Resource,
    HackerNews_TopStories_Story_Comments_Resource,
    HackerNews_NewStories_Resource,
    HackerNews_NewStories_Story_Resource,
)
from .resources.blog_news import (
    BlogNewsStoriesResource,
    BlogNews_StoriesPages_Resource,
    BlogNews_Stories_Comments_Resource,
)

api_bp = Blueprint("api", __name__, url_prefix="/api")

api = Api(api_bp)


@api_bp.route("/")
def api_home_page():
    return make_response(jsonify({"message": "Api Home page"}))


api.add_resource(UserRegistration, "/users/register")
api.add_resource(UserLogin, "/users/signin")
api.add_resource(UserList, "/users")
###
api.add_resource(
    HackerNews_TopStories_Resourse, "/hacker_news/top_stories/<int:page_number>"
)
api.add_resource(
    HackerNews_TopStories_Story_Resource,
    "/hacker_news/top_stories/stories/<int:story_id>",
)
api.add_resource(
    HackerNews_TopStories_Story_Comments_Resource,
    "/hacker_news/top_stories/stories/<int:story_id>/comments",
)
api.add_resource(
    HackerNews_NewStories_Resource, "/hacker_news/new_stories/<int:page_number>"
)
api.add_resource(
    HackerNews_NewStories_Story_Resource,
    "/hacker_news/new_stories/stories/<int:story_id>",
)
###
api.add_resource(BlogNewsStoriesResource, "/blognews/", methods=["GET", "POST"])
api.add_resource(
    BlogNews_Stories_Comments_Resource, "/blog_news/stories/<int:story_id>/comments"
)
