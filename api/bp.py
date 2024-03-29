from flask import Blueprint, make_response, jsonify
from flask_restful import Api
from .resources.user import (
    UsersResource,
    UserResource,
    UserLogin,
    UserStories,
    UserStory,
    UserComments,
)
from .resources.hacker_news_top_story import (
    HackerNewsTopStoriesResourse,
    HackerNewsTopStoryResource,
    HackerNewsTopStoryCommentsResource,
    HackerNewsTopStoryCommentResource,
)
from .resources.hacker_news_new_story import (
    HackerNewsNewStoriesResource,
    HackerNewsNewStoryResource,
    HackerNewsNewStoryCommentsResource,
    HackerNewsNewStoryCommentResource,
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


api.add_resource(
    UsersResource, "/users",
    methods=["GET", "POST"]
)
api.add_resource(
    UserResource, "/users/<username>",
    methods=["GET", "PATCH", "DELETE"]
)
api.add_resource(UserLogin, "/users/signin")
api.add_resource(
    UserStories, "/users/<username>/stories/",
    methods=["GET"]

)
api.add_resource(
    UserStory, "/users/<username>/stories/<story_id>",
    methods=["GET"]
)
api.add_resource(
    UserComments, "/users/<username>/comments/",
    methods=["GET"]
)
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
    methods=["GET", "POST"]
)
api.add_resource(
    HackerNewsNewStoryCommentResource,
    "/hackernews/newstories/<int:story_id>/comments/<int:comment_id>",
    methods=["PATCH", "DELETE"]
)
###
api.add_resource(
    BlogNewsStoriesResource,
    "/blognews/",
    methods=["GET", "POST"]
)
api.add_resource(
    BlogNewsStoryResource,
    "/blognews/<story_id>",
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
