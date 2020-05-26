from marshmallow import Schema, fields, validate


class HackerNews_TopStories_Schema(Schema):
    id = fields.Str()
    #
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
