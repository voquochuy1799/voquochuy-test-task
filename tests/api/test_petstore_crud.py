from __future__ import annotations

import random
import string
import time
import pytest
import allure


def _rand_name(prefix: str = "pet") -> str:
    return f"{prefix}-" + "".join(random.choices(string.ascii_lowercase + string.digits, k=6))


@allure.feature("Petstore API")
@pytest.mark.api
@pytest.mark.smoke
def test_create_pet_happy(api_client):
    pet_id = random.randint(1000000, 9999999)
    payload = {
        "id": pet_id,
        "name": _rand_name(),
        "status": "available",
    }
    resp = api_client.post("/pet", json=payload)
    assert resp.status_code in (200, 201)
    body = resp.json()
    assert body["id"] == pet_id
    assert body["name"] == payload["name"]


@allure.feature("Petstore API")
@pytest.mark.api
@pytest.mark.smoke
def test_get_pet_happy(api_client):
    # Create first
    pet_id = random.randint(1000000, 9999999)
    payload = {"id": pet_id, "name": _rand_name(), "status": "available"}
    r = api_client.post("/pet", json=payload)
    assert r.status_code in (200, 201)
    body = r.json()
    got_id = body.get("id", pet_id)
    # small retry for eventual consistency
    for _ in range(3):
        resp = api_client.get(f"/pet/{got_id}")
        if resp.status_code == 200:
            break
        time.sleep(0.5)
    assert resp.status_code == 200
    assert resp.json()["id"] == got_id


@allure.feature("Petstore API")
@pytest.mark.api
@pytest.mark.smoke
def test_update_pet_happy(api_client):
    pet_id = random.randint(1000000, 9999999)
    payload = {"id": pet_id, "name": _rand_name(), "status": "available"}
    r = api_client.post("/pet", json=payload)
    assert r.status_code in (200, 201)
    update_payload = {"id": pet_id, "name": _rand_name("updated"), "status": "pending"}
    resp = api_client.put("/pet", json=update_payload)
    assert resp.status_code in (200, 201)
    assert resp.json()["status"] == "pending"


@allure.feature("Petstore API")
@pytest.mark.api
@pytest.mark.smoke
def test_delete_pet_happy(api_client):
    pet_id = random.randint(1000000, 9999999)
    payload = {"id": pet_id, "name": _rand_name(), "status": "available"}
    r = api_client.post("/pet", json=payload)
    assert r.status_code in (200, 201)
    # ensure created before delete
    for _ in range(3):
        g = api_client.get(f"/pet/{pet_id}")
        if g.status_code == 200:
            break
        time.sleep(0.5)
    resp = api_client.delete(f"/pet/{pet_id}")
    assert resp.status_code in (200, 204, 404)
    # Confirm delete with small retry
    for _ in range(3):
        resp2 = api_client.get(f"/pet/{pet_id}")
        if resp2.status_code in (404, 400):
            break
        time.sleep(0.5)
    assert resp2.status_code in (404, 400)


@allure.feature("Petstore API")
@pytest.mark.api
def test_get_pet_not_found(api_client):
    resp = api_client.get("/pet/0")
    assert resp.status_code in (404, 400)


@allure.feature("Petstore API")
@pytest.mark.api
def test_create_pet_invalid_body(api_client):
    # Send wrong content-type to provoke error
    resp = api_client.session.post(api_client._url("/pet"), data="invalid", headers={"Content-Type": "text/plain"})
    assert resp.status_code in (400, 405, 415, 500)
