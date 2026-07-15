"""Converts a pytest-json-report output file into the common results.json
format shared across all portfolio repositories."""

import json
import sys
from datetime import datetime, timezone

REPO_NAME = "llm-test-case-generator"


def main():
    with open("pytest-report.json", "r", encoding="utf-8") as f:
        report = json.load(f)

    summary = report.get("summary", {})

    result = {
        "repo": REPO_NAME,
        "total": summary.get("total", 0),
        "passed": summary.get("passed", 0),
        "failed": summary.get("failed", 0),
        "skipped": summary.get("skipped", 0),
        "duration_seconds": round(report.get("duration", 0), 2),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    with open("results.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    print(f"results.json generated for {REPO_NAME}: {result}")


if __name__ == "__main__":
    sys.exit(main())