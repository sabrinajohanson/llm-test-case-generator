import os
import json
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables from .env file
load_dotenv()

# Initialize the OpenAI client using the API key from .env
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def read_feature_file(path: str) -> str:
    """Reads the feature description from a text file."""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def build_prompt(feature_description: str) -> str:
    """Builds the instruction prompt sent to the LLM."""
    return f"""You are a senior QA engineer generating structured test cases
from a feature description.

Feature description:
\"\"\"
{feature_description}
\"\"\"

Generate test cases covering ALL of the following test layers:
- unit
- integration
- e2e

For each test layer, include positive, negative, and edge_case scenarios
where relevant. If a specific detail required for an "integration" test case
cannot be determined from the feature description alone (e.g. a specific
endpoint, request/response contract, or service name), use the placeholder
"TBD" for that detail instead of guessing or inventing it.

Return ONLY a valid JSON object (no markdown, no code fences, no extra text)
matching exactly this schema:

{{
  "test_cases": [
    {{
      "id": "TC-001",
      "title": "string",
      "description": "string",
      "type": "positive | negative | edge_case",
      "layer": "unit | integration | e2e",
      "priority": "high | medium | low",
      "steps": ["string", "string"],
      "expected_result": "string"
    }}
  ]
}}
"""

def generate_test_cases(feature_description: str) -> dict:
    """Sends the prompt to the OpenAI API and returns the parsed JSON response."""
    prompt = build_prompt(feature_description)

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.2,
    )

    raw_content = response.choices[0].message.content

    try:
        return json.loads(raw_content)
    except json.JSONDecodeError as e:
        print("Failed to parse JSON response from the model.")
        print("Raw response was:\n", raw_content)
        raise e
    
if __name__ == "__main__":
    feature_text = read_feature_file("examples/sample_feature.txt")
    result = generate_test_cases(feature_text)

    output_path = "output/generated_test_cases.json"
    os.makedirs("output", exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"Test cases generated and saved to {output_path}")