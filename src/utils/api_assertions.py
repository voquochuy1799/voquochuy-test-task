from __future__ import annotations

from typing import Any, Iterable

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


# Previously we allowed asserting membership in a list of acceptable status codes.
# Simplified tests now require exact status codes, so the helper was removed for clarity.
