from flask import request, jsonify, make_response, jsonify
from flask_restful import Resource
from api.models.hn_db import HackerNews_TopStories
from api.schemas.hacker_news import HackerNews_TopStories_Schema

top_stories_schema = HackerNews_TopStories_Schema(many=True)
from sqlalchemy import desc

class HackerNews_TopStories_Resourse(Resource):
    @classmethod
    def get(cls):
        """
        Getting GET requests on the '/api/hacker_news/top_stories' 
        endpoint, and returning a list
        with all hacker_news top_stories in database.
        """
        if not HackerNews_TopStories.query.all():
            return {"message": "No top_stories in this table"}
        return jsonify(
            {"message": top_stories_schema.dump(
                HackerNews_TopStories.query.order_by(desc(HackerNews_TopStories.parse_dt)).all()
                )}
        )
