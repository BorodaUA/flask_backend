from marshmallow import Schema, fields, validate


class PaginationSchema(Schema):
    pagenumber = fields.Int(required=True)


class StorySchema(Schema):
    story_id = fields.Int(required=True)


class CommentIdSchema(Schema):
    comment_id = fields.Int(required=True)


class HackerNewsCommentSchema(Schema):
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
    parsed_time = fields.DateTime()


class Add_Comment_Schema(Schema):
    parsed_time = fields.DateTime()
    by = fields.Str()
    deleted = fields.Bool()
    existed_comment_id = fields.Int()
    id = fields.Int()
    kids = fields.List(fields.Int())
    parent = fields.Int()
    existed_comment_text = fields.Str()
    text = fields.Str()
    time = fields.Int()
    type = fields.Str()
    origin = fields.Str()


class HackerNewsTopStorySchema(Schema):
    id = fields.Str()
    hn_id = fields.Int()
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
    comments = fields.Nested(HackerNewsCommentSchema(many=True))
    #
    origin = fields.Str()
    parsed_time = fields.DateTime()


class HackerNews_NewStories_Schema(Schema):
    id = fields.Str()
    parse_dt = fields.DateTime()
    #
    hn_url = fields.Str()
    #
    item_id = fields.Int()
    deleted = fields.Bool()
    item_type = fields.Str()
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
    comments = fields.Nested(HackerNewsCommentSchema(many=True))
    origin = fields.Str()
