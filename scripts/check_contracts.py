#!/usr/bin/env python3
"""Check only the pilot's explicitly requested JSON and one-word contracts."""

import argparse
import json
from pathlib import Path

from evaluate import input_files, read_jsonl


def check(responses_dir):
    expected = {"items": [
        {"id": "r1", "status": "paid"},
        {"id": "r2", "status": "unpaid"},
        {"id": "r3", "status": "unknown"},
    ]}
    results = {}
    for path in input_files(responses_dir, ".jsonl"):
        rows = read_jsonl(path, ("id", "response"))
        if not {"C09", "C10"}.issubset(rows):
            raise ValueError(f"{path}: C09 and C10 are required")
        try:
            parsed = json.loads(rows["C09"]["response"])
            json_ok = parsed == expected
        except (json.JSONDecodeError, TypeError):
            json_ok = False
        results[path.stem] = {
            "C09_valid_json_and_exact_data": json_ok,
            "C10_only_requested_word": rows["C10"]["response"].strip() == "保留",
        }
    return {
        "checks": results,
        "all_passed": all(all(checks.values()) for checks in results.values()),
        "scope": "Explicit C09/C10 output contracts only; other forms are judged in context.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--responses", required=True, type=Path)
    args = parser.parse_args()
    try:
        result = check(args.responses)
    except (ValueError, OSError) as error:
        parser.error(str(error))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["all_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
