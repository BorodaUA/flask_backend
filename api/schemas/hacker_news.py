from marshmallow import Schema, fields, validate


class NewsPagination_Schema(Schema):
    page_number = fields.Int()


class Story_id_Schema(Schema):
    story_id = fields.Int()


class Comments_Schema(Schema):
    id = fields.Int()
    parse_dt = fields.DateTime()
    by = fields.Str()
    deleted = fields.Bool()
    comment_id = fields.Int()
    kids = fields.List(fields.Int())
    parent = fields.Int()
    text = fields.Str()
    time = fields.Int()
    comment_type = fields.Str()


class HackerNews_TopStories_Schema(Schema):
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
    comments = fields.Nested(Comments_Schema(many=True))


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
    comments = fields.Nested(Comments_Schema(many=True))
