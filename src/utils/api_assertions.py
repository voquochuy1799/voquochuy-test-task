from __future__ import annotations

from typing import Any, Mapping, Iterable

import pytest_check as check


def assert_status(resp, expected: int, msg: str | None = None):
    actual = getattr(resp, "status_code", None)
    text = getattr(resp, "text", "")
    default = f"Expected status {expected}, got {actual}. Body: {text[:500]}"
    check.equal(actual, expected, msg or default)


def assert_json_has_keys(resp, keys: Iterable[str]):
    try:
        data = resp.json()
    except Exception as e:
        check.is_true(False, f"Response is not JSON: {e}. Body: {getattr(resp, 'text', '')[:300]}")
        return
    for k in keys:
        check.is_true(k in data, f"Missing key '{k}' in JSON body. Body: {str(data)[:500]}")


def assert_json_field_equals(resp, field: str, expected: Any):
    try:
        data = resp.json()
    except Exception as e:
        check.is_true(False, f"Response is not JSON: {e}. Body: {getattr(resp, 'text', '')[:300]}")
        return
    actual = data.get(field)
    check.equal(actual, expected, f"Field '{field}' mismatch. Expected {expected}, got {actual}. Body: {str(data)[:500]}")


def assert_in_statuses(resp, allowed: Iterable[int]):
    actual = getattr(resp, "status_code", None)
    check.is_true(actual in allowed, f"Expected status in {list(allowed)}, got {actual}. Body: {getattr(resp, 'text', '')[:300]}")
