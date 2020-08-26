from marshmallow import Schema, fields, validate


# class Comments_Schema(Schema):
#     id = fields.Int()
#     parse_dt = fields.DateTime()
#     by = fields.Str()
#     deleted = fields.Bool()
#     comment_id = fields.Int()
#     kids = fields.List(fields.Int())
#     parent = fields.Int()
#     text = fields.Str()
#     time = fields.Int()
#     comment_type = fields.Str()
#     origin = fields.Str()


class NewsPaginationSchema(Schema):
    pagenumber = fields.Int(required=True)


class StoryIdSchema(Schema):
    story_id = fields.Int(required=True)

class BlogNewsCommentSchema(Schema):
    id = fields.Str()
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


class BlogNewsStorySchema(Schema):
    id = fields.Str()
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
    comments = fields.Nested(BlogNewsCommentSchema(many=True))
    #
    origin = fields.Str()


# class Add_Comment_Schema(Schema):
#     parse_dt = fields.DateTime()
#     by = fields.Str()
#     deleted = fields.Bool()
#     existed_comment_id = fields.Int()
#     comment_id = fields.Int()
#     kids = fields.List(fields.Int())
#     parent = fields.Int()
#     existed_comment_text = fields.Str()
#     text = fields.Str()
#     time = fields.Int()
#     comment_type = fields.Str()
#     origin = fields.Str()
