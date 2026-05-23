import pytest
from pymongo.errors import WriteError
from unittest.mock import patch

from src.util.dao import DAO


@pytest.fixture
def validator():
    return {
        "$jsonSchema": {
            "bsonType": "object",
            "required": ["firstName", "email"],
            "properties": {
                "firstName": {
                    "bsonType": "string"
                },
                "email": {
                    "bsonType": "string",
                    "uniqueItems": True
                },
                "isActive": {
                    "bsonType": "bool"
                }
            }
        }
    }


@pytest.fixture
def test_dao(validator):
    with patch("src.util.dao.getValidator", return_value=validator):
        dao = DAO("testing_integrtion")
        yield dao
        dao.drop()

#valid cases
@pytest.mark.integration
def test_create_valid_user(test_dao):
    data = {"firstName": "John", "email": "john@example.com", "isActive": True}

    result = test_dao.create(data)

    assert result["firstName"] == "John"
    assert result["email"] == "john@example.com"
    assert "_id" in result

#invalid cases
@pytest.mark.integration
@pytest.mark.parametrize(
    "data",
    [
        # Missing required fields
        {"email": "john@example.com", "isActive": False},
        {"firstName": "John", "isActive": True},

        # Wrong field types
        {"firstName": "John", "email": 123, "isActive": True},
        {"firstName": "John", "email": "john@example.com", "isActive": "invalidString"},
        {"firstName": 123, "email": "john@example.com", "isActive": True},
    ],
)
def test_create_invalid_users(test_dao, data):
    with pytest.raises(WriteError):
        test_dao.create(data)

#should give an error uniqueItem constrain on email: string
@pytest.mark.integration
def test_duplicate_email_should_fail(test_dao):
    data = {"firstName": "John", "email": "dup@example.com", "isActive": True}

    test_dao.create(data)

    with pytest.raises(WriteError):
        test_dao.create(data)
