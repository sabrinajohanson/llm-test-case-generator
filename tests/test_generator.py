import json
import pytest
from unittest.mock import patch, MagicMock
from generator import read_feature_file, build_prompt, generate_test_cases

def test_read_feature_file(tmp_path):
    # Arrange: create a temporary file with known content
    feature_file = tmp_path / "sample_feature.txt"
    feature_file.write_text("User can log in with email and password.", encoding="utf-8")

    # Act: call the real function
    result = read_feature_file(str(feature_file))

    # Assert: confirm the content read matches exactly what we wrote
    assert result == "User can log in with email and password."

def test_build_prompt_contains_feature_description():
    # Arrange
    feature_description = "User can log in with email and password."

    # Act: call the real function
    prompt = build_prompt(feature_description)

    # Assert: confirm the feature description is embedded in the generated prompt
    assert feature_description in prompt

def test_generate_test_cases_success():
    # Arrange: build a fake OpenAI response object matching the real shape
    fake_json_response = json.dumps({
        "test_cases": [
            {
                "id": "TC-001",
                "title": "Valid login",
                "description": "Verifies successful login with valid credentials.",
                "type": "positive",
                "layer": "unit",
                "priority": "high",
                "steps": ["Enter valid email.", "Enter valid password.", "Submit form."],
                "expected_result": "User is logged in successfully."
            }
        ]
    })

    mock_response = MagicMock()
    mock_response.choices[0].message.content = fake_json_response

    # Act: patch only the API call, everything else in the function runs for real
    with patch("generator.client.chat.completions.create", return_value=mock_response):
        result = generate_test_cases("User can log in with email and password.")

    # Assert: confirm the real json.loads correctly parsed the mocked content
    assert result["test_cases"][0]["id"] == "TC-001"
    assert result["test_cases"][0]["layer"] == "unit"

def test_generate_test_cases_invalid_json():
    # Arrange: simulate the API returning a malformed, non-JSON response
    mock_response = MagicMock()
    mock_response.choices[0].message.content = "This is not valid JSON"

    # Act & Assert: confirm the function raises JSONDecodeError instead of failing silently
    with patch("generator.client.chat.completions.create", return_value=mock_response):
        with pytest.raises(json.JSONDecodeError):
            generate_test_cases("User can log in with email and password.")