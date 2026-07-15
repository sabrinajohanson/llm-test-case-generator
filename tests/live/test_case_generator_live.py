from generator import generate_test_cases

ALLOWED_TYPES = {"positive", "negative", "edge_case"}
ALLOWED_LAYERS = {"unit", "integration", "e2e"}
REQUIRED_FIELDS = {"id", "title", "description", "type", "layer", "priority", "steps", "expected_result"}


def test_generate_test_cases_real_api_contract():
    feature_description = "User can log in with a valid email and password."

    result = generate_test_cases(feature_description)

    assert "test_cases" in result
    assert len(result["test_cases"]) > 0

    for test_case in result["test_cases"]:
        # Every required field must be present
        missing_fields = REQUIRED_FIELDS - test_case.keys()
        assert not missing_fields, f"Missing fields: {missing_fields}"
        assert test_case["type"] in ALLOWED_TYPES
        assert test_case["layer"] in ALLOWED_LAYERS
        assert isinstance(test_case["steps"], list)
        assert len(test_case["steps"]) > 0