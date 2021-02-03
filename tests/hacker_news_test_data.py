from faker import Faker
import random


def generate_test_data():
    '''
    return Faker's test data
    '''
    fake = Faker()
    fake_user = fake.profile()
    fake_user['password'] = fake.password(
        length=random.randrange(6, 32)
    )
    return fake_user


test_row = {
    "by": generate_test_data()['username'],
    "dead": None,
    "deleted": None,
    "descendants": 328,
    "hn_id": 24611558,
    "id": "2402",
    "kids": [
        24611767,
        24611659,
        24612195,
        24612606,
        24611805,
    ],
    "origin": "hacker_news",
    "parent": None,
    "parsed_time": "2020-09-28T08:20:23.918000",
    "parts": None,
    "poll": None,
    "score": 207,
    "text": None,
    "time": 1601253055,
    "title": generate_test_data()['residence'],
    "type": "story",
    "url": generate_test_data()['website'][0]
}
