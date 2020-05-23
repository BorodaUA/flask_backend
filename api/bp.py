from flask import Blueprint
from flask_restful import Api, Resource
from .resources.user import UserRegistration, UserList, UserLogin

api_bp = Blueprint("api", __name__, url_prefix="/api")

api = Api(api_bp)


api.add_resource(UserRegistration, "/users/register")
api.add_resource(UserLogin, "/users/signin")
api.add_resource(UserList, "/users")
