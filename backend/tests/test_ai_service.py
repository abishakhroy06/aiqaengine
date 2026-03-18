import json
import pytest
from unittest.mock import patch
from app.services.ai_service import generate_qa_output
from app.services.qa_prompt import (
    build_enumeration_system_prompt,
    build_enumeration_user_prompt,
    build_coverage_system_prompt,
    build_coverage_user_prompt,
    build_additional_tests_system_prompt,
    build_additional_tests_user_prompt,
)


def test_build_enumeration_system_prompt():
    prompt = build_enumeration_system_prompt()
    assert len(prompt) > 100


def test_build_enumeration_user_prompt():
    prompt = build_enumeration_user_prompt(
        requirement="User can login with email and password",
        context={"product": "Test App", "platform": "Web", "users_roles": "Admin, User"}
    )
    assert "User can login" in prompt
    assert "Test App" in prompt
    assert "Web" in prompt


def test_build_enumeration_user_prompt_empty_context():
    prompt = build_enumeration_user_prompt(requirement="User story", context={})
    assert "User story" in prompt


def test_build_coverage_system_prompt():
    prompt = build_coverage_system_prompt()
    assert len(prompt) > 100


def test_build_coverage_user_prompt():
    enumeration = {
        "functional": [{"reference_id": "F-001", "description": "Login with valid credentials"}],
        "validation": [],
        "data": [],
        "permission": [],
        "integration": [],
    }
    prompt = build_coverage_user_prompt(
        requirement="User can login",
        context={"product": "App"},
        enumeration=enumeration,
    )
    assert "login" in prompt.lower()


def test_build_additional_tests_system_prompt():
    prompt = build_additional_tests_system_prompt()
    assert len(prompt) > 100


def test_build_additional_tests_user_prompt():
    enumeration = {
        "functional": [{"reference_id": "F-001", "description": "Login"}],
        "validation": [],
        "data": [],
        "permission": [],
        "integration": [],
    }
    prompt = build_additional_tests_user_prompt(
        requirement="User can login",
        context={},
        enumeration=enumeration,
        positive=[],
        negative=[],
    )
    assert len(prompt) > 10


_ENUM_JSON = json.dumps({
    "functional": [{"reference_id": "F-001", "description": "Login with valid credentials"}],
    "validation": [],
    "data": [],
    "permission": [],
    "integration": [],
})

_COVERAGE_JSON = json.dumps({
    "positive": [
        {
            "test_id": "TC-POS-001",
            "reference_id": "F-001",
            "scenario": "Login with valid credentials",
            "requirement_ref": "F-001",
            "preconditions": "User is registered",
            "steps": "1. Enter email\n2. Enter password\n3. Click Submit",
            "test_data": "email: test@example.com",
            "expected_result": "User is logged in and redirected to dashboard",
            "priority": "P1",
            "notes": "",
        }
    ],
    "negative": [],
})

_ADDITIONAL_JSON = json.dumps({
    "boundary": [],
    "edge": [],
    "permission": [],
    "scenario_map": {
        "main_flows": ["Successful login flow"],
        "alternate_flows": [],
        "error_flows": ["Invalid credentials"],
        "permission_flows": [],
        "integration_flows": [],
    },
    "assumptions": ["User has a verified email"],
    "questions": ["Is there a lockout policy?"],
    "checklist_result": {
        "all_items_traced": "Pass",
        "positive_negative_coverage": "Pass",
        "boundary_coverage": "Pass",
        "edge_coverage": "Pass",
        "permission_coverage": "Pass",
        "integration_coverage": "Pass",
        "no_duplicates": "Pass",
        "clear_expected_results": "Pass",
        "no_hallucinated_rules": "Pass",
    },
})


def _make_sequential_side_effect(*responses):
    """Return a side_effect function that yields responses in order."""
    it = iter(responses)
    def side_effect(system, user, max_tokens=4096):
        return next(it)
    return side_effect


def test_generate_qa_output_success():
    with patch(
        "app.services.ai_service._call_ai",
        side_effect=_make_sequential_side_effect(_ENUM_JSON, _COVERAGE_JSON, _ADDITIONAL_JSON),
    ):
        result = generate_qa_output(requirement="User can login", context={"product": "App"})

    assert "test_cases" in result
    assert "scenario_map" in result
    assert len(result["test_cases"]["positive"]) == 1
    assert result["test_cases"]["positive"][0]["test_id"] == "TC-POS-001"
    assert "checklist" in result


def test_generate_qa_output_invalid_coverage_json():
    with patch(
        "app.services.ai_service._call_ai",
        side_effect=_make_sequential_side_effect(_ENUM_JSON, "not valid json", "also not json"),
    ):
        with pytest.raises(ValueError):
            generate_qa_output(requirement="Test", context={})
