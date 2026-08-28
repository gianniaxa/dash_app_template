"""
Integration tests using mongomock.

These tests simulate interactions with a MongoDB database without requiring
a running MongoDB instance. mongomock patches pymongo in-memory.

Fixtures (mongo_client, users_collection) are defined in conftest.py.
"""


class TestUserCollection:

    def test_find_all_users(self, users_collection):
        results = list(users_collection.find())
        assert len(results) == 3

    def test_find_user_by_name(self, users_collection):
        user = users_collection.find_one({"name": "Alice"})
        assert user is not None
        assert user["nationality"] == "German"

    def test_insert_new_user(self, users_collection):
        users_collection.insert_one({
            "name": "David",
            "nationality": "Italian",
            "email": "david@example.com",
            "birthday": "1988-01-30",
        })
        assert users_collection.count_documents({}) == 4

    def test_update_user_email(self, users_collection):
        users_collection.update_one(
            {"name": "Bob"},
            {"$set": {"email": "bob.new@example.com"}},
        )
        updated = users_collection.find_one({"name": "Bob"})
        assert updated["email"] == "bob.new@example.com"

    def test_delete_user(self, users_collection):
        users_collection.delete_one({"name": "Clara"})
        assert users_collection.count_documents({}) == 2
        assert users_collection.find_one({"name": "Clara"}) is None

    def test_filter_by_nationality(self, users_collection):
        results = list(users_collection.find({"nationality": "German"}))
        assert len(results) == 1
        assert results[0]["name"] == "Alice"
