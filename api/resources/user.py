from flask import request, jsonify, make_response
from flask_restful import Resource
from api.models.user import UserModel, Base
from api.schemas.user import (
    UserUuidSchema,
    UserSchema,
    UserSigninSchema,
    UserPasswordUpdateSchema
)
from marshmallow import ValidationError


from passlib.hash import argon2
from sqlalchemy.exc import IntegrityError
from uuid import uuid4

user_uuid_schema = UserUuidSchema()
user_register_schema = UserSchema()
users_schema = UserSchema(many=True)
user_signin_schema = UserSigninSchema()
user_password_schema = UserPasswordUpdateSchema()


class UsersResource(Resource):
    @classmethod
    def get(cls):
        """
        Getting GET requests on the '/api/users' endpoint, and returning a list
        with all users in database.
        """
        if not UserModel.query.all():
            return make_response(
                jsonify({"message": "users not found", "code": 404}), 404
            )
        return users_schema.dump(UserModel.query.all())

    @classmethod
    def post(cls):
        """
        Getting POST requests on the '/api/users' endpoint, and
        saving the new user to the database.
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


class UserResource(Resource):
    @classmethod
    def get(cls, user_uuid):
        """
        Getting GET requests on the '/api/users/<user_uuid>' endpoint, and
        returning the user from the database.
        """
        try:
            user_uuid = {"user_uuid": user_uuid}
            incoming_user_uuid = user_uuid_schema.load(user_uuid)
        except ValidationError as err:
            return err.messages, 400
        if not UserModel.query.filter(
            UserModel.user_uuid == incoming_user_uuid['user_uuid']
        ).first():
            return make_response(
                jsonify({"message": "user not found", "code": 404}), 404
            )
        user = UserModel.query.filter(
            UserModel.user_uuid == incoming_user_uuid['user_uuid']
        ).first()
        return make_response(
            jsonify(user_register_schema.dump(user))
        )
        if not UserModel.query.filter(
            UserModel.user_uuid == incoming_user_uuid['user_uuid']
        ).first():
            return make_response(
                jsonify({"message": "user not found", "code": 404}), 404
            )

    @classmethod
    def patch(cls, user_uuid):
        """
        Getting PATCH requests on the '/api/users/<user_uuid>' endpoint, and
        updating the user data in the database.
        """
        try:
            user_uuid = {"user_uuid": user_uuid}
            incoming_user_uuid = user_uuid_schema.load(user_uuid)
        except ValidationError as err:
            return err.messages, 400
        if not UserModel.query.filter(
            UserModel.user_uuid == incoming_user_uuid['user_uuid']
        ).first():
            return make_response(
                jsonify({"message": "user not found", "code": 404}), 404
            )
        try:
            user = user_password_schema.load(request.get_json())
        except ValidationError as err:
            return err.messages, 400
        UserModel.query.filter(
            UserModel.user_uuid == incoming_user_uuid['user_uuid']
        ).update(
            {
                "password": argon2.hash(user["password"])
            }
        )
        Base.session.commit()
        return make_response(
            jsonify(
                {
                    "message": "User credentials succesfully updated",
                    "code": 200
                }
            ), 200
        )

    @classmethod
    def delete(cls, user_uuid):
        """
        Getting DELETE requests on the '/api/users/<user_uuid>' endpoint, and
        deleting the user in the database.
        """
        try:
            user_uuid = {"user_uuid": user_uuid}
            incoming_user_uuid = user_uuid_schema.load(user_uuid)
        except ValidationError as err:
            return err.messages, 400
        if not UserModel.query.filter(
            UserModel.user_uuid == incoming_user_uuid['user_uuid']
        ).first():
            return make_response(
                jsonify({"message": "user not found", "code": 404}), 404
            )
        user = UserModel.query.filter(
            UserModel.user_uuid == incoming_user_uuid['user_uuid']
        ).first()
        Base.session.delete(user)
        Base.session.commit()
        return make_response(jsonify(
            {
                "message": "User deleted",
                "code": 200
            }
        ), 200,)


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
