from __future__ import annotations

import random
import string
import time
import pytest
import allure

from src.utils.api_assertions import (
    assert_status,
    assert_json_field_equals,
    assert_json_has_keys,
)


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
    assert_status(resp, 200, "Create pet should return 200")
    assert_json_has_keys(resp, ["id", "name", "status"])
    assert_json_field_equals(resp, "id", pet_id)
    assert_json_field_equals(resp, "name", payload["name"])


@allure.feature("Petstore API")
@pytest.mark.api
@pytest.mark.smoke
def test_get_pet_happy(api_client):
    # Create first
    pet_id = random.randint(1000000, 9999999)
    payload = {"id": pet_id, "name": _rand_name(), "status": "available"}
    r = api_client.post("/pet", json=payload)
    assert_status(r, 200, "Create before get should succeed")
    assert_json_has_keys(r, ["id", "name", "status"])
    body = r.json()
    got_id = body.get("id", pet_id)
    # small retry for eventual consistency
    for _ in range(3):
        resp = api_client.get(f"/pet/{got_id}")
        if resp.status_code == 200:
            break
        time.sleep(0.5)
    assert_status(resp, 200, "Get pet should return 200 after creation")
    assert_json_field_equals(resp, "id", got_id)


@allure.feature("Petstore API")
@pytest.mark.api
@pytest.mark.smoke
def test_update_pet_happy(api_client):
    pet_id = random.randint(1000000, 9999999)
    payload = {"id": pet_id, "name": _rand_name(), "status": "available"}
    r = api_client.post("/pet", json=payload)
    assert_status(r, 200, "Create before update should succeed")
    update_payload = {"id": pet_id, "name": _rand_name("updated"), "status": "pending"}
    resp = api_client.put("/pet", json=update_payload)
    assert_status(resp, 200, "Update pet should be 200")
    assert_json_field_equals(resp, "status", "pending")


@allure.feature("Petstore API")
@pytest.mark.api
@pytest.mark.smoke
def test_delete_pet_happy(api_client):
    pet_id = random.randint(1000000, 9999999)
    payload = {"id": pet_id, "name": _rand_name(), "status": "available"}
    r = api_client.post("/pet", json=payload)
    assert_status(r, 200, "Create before delete should succeed")
    # ensure created before delete
    for _ in range(3):
        g = api_client.get(f"/pet/{pet_id}")
        if g.status_code == 200:
            break
        time.sleep(0.5)
    resp = api_client.delete(f"/pet/{pet_id}")
    assert_status(resp, 200, "Delete pet should return 200")
    # Confirm delete with small retry
    for _ in range(3):
        resp2 = api_client.get(f"/pet/{pet_id}")
        if resp2.status_code == 404:
            break
        time.sleep(0.5)
    # After deletion the expected status is 404 (not found). Some flaky gateways may return 400 briefly, but we require strict 404 now.
    assert_status(resp2, 404, "Deleted pet should return 404 on get")


@allure.feature("Petstore API")
@pytest.mark.api
def test_get_pet_not_found(api_client):
    resp = api_client.get("/pet/0")
    assert_status(resp, 404, "Non-existent pet should return 404")


@allure.feature("Petstore API")
@pytest.mark.api
def test_create_pet_invalid_body(api_client):
    # Send wrong content-type to provoke error; primary expected code is 400 (bad request)
    resp = api_client.session.post(api_client._url("/pet"), data="invalid", headers={"Content-Type": "text/plain"})
    assert_status(resp, 415, "Invalid body should return 415")
