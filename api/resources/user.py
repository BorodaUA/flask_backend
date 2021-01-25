from flask import request, jsonify, make_response
from flask_restful import Resource
from api.models.user import UserModel, Base
from api.models.blog_news import BlogNewsStory, BlogNewsStoryComment
from api.schemas.user import (
    UserSchema,
    UserSigninSchema,
    UserPasswordUpdateSchema,
    UsernameSchema
)
from api.schemas.blog_news import (
    BlogNewsStorySchema,
    StoryIdSchema,
    NewsPaginationSchema
)
from marshmallow import ValidationError
from sqlalchemy_pagination import paginate
from sqlalchemy import desc
from passlib.hash import argon2
from sqlalchemy.exc import IntegrityError
from uuid import uuid4

user_register_schema = UserSchema()
users_schema = UserSchema(many=True)
user_signin_schema = UserSigninSchema()
user_password_schema = UserPasswordUpdateSchema()
username_schema = UsernameSchema()
blognews_stories_schema = BlogNewsStorySchema(many=True)
blognews_story_schema = BlogNewsStorySchema()
story_id_schema = StoryIdSchema()
news_pagination_schema = NewsPaginationSchema()


class UsersResource(Resource):
    @classmethod
    def get(cls):
        """
        Getting GET requests on the '/api/users' endpoint, and returning a list
        with all users in database.
        """
        users = UserModel.query.all()
        if not users:
            UserModel.session.close()
            return make_response(
                jsonify({"message": "users not found", "code": 404}), 404
            )
        UserModel.session.close()
        return users_schema.dump(users)

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
        user_username = UserModel.query.filter_by(
            username=user["username"]
        ).first()
        user_email = UserModel.query.filter_by(
            email_address=user["email_address"]
        ).first()
        if user_username:
            UserModel.session.close()
            return make_response(
                jsonify(
                    {
                        "message": "User with this username already exist"
                    }
                ), 400
            )
        if user_email:
            UserModel.session.close()
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
                UserModel.session.add(UserModel(**user))
                UserModel.session.commit()
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
    def get(cls, username):
        """
        Getting GET requests on the '/api/users/<username>' endpoint, and
        returning the user from the database.
        """
        try:
            username = {"username": username}
            incoming_username = username_schema.load(username)
        except ValidationError as err:
            return err.messages, 400
        user = UserModel.query.filter(
            UserModel.username == incoming_username['username']
        ).first()
        if not user:
            UserModel.session.close()
            return make_response(
                jsonify({"message": "user not found", "code": 404}), 404
            )
        UserModel.session.close()
        return make_response(
            jsonify(user_register_schema.dump(user))
        )

    @classmethod
    def patch(cls, username):
        """
        Getting PATCH requests on the '/api/users/<username>' endpoint, and
        updating the user data in the database.
        """
        try:
            username = {"username": username}
            incoming_username = username_schema.load(username)
        except ValidationError as err:
            return err.messages, 400
        try:
            incoming_user = user_password_schema.load(request.get_json())
        except ValidationError as err:
            return err.messages, 400
        user = UserModel.query.filter(
            UserModel.username == incoming_username['username']
        ).first()
        if not user:
            UserModel.session.close()
            return make_response(
                jsonify({"message": "user not found", "code": 404}), 404
            )
        UserModel.query.filter(
            UserModel.user_uuid == incoming_username['username']
        ).update(
            {
                "password": argon2.hash(incoming_user["password"])
            }
        )
        UserModel.session.commit()
        return make_response(
            jsonify(
                {
                    "message": "User credentials succesfully updated",
                    "code": 200
                }
            ), 200
        )

    @classmethod
    def delete(cls, username):
        """
        Getting DELETE requests on the '/api/users/<user_uuid>' endpoint, and
        deleting the user in the database.
        """
        try:
            username = {"username": username}
            incoming_username = username_schema.load(username)
        except ValidationError as err:
            return err.messages, 400
        user = UserModel.query.filter(
            UserModel.username == incoming_username['username']
        ).first()
        if not user:
            UserModel.session.close()
            return make_response(
                jsonify({"message": "user not found", "code": 404}), 404
            )
        UserModel.session.delete(user)
        UserModel.session.commit()
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
                UserModel.session.close()
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
            UserModel.session.close()
            return make_response(
                jsonify({"message": "Username or password Incorect!"}), 400
            )
        elif db_email_address:
            if argon2.verify(
                incoming_user["password"],
                db_email_address.password
            ):
                UserModel.session.close()
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
            UserModel.session.close()
            return make_response(
                jsonify(
                    {
                        "message": "Email address or password Incorect!"
                    }
                ), 400
            )
        else:
            UserModel.session.close()
            return make_response(
                jsonify(
                    {
                        "message": "Username or Email address not found."
                    }
                ), 400
            )


class UserStories(Resource):
    @classmethod
    def get(cls, username):
        """
        Getting GET requests on the
        '/api/users/<username>/stories/?pagenumber=N' endpoint,
        and returning up to 500 user`s stories
        """
        try:
            pagenumber = {"pagenumber": request.args.get("pagenumber")}
            incoming_pagination = news_pagination_schema.load(pagenumber)
        except ValidationError as err:
            return err.messages, 400
        if incoming_pagination["pagenumber"] <= 0:
            return make_response(
                jsonify(
                    {
                        "message": "pagenumber must be greater then 0",
                        "code": 400
                    }
                ),
                400,
            )
        try:
            username = {"username": username}
            incoming_username = username_schema.load(username)
        except ValidationError as err:
            return err.messages, 400
        users_stories = BlogNewsStory.query.filter(
            BlogNewsStory.by == incoming_username['username']
        ).all()
        if not users_stories:
            BlogNewsStory.session.close()
            return make_response(
                jsonify(
                    {'message': 'stories not found', 'code': 404}
                ), 404
            )
        page = paginate(
            BlogNewsStory.query.filter(
                BlogNewsStory.by == incoming_username['username']
            ).order_by(desc(BlogNewsStory.time))
            .limit(500)
            .from_self(),
            incoming_pagination["pagenumber"],
            30,
        )
        result_page = {
            "current_page": incoming_pagination["pagenumber"],
            "has_next": page.has_next,
            "has_previous": page.has_previous,
            "items": blognews_stories_schema.dump(page.items),
            "next_page": page.next_page,
            "previous_page": page.previous_page,
            "pages": page.pages,
            "total": page.total,
        }
        if incoming_pagination["pagenumber"] > result_page["pages"]:
            BlogNewsStory.session.close()
            return make_response(
                jsonify(
                    {
                        "message": "Pagination page not found",
                        "code": 404
                    }
                ), 404,
            )
        BlogNewsStory.session.close()
        return jsonify(result_page)


class UserStory(Resource):
    @classmethod
    def get(cls, username, story_id):
        """
        Getting GET requests on the
        '/api/users/<username>/stories/<story_id>' endpoint,
        and returning user`s story by story id
        """
        try:
            username = {"username": username}
            incoming_username = username_schema.load(username)
        except ValidationError as err:
            return err.messages, 400
        try:
            story_id = {"story_id": story_id}
            incoming_story_id = story_id_schema.load(story_id)
        except ValidationError as err:
            return err.messages, 400
        user_story = BlogNewsStory.query.filter(
            BlogNewsStory.by == incoming_username['username']
        ).filter(
            BlogNewsStory.id == incoming_story_id['story_id']
        ).first()
        if not user_story:
            BlogNewsStory.session.close()
            return make_response(
                jsonify(
                    {'message': 'story not found', 'code': 404}
                ), 404
            )
        BlogNewsStory.session.close()
        return jsonify(blognews_story_schema.dump(user_story))


class UserComments(Resource):
    @classmethod
    def get(cls, username):
        """
        Getting GET requests on the
        '/api/users/<username>/comments/?pagenumber=N' endpoint,
        and returning up to 500 user' comments
        """
        try:
            pagenumber = {"pagenumber": request.args.get("pagenumber")}
            incoming_pagination = news_pagination_schema.load(pagenumber)
        except ValidationError as err:
            return err.messages, 400
        if incoming_pagination["pagenumber"] <= 0:
            return make_response(
                jsonify(
                    {
                        "message": "pagenumber must be greater then 0",
                        "code": 400
                    }
                ),
                400,
            )
        try:
            username = {"username": username}
            incoming_username = username_schema.load(username)
        except ValidationError as err:
            return err.messages, 400
        users_comments = BlogNewsStoryComment.query.filter(
            BlogNewsStoryComment.by == incoming_username['username']
        ).all()
        if not users_comments:
            BlogNewsStoryComment.session.close()
            return make_response(
                jsonify(
                    {'message': 'comments not found', 'code': 404}
                ), 404
            )
        page = paginate(
            BlogNewsStoryComment.query.filter(
                BlogNewsStoryComment.by == incoming_username['username']
            ).order_by(desc(BlogNewsStoryComment.time))
            .limit(500)
            .from_self(),
            incoming_pagination["pagenumber"],
            30,
        )
        result_page = {
            "current_page": incoming_pagination["pagenumber"],
            "has_next": page.has_next,
            "has_previous": page.has_previous,
            "items": blognews_stories_schema.dump(page.items),
            "next_page": page.next_page,
            "previous_page": page.previous_page,
            "pages": page.pages,
            "total": page.total,
        }
        if incoming_pagination["pagenumber"] > result_page["pages"]:
            BlogNewsStoryComment.session.close()
            return make_response(
                jsonify(
                    {
                        "message": "Pagination page not found",
                        "code": 404
                    }
                ), 404,
            )
        BlogNewsStoryComment.session.close()
        return jsonify(result_page)
