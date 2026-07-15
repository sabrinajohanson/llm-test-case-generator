import os
import json
from generator import read_feature_file, generate_test_cases

if __name__ == "__main__":
    feature_text = read_feature_file("examples/sample_feature.txt")
    result = generate_test_cases(feature_text)

    output_path = "output/generated_test_cases.json"
    os.makedirs("output", exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"Test cases generated and saved to {output_path}")