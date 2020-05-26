from flask import Blueprint, make_response, jsonify
from flask_restful import Api, Resource
from .resources.user import UserRegistration, UserList, UserLogin
from .resources.hacker_news import HackerNews_TopStories_Resourse

api_bp = Blueprint("api", __name__, url_prefix="/api")

api = Api(api_bp)


@api_bp.route("/")
def api_home_page():
    return make_response(jsonify({"message": "Api Home page"}))


api.add_resource(UserRegistration, "/users/register")
api.add_resource(UserLogin, "/users/signin")
api.add_resource(UserList, "/users")
###
api.add_resource(HackerNews_TopStories_Resourse, "/hacker_news/top_stories")
