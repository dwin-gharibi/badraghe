import pytest
from fastapi import status
import pytest_asyncio
import os
import sys
from httpx import AsyncClient

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from main import app

test_user_id = None

@pytest_asyncio.fixture(scope="session")
async def admin_token():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/token",
            data={
                "username": "dwin@dwin.codes",
                "password": "password"
            }
        )
        response.raise_for_status()
        return response.json()["access_token"]
    
@pytest.mark.asyncio
async def test_create_new_user():
    global test_user_id
    async with AsyncClient(app=app, base_url="http://test") as client:
        user_data = {
            "email": "testuser@example.com",
            "password": "testpassword",
            "first_name": "Test",
            "last_name": "User",
            "phone": "+989111111111"
        }
        response = await client.post("/signup", json=user_data)
        assert response.status_code == status.HTTP_200_OK
        user_id = response.json().get("user_id")
        assert user_id is not None, "User ID not returned"
        test_user_id = user_id
        return user_id


@pytest.mark.asyncio
async def test_get_user_profile(admin_token):
    global test_user_id
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get(
            f"/users/{test_user_id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == status.HTTP_200_OK
        user_data = response.json()
        assert "email" in user_data
        assert "first_name" in user_data

@pytest.mark.asyncio
async def test_update_user_profile(admin_token):
    global test_user_id
    async with AsyncClient(app=app, base_url="http://test") as client:
        update_data = {
            "first_name": "Updated",
            "last_name": "Name",
            "bio": "This is a test bio"
        }
        response = await client.put(
            f"/users/{test_user_id}",
            json=update_data,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == status.HTTP_200_OK
        updated_user = response.json()
        assert updated_user["first_name"] == "Updated"
        assert updated_user["bio"] == "This is a test bio"

@pytest.mark.asyncio
async def test_update_user_status(admin_token):
    global test_user_id
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.patch(
            f"/users/{test_user_id}/status",
            params={"user_status": False},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == status.HTTP_200_OK
        
        response = await client.patch(
            f"/users/{test_user_id}/status",
            params={"user_status": True},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == status.HTTP_200_OK

@pytest.mark.asyncio
async def test_get_user_roles(admin_token):
    global test_user_id
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get(
            f"/users/{test_user_id}/roles",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.json(), list)

@pytest.mark.asyncio
async def test_get_user_permissions(admin_token):
    global test_user_id
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get(
            f"/users/{test_user_id}/permissions",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.json(), list)

@pytest.mark.asyncio
async def test_delete_user(admin_token):
    global test_user_id
    async with AsyncClient(app=app, base_url="http://test") as client:
        
        response = await client.delete(
            f"/users/{test_user_id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == status.HTTP_200_OK
