from flask import request, jsonify, make_response
from flask_restful import Resource
from api.models.user import UserModel, Base
from api.schemas.user import UserRegisterSchema, UserSigninSchema
from marshmallow import ValidationError


from passlib.hash import argon2
from sqlalchemy.exc import IntegrityError
from uuid import uuid4

user_register_schema = UserRegisterSchema()
users_schema = UserRegisterSchema(many=True)

user_signin_schema = UserSigninSchema()


class UserRegistration(Resource):
    @classmethod
    def post(cls):
        """
        Getting POST requests on the '/api/users/register' endpoint, and
        saving new users to the database.
        """
        try:
            user = user_register_schema.load(request.get_json())
        except ValidationError as err:
            return err.messages, 400
        if UserModel.query.filter_by(username=user["username"]).first():
            return make_response(
                jsonify(
                    {
                        "message": "User with this username already exist"
                    }
                ), 400
            )
        if UserModel.query.filter_by(
            email_address=user["email_address"]
        ).first():
            return make_response(
                jsonify({"message": "User with this email already exist"}), 400
            )
        user["password"] = argon2.hash(user["password"])
        ###
        flag = True
        while flag:
            try:
                user["user_uuid"] = str(uuid4())
                user["origin"] = "my_blog"
                Base.session.add(UserModel(**user))
                Base.session.commit()
                Base.session.close()
                return make_response(
                    jsonify(
                        {
                            "message": (
                                f"Registration succesfull "
                                f"{user['username']}"
                            ),
                            "username": user["username"],
                            "user_uuid": user["user_uuid"],
                            "origin": user["origin"],
                        }
                    ),
                    201,
                )
                flag = False
            except IntegrityError:
                Base.session.rollback()


class UserLogin(Resource):
    @classmethod
    def post(cls):
        """
        Getting POST requests on the '/api/users/login' endpoint, and
        returning 200 http status code if username and password were correct.
        And 400 http status if user was not found or password didn't match.
        """
        try:
            incoming_user = user_signin_schema.load(request.get_json())
        except ValidationError as err:
            return err.messages, 400
        ###
        db_user = UserModel.query.filter_by(
            username=incoming_user["username"]
        ).first()
        db_email_address = UserModel.query.filter_by(
            email_address=incoming_user["email_address"]
        ).first()
        ###
        if db_user:
            if argon2.verify(incoming_user["password"], db_user.password):
                return make_response(
                    jsonify(
                        {
                            "message": f"Login succesfull {db_user.username}",
                            "user_uuid": db_user.user_uuid,
                            "username": db_user.username,
                            "origin": db_user.origin,
                        }
                    ),
                    200,
                )
            return make_response(
                jsonify({"message": "Username or password Incorect!"}), 400
            )
        elif db_email_address:
            if argon2.verify(
                incoming_user["password"],
                db_email_address.password
            ):
                return make_response(
                    jsonify(
                        {
                            "message": (
                                f"Login succesfull "
                                f"{db_email_address.email_address}"
                            ),
                            "user_uuid": db_email_address.user_uuid,
                            "username": db_email_address.username,
                            "origin": db_email_address.origin,
                        }
                    ),
                    200,
                )
            return make_response(
                jsonify(
                    {
                        "message": "Email address or password Incorect!"
                    }
                ), 400
            )
        else:
            return make_response(
                jsonify(
                    {
                        "message": "Username or Email address not found."
                    }
                ), 400
            )


class UserList(Resource):
    @classmethod
    def get(cls):
        """
        Getting GET requests on the '/api/users' endpoint, and returning a list
        with all users in database.
        """
        if not UserModel.query.all():
            return {"message": "No users in this table"}
        return {"message": users_schema.dump(UserModel.query.all())}
