import pytest

from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

@pytest.fixture(scope="module")
def auth_headers():
    return {"Authorization": "Basic YWRtaW46YWRtaW4xMjM="}  # admin:admin123 in base64

def test_list_users_unauthorized():
    response = client.get("/users/")
    assert response.status_code == 401

def test_list_users_success(auth_headers):
    response = client.get("/users/", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert all("login" in u and "id" in u for u in data)

@pytest.mark.parametrize("login", ["mojombo", "defunkt", "nonexistentuser"])
def test_get_user(auth_headers, login):
    response = client.get(f"/users/{login}", headers=auth_headers)
    if login == "nonexistentuser":
        assert response.status_code == 404
    else:
        assert response.status_code == 200
        u = response.json()
        assert u["login"].lower() == login.lower()

@pytest.mark.parametrize("query,expected_min", [("mojo", 1), ("xyz", 0)])
def test_search_users(auth_headers, query, expected_min):
    response = client.get(f"/users/search?q={query}", headers=auth_headers)
    assert response.status_code == 200
    results = response.json()
    assert isinstance(results, list)
    assert len(results) >= expected_min
