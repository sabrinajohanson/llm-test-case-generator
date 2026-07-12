# llm-test-case-generator

Generates structured test cases (unit, integration, and e2e) from a plain-text feature description, using the OpenAI API (GPT-4o).

## Tech Stack

- Python
- OpenAI API (`gpt-4o`)
- python-dotenv

## How It Works

1. A feature description is read from a `.txt` file (see `examples/sample_feature.txt`).
2. The description is sent to the OpenAI API with a structured prompt instructing the model to generate test cases across three layers (`unit`, `integration`, `e2e`) and three types (`positive`, `negative`, `edge_case`).
3. The model returns a structured JSON object containing the generated test cases.
4. The result is saved to `output/generated_test_cases.json`.

Each test case includes: `id`, `title`, `description`, `type`, `layer`, `priority`, `steps`, and `expected_result`.

## Setup

1. Clone this repository.
2. Create a virtual environment and activate it.
3. Install dependencies: pip install -r requirements.txt
4. Create a `.env` file in the project root with your OpenAI API key: OPENAI_API_KEY=your_key_here
5. Run the generator: python main.py

## Prompt Iteration & Findings

This project was built iteratively, evaluating each output as a QA engineer would rather than accepting the first result. Three issues were identified and addressed through prompt refinement:

**1. "TBD" placeholder not being used explicitly**
The initial prompt asked the model to use the literal string `"TBD"` when a technical detail (e.g. an endpoint or status code) couldn't be determined from the feature description. In practice, the model avoided inventing details, but also avoided writing `"TBD"` - it simply described the check vaguely instead.
*Fix:* Added a concrete few-shot example showing the exact expected format, with `"TBD"` embedded directly in a step. This resolved the issue completely.

**2. Inconsistent unit vs. integration classification**
The model tended to under-classify test cases as `unit` when they actually involved multiple components (e.g. cart + checkout).
*Fix:* Added explicit, objective criteria for each layer (`unit`, `integration`, `e2e`) directly in the prompt. This significantly improved classification, but did not fully resolve it - some edge cases were still inconsistently classified depending on whether the test was framed as a success or a failure scenario.

**3. Type (positive/negative/edge_case) influencing layer classification**
Following up on issue #2, it was observed that negative/edge_case tests involving multiple components were still sometimes classified as `unit`, even when the equivalent positive test was correctly classified as `integration`.
*Fix:* Added an explicit rule stating that test type does not affect layer classification, plus a second few-shot example showing an `edge_case` correctly classified as `integration`. This further reduced misclassification.

**Takeaway:** prompt refinement improved reliability substantially, but did not achieve 100% consistency for the layer classification problem - unlike the `"TBD"` issue, which was fully resolved. This reflects a real limitation of prompt-based control over LLM outputs: some rules are objective and easy to enforce, while others involve inherently fuzzy judgment calls, even for the model.

## Example Output

See [`examples/sample_output.json`](./examples/sample_output.json) for a real, unedited output generated from [`examples/sample_feature.txt`](./examples/sample_feature.txt).

## Known Limitations

- Test case classification (`unit` vs `integration`) is not 100% consistent across positive vs. negative/edge_case variants of similar scenarios.
- The model is called with `temperature=0.2` to reduce variability, but outputs are not guaranteed to be identical across runs.
- Integration test details marked as `"TBD"` require manual completion once the actual system/API implementation exists.