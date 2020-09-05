from marshmallow import Schema, fields, validate


class UserSchema(Schema):
    id = fields.Str()
    username = fields.Str(
        required=True,
        validate=validate.Length(min=3, max=128)
    )
    password = fields.Str(
        required=True,
        validate=validate.Length(min=3, max=128)
    )
    user_uuid = fields.Str()
    email_address = fields.Str(
        required=True,
        validate=validate.Length(min=3, max=128)
    )
    is_activated = fields.Bool()
    origin = fields.Str()
