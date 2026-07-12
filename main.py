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

Generate test cases covering ALL of the following test layers. Use these strict criteria to decide which layer each test case belongs to:

- "unit": Tests a single function, rule, or piece of logic in isolation, without depending on other components, services, or persistence (e.g. validating an email format, checking a required field).
- "integration": Tests the interaction BETWEEN two or more components or services, such as the checkout flow calling an order confirmation service, or the cart communicating with a database/persistence layer. If a test case depends on more than one component working together, it MUST be
  classified as "integration", not "unit".
- "e2e": Tests a complete user journey through the system from start to finish, as the end user would experience it (e.g. logging in, adding products, and completing checkout in a single flow).

This layer classification rule applies regardless of whether the test case is "positive", "negative", or "edge_case" — the type of test does NOT change which layer it belongs to. A test case that checks an error or edge scenario involving multiple components (e.g. checkout blocked due to an empty cart) is still "integration", not "unit", for the same reason a successful case involving those same components would be.

For each test layer, include positive, negative, and edge_case scenarios where relevant. If a specific detail required for an "integration" test case cannot be determined from the feature description alone (e.g. a specific endpoint, request/response contract, or service name), you MUST use the
literal placeholder string "TBD" for that detail instead of guessing,inventing, or describing it vaguely.

Example of a correctly written integration test case, where the endpoint and expected status code are not specified in the feature description:

{{
  "id": "TC-EXAMPLE",
  "title": "Order confirmation service integration",
  "description": "Verifies that the checkout flow correctly calls the order confirmation service.",
  "type": "positive",
  "layer": "integration",
  "priority": "high",
  "steps": [
    "Submit a valid checkout request.",
    "Call the order confirmation service endpoint: TBD.",
    "Verify the service responds with status code: TBD."
  ],
  "expected_result": "Order confirmation service returns a success response: TBD."
}}

Example of an edge_case that is still classified as "integration" because it involves interaction between multiple components (cart and checkout):

{{
  "id": "TC-EXAMPLE-2",
  "title": "Checkout blocked with empty cart",
  "description": "Verifies that checkout cannot proceed when the cart has no items, which requires the cart and checkout components to interact.",
  "type": "edge_case",
  "layer": "integration",
  "priority": "medium",
  "steps": [
    "Ensure the shopping cart is empty.",
    "Attempt to submit a checkout request."
  ],
  "expected_result": "Checkout is blocked and the system returns an error indicating the cart is empty."
}}

Return ONLY a valid JSON object (no markdown, no code fences, no extra text) matching exactly this schema:

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