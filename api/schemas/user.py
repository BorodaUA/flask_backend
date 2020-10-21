from marshmallow import Schema, fields, validate


class UserUuidSchema(Schema):
    user_uuid = fields.Str(
        required=True,
        validate=[
            validate.Length(min=2, max=40)
        ]
    )


class UserPasswordUpdateSchema(Schema):
    password = fields.Str(
        required=True,
        validate=[
            validate.Length(min=6, max=32),
            validate.Regexp(regex=r"^[\b\w-]+$")
        ]
    )


class UserSchema(Schema):
    id = fields.Str()
    username = fields.Str(
        required=True,
        validate=[
            validate.Length(min=2, max=32),
            validate.Regexp(regex=r"^[\b\w-]+$")
        ]
    )
    password = fields.Str(
        required=True,
        validate=[
            validate.Length(min=6, max=32),
            validate.Regexp(regex=r"^[\b\w-]+$")
        ]
    )
    user_uuid = fields.Str()
    email_address = fields.Email(
        required=True,
        validate=validate.Length(min=3, max=256)
    )
    is_activated = fields.Bool()
    origin = fields.Str()


class UserSigninSchema(Schema):
    username = fields.Str(
        required=True,
        validate=[
            validate.Length(min=3, max=256),
        ]
    )
    email_address = fields.Str(
        required=True,
        validate=validate.Length(min=3, max=256)
    )
    password = fields.Str(
        required=True,
        validate=[
            validate.Length(min=6, max=32),
            validate.Regexp(regex=r"^[\b\w-]+$")
        ]
    )
