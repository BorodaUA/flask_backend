from marshmallow import Schema, fields, validate


class PageNumberSchema(Schema):
    pagenumber = fields.Int(required=True)


class StoryIdSchema(Schema):
    story_id = fields.Int(required=True)


class CommentIdSchema(Schema):
    comment_id = fields.Int(required=True)


class HackerNewsCommentSchema(Schema):
    id = fields.Str()
    hn_id = fields.Str()
    deleted = fields.Bool()
    type = fields.Str()
    by = fields.Str()
    time = fields.Int()
    text = fields.Str()
    dead = fields.Bool()
    parent = fields.Int()
    poll = fields.Int()
    kids = fields.List(fields.Int())
    url = fields.Str()
    score = fields.Int()
    title = fields.Str()
    parts = fields.List(fields.Int())
    descendants = fields.Int()
    origin = fields.Str()
    parsed_time = fields.DateTime()


class HackerNewsStorySchema(Schema):
    id = fields.Str()
    hn_id = fields.Int()
    deleted = fields.Bool()
    type = fields.Str()
    by = fields.Str(
        required=True,
        validate=validate.Length(min=1)
    )
    time = fields.Int()
    text = fields.Str(
        required=True,
        validate=validate.Length(min=1)
    )
    dead = fields.Bool()
    parent = fields.Int()
    poll = fields.Int()
    kids = fields.List(fields.Int())
    url = fields.Str()
    score = fields.Int()
    title = fields.Str()
    parts = fields.List(fields.Int())
    descendants = fields.Int()
    comments = fields.Nested(HackerNewsCommentSchema(many=True))
    #
    origin = fields.Str()
    parsed_time = fields.DateTime()
    updated_time = fields.DateTime()
