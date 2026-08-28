"""
pytest configuration and shared fixtures.

Fixtures defined here are available to all tests automatically.
"""

import pytest
import mongomock
import pymongo


@pytest.fixture
def mongo_client():
    """
    Returns a mongomock MongoClient that behaves like a real pymongo client
    but runs fully in-memory. No MongoDB installation required.

    Usage in tests:
        def test_something(mongo_client):
            db = mongo_client["testdb"]
            db["users"].insert_one({"name": "Alice"})
    """
    with mongomock.patch(servers=(("localhost", 27017),)):
        client = pymongo.MongoClient("localhost", 27017)
        yield client
        client.drop_database("testdb")


@pytest.fixture
def users_collection(mongo_client):
    """
    Returns a fresh 'users' collection pre-seeded with sample data.
    """
    db = mongo_client["testdb"]
    collection = db["users"]
    collection.insert_many([
        {"name": "Alice", "nationality": "German",  "email": "alice@example.com", "birthday": "1990-03-15"},
        {"name": "Bob",   "nationality": "Swiss",   "email": "bob@example.com",   "birthday": "1985-07-22"},
        {"name": "Clara", "nationality": "Austrian","email": "clara@example.com", "birthday": "1992-11-08"},
    ])
    return collection
