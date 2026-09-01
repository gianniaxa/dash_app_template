---
name: dash-run-tests
description: Use when running, debugging, or writing pytest tests for this project. Covers how to run unit tests and integration tests, the mongomock setup, available fixtures, and where test files live.
---

# Running and Writing Tests

## Test location

```
src/tests/
├── conftest.py                  # Shared fixtures (mongomock)
├── test_data_loader.py          # Unit tests for utils/data_loader.py
└── test_mongo_integration.py    # Integration tests with mongomock
```

## Running tests

```bash
cd src
uv run pytest tests/ -v
```

Run a single file:
```bash
uv run pytest tests/test_data_loader.py -v
```

Run a single test:
```bash
uv run pytest tests/test_data_loader.py::TestLoadCsv::test_returns_list_of_dicts_by_default -v
```

## Available fixtures (from conftest.py)

| Fixture | Description |
|---|---|
| `mongo_client` | In-memory mongomock MongoClient |
| `users_collection` | `mongo_client["testdb"]["users"]` pre-seeded with 3 users |

## Unit test pattern

```python
class TestMyUtil:

    def test_something(self, tmp_path):
        # Use tmp_path for file operations
        ...

    def test_raises_on_invalid_input(self):
        with pytest.raises(ValueError):
            my_function(invalid_input)
```

## Integration test pattern (mongomock)

```python
class TestMyCollection:

    def test_insert(self, users_collection):
        users_collection.insert_one({"name": "Test"})
        assert users_collection.count_documents({}) == 4  # 3 seeded + 1

    def test_find(self, mongo_client):
        db = mongo_client["testdb"]
        col = db["products"]
        col.insert_one({"name": "Widget", "price": 9.99})
        result = col.find_one({"name": "Widget"})
        assert result["price"] == 9.99
```

## Adding new fixtures

Add to `src/tests/conftest.py`:

```python
@pytest.fixture
def my_collection(mongo_client):
    db = mongo_client["testdb"]
    collection = db["my_collection"]
    collection.insert_many([...])
    return collection
```

## Dev dependencies

`pytest`, `mongomock`, and `pymongo` are defined under `[dependency-groups] dev` in `src/pyproject.toml`.

Install with:
```bash
cd src
uv sync --group dev
```
