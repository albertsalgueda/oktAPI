import pytest
from models.user import UserIn
def test_user_exists():
    with pytest.raises(ValueError):
        UserIn(username="admin", password="thisisapassword", scopes=["read"])


def test_password_small():
    with pytest.raises(ValueError):
        UserIn(username="newuser", password="small", scopes=["read"])

def test_valid_user_in():
    assert UserIn(username="newuser", password="notsmall", scopes=["read"])