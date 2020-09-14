from flask import Blueprint, make_response, jsonify
from flask_restful import Api
from .resources.user import UserRegistration, UserList, UserLogin
from .resources.hacker_news import (
    HackerNewsTopStoriesResourse,
    HackerNewsTopStoryResource,
    HackerNewsTopStoryCommentsResource,
    HackerNewsTopStoryCommentResource,
    HackerNewsNewStoriesResource,
    HackerNewsNewStoryResource,
    HackerNewsNewStoryCommentsResource
)
from .resources.blog_news import (
    BlogNewsStoriesResource,
    BlogNewsStoryResource,
    BlogNewsStoryCommentsResource,
    BlogNewsStoryCommentResource
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
    HackerNewsTopStoriesResourse,
    "/hackernews/topstories/",
    methods=["GET"]
)
api.add_resource(
    HackerNewsTopStoryResource,
    "/hackernews/topstories/<int:story_id>",
    methods=["GET"]
)
api.add_resource(
    HackerNewsTopStoryCommentsResource,
    "/hackernews/topstories/<int:story_id>/comments",
    methods=["GET", "POST"]
)
api.add_resource(
    HackerNewsTopStoryCommentResource,
    "/hackernews/topstories/<int:story_id>/comments/<int:comment_id>",
    methods=["PATCH", "DELETE"]
)
api.add_resource(
    HackerNewsNewStoriesResource,
    "/hackernews/newstories/",
    methods=["GET"]
)
api.add_resource(
    HackerNewsNewStoryResource,
    "/hackernews/newstories/<int:story_id>",
    methods=["GET"]
)
api.add_resource(
    HackerNewsNewStoryCommentsResource,
    "/hackernews/newstories/<int:story_id>/comments",
    methods=["GET"]
)
###
api.add_resource(
    BlogNewsStoriesResource,
    "/blognews/",
    methods=["GET", "POST"]
)
api.add_resource(
    BlogNewsStoryResource,
    "/blognews/<int:story_id>",
    methods=["GET", "DELETE", "PATCH"]
)
api.add_resource(
    BlogNewsStoryCommentsResource,
    "/blognews/<int:story_id>/comments",
    methods=["GET", "POST"]
)
api.add_resource(
    BlogNewsStoryCommentResource,
    "/blognews/<int:story_id>/comments/<int:comment_id>",
    methods=["GET", "DELETE", "PATCH"]
)
