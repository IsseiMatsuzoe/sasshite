#!/usr/bin/env python3
"""Offline generation packets, blinded evaluation, and descriptive summaries.

Judgments: {"cases": [{"id": "...", "candidates": [{"label": "X",
"acceptable": true, "issues": []}], "preferred": ["X"]}]}. Include every
candidate and case exactly once. Select one or more jointly best labels, even
when every answer is unacceptable. Two unpreferred answers remain unranked.
"""

import argparse
import hashlib
import itertools
import json
import random
from pathlib import Path


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def index_rows(rows, fields, context):
    indexed = {}
    if not isinstance(rows, list) or not rows:
        raise ValueError(f"{context}: expected a nonempty list")
    for row in rows:
        if not isinstance(row, dict) or set(row) != set(fields):
            raise ValueError(f"{context}: each row must contain only {', '.join(fields)}")
        case_id = row["id"]
        if not isinstance(case_id, str) or not case_id:
            raise ValueError(f"{context}: ids must be nonempty strings")
        if case_id in indexed:
            raise ValueError(f"{context}: duplicate id {case_id!r}")
        indexed[case_id] = row
    return indexed


def read_jsonl(path, fields):
    rows = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if line.strip():
            try:
                rows.append(json.loads(line))
            except ValueError as error:
                raise ValueError(f"{path}:{number}: invalid JSON: {error}") from error
    return index_rows(rows, fields, str(path))


def read_cases(path):
    cases = read_jsonl(path, ("id", "messages"))
    for case in cases.values():
        messages = case["messages"]
        if not isinstance(messages, list) or not messages:
            raise ValueError(f"case {case['id']!r}: messages must be a nonempty list")
        for message in messages:
            if (not isinstance(message, dict) or set(message) != {"role", "content"}
                    or not isinstance(message["role"], str) or not message["role"]
                    or not isinstance(message["content"], str)):
                raise ValueError(f"case {case['id']!r}: messages require string role/content")
    return cases


def require_coverage(actual, expected, context):
    missing, extra = set(expected) - set(actual), set(actual) - set(expected)
    if missing or extra:
        raise ValueError(f"{context}: coverage mismatch; missing={sorted(missing)}, extra={sorted(extra)}")


def input_hashes(paths):
    return {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in paths}


def input_files(directory, suffix):
    if not directory.is_dir():
        raise ValueError(f"not a directory: {directory}")
    paths = sorted(path for path in directory.glob(f"*{suffix}") if path.is_file())
    if not paths:
        raise ValueError(f"{directory}: no {suffix} files")
    return paths


def make_output(path):
    if path.exists():
        raise ValueError(f"output already exists: {path}; choose a new directory")
    path.mkdir(parents=True, exist_ok=False)


def prepare(cases_path, conditions_dir, out, seed):
    cases = list(read_cases(cases_path).values())
    paths = input_files(conditions_dir, ".txt")
    conditions = {path.stem: path.read_text(encoding="utf-8") for path in paths}
    random.Random(seed).shuffle(cases)
    instructions = (
        "Answer each conversation independently with the assistant's next response. "
        "Apply the condition to each conversation; reset conversation context between cases. "
        "Do not grade, compare, or discuss these tasks. Save one JSONL row per case in the "
        'provided order: {"id":"case id","response":"complete answer"}. '
        "JSONL is only a transport format: inside the response string, use the length and "
        "presentation appropriate for that user's request. Include every id exactly once.\n"
    )
    manifest = {"schema_version": 1, "seed": seed, "case_ids": [case["id"] for case in cases],
                "input_sha256": input_hashes([cases_path, *paths]),
                "packets": {name: f"{name}.md" for name in conditions}}
    make_output(out)
    for name, condition in conditions.items():
        packet = ("# Generation packet\n\n" + instructions
                  + "\n## Condition\n\nThe JSON string below is the additional instruction. "
                  + "An empty string means no additional instruction.\n\n```json\n"
                  + json.dumps(condition, ensure_ascii=False)
                  + "\n```\n\n## Conversations\n\n```json\n"
                  + json.dumps(cases, ensure_ascii=False, indent=2) + "\n```\n")
        (out / f"{name}.md").write_text(packet, encoding="utf-8")
    write_json(out / "manifest.json", manifest)
    return manifest


def candidate_label(index):
    alphabet, label = "XYZABCDEFGHIJKLMNOPQRSTUVW", ""
    while True:
        index, remainder = divmod(index, len(alphabet))
        label = alphabet[remainder] + label
        if not index:
            return label
        index -= 1


def blind(cases_path, rubric_path, responses_dir, out, seed):
    cases = read_cases(cases_path)
    rubric = read_json(rubric_path)
    if not isinstance(rubric, dict):
        raise ValueError("rubric must be a JSON object")
    paths = input_files(responses_dir, ".jsonl")
    responses = {}
    for path in paths:
        rows = read_jsonl(path, ("id", "response"))
        require_coverage(rows, cases, str(path))
        if any(not isinstance(row["response"], str) for row in rows.values()):
            raise ValueError(f"{path}: every response must be a string")
        responses[path.stem] = rows
    packet = {"schema_version": 1,
              "instructions": (
                  "Evaluate each candidate against the conversation and rubric independently. "
                  "Return JSON: {\"cases\":[{\"id\":\"...\",\"candidates\":[{\"label\":\"X\","
                  "\"acceptable\":true,\"issues\":[]}],\"preferred\":[\"X\"]}]}. "
                  "Include every case and candidate exactly once. Issues are strings. Select "
                  "one or more jointly best labels, even if all answers are unacceptable. "
                  "Two unpreferred candidates have no observed ordering. Judge suitability "
                  "to the request; do not reward a fixed length or presentation style."),
              "rubric": rubric, "cases": []}
    key = {"schema_version": 1, "seed": seed,
           "input_sha256": input_hashes([cases_path, rubric_path, *paths]), "cases": {}}
    rng = random.Random(seed)
    for case_id, case in cases.items():
        names = list(responses)
        rng.shuffle(names)
        candidates, mapping = [], {}
        for index, name in enumerate(names):
            label, response = candidate_label(index), responses[name][case_id]["response"]
            candidates.append({"label": label, "response": response})
            mapping[label] = {"condition": name, "characters": len(response)}
        packet["cases"].append({**case, "candidates": candidates})
        key["cases"][case_id] = mapping
    make_output(out)
    write_json(out / "packet.json", packet)
    write_json(out / "private_key.json", key)
    return packet, key


def summarize(judgments_path, key_path):
    judgments, key = read_json(judgments_path), read_json(key_path)
    mappings = key.get("cases") if isinstance(key, dict) else None
    if not isinstance(mappings, dict) or not mappings:
        raise ValueError("private key must contain a nonempty cases object")
    conditions, lengths = None, {}
    for case_id, mapping in mappings.items():
        if not isinstance(case_id, str) or not case_id or not isinstance(mapping, dict) or not mapping:
            raise ValueError("private key has an invalid case mapping")
        names = []
        for label, record in mapping.items():
            if (not isinstance(label, str) or not label or not isinstance(record, dict)
                    or not isinstance(record.get("condition"), str) or not record["condition"]
                    or type(record.get("characters")) is not int or record["characters"] < 0):
                raise ValueError("private key has an invalid candidate mapping")
            names.append(record["condition"])
            lengths.setdefault(record["condition"], []).append(record["characters"])
        if len(set(names)) != len(names) or (conditions is not None and set(names) != conditions):
            raise ValueError("private key must map each condition exactly once in every case")
        conditions = set(names)
    rows = index_rows(judgments.get("cases") if isinstance(judgments, dict) else None,
                      ("id", "candidates", "preferred"), "judgments")
    require_coverage(rows, mappings, "judgments")
    counts = {name: {"acceptable": 0, "unacceptable": 0, "sole_best": 0, "shared_best": 0}
              for name in sorted(conditions)}
    pairs = [{"conditions": [a, b], "wins": {a: 0, b: 0}, "ties": 0, "unobserved": 0}
             for a, b in itertools.combinations(sorted(conditions), 2)]
    for case_id, row in rows.items():
        mapping, candidates = mappings[case_id], row["candidates"]
        if not isinstance(candidates, list):
            raise ValueError(f"{case_id}: candidates must be a list")
        seen = set()
        for candidate in candidates:
            if (not isinstance(candidate, dict) or set(candidate) != {"label", "acceptable", "issues"}
                    or not isinstance(candidate["label"], str)
                    or type(candidate["acceptable"]) is not bool
                    or not isinstance(candidate["issues"], list)
                    or any(not isinstance(issue, str) for issue in candidate["issues"])):
                raise ValueError(f"{case_id}: invalid candidate judgment")
            label = candidate["label"]
            if label in seen:
                raise ValueError(f"{case_id}: duplicate candidate label {label!r}")
            seen.add(label)
        require_coverage(seen, mapping, f"{case_id} candidates")
        preferred = row["preferred"]
        if (not isinstance(preferred, list) or not preferred
                or any(not isinstance(label, str) for label in preferred)
                or len(set(preferred)) != len(preferred) or not set(preferred) <= seen):
            raise ValueError(f"{case_id}: preferred must contain unique known labels, at least one")
        for candidate in candidates:
            name = mapping[candidate["label"]]["condition"]
            counts[name]["acceptable" if candidate["acceptable"] else "unacceptable"] += 1
        best = {mapping[label]["condition"] for label in preferred}
        for name in best:
            counts[name]["sole_best" if len(best) == 1 else "shared_best"] += 1
        for pair in pairs:
            a, b = pair["conditions"]
            if a in best and b in best:
                pair["ties"] += 1
            elif a in best or b in best:
                pair["wins"][a if a in best else b] += 1
            else:
                pair["unobserved"] += 1
    return {"case_count": len(rows), "conditions": counts, "pairwise": pairs,
            "character_diagnostics": {
                name: {"mean": round(sum(values) / len(values), 2), "min": min(values), "max": max(values)}
                for name, values in sorted(lengths.items())},
            "interpretation": (
                "Descriptive counts only; no statistical significance is inferred. A pairwise win "
                "means preferred over an unpreferred candidate. A tie means jointly preferred. "
                "Two unpreferred candidates are unobserved, not tied. Character counts are "
                "diagnostics only and do not affect acceptability or preference.")}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for command in ("prepare", "blind"):
        sub = commands.add_parser(command)
        sub.add_argument("--cases", type=Path, required=True)
        sub.add_argument("--out", type=Path, required=True)
        sub.add_argument("--seed", type=int, required=True)
        if command == "prepare":
            sub.add_argument("--conditions", type=Path, required=True)
        else:
            sub.add_argument("--rubric", type=Path, required=True)
            sub.add_argument("--responses", type=Path, required=True)
    sub = commands.add_parser("summarize")
    sub.add_argument("--judgments", type=Path, required=True)
    sub.add_argument("--key", type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.command == "prepare":
            prepare(args.cases, args.conditions, args.out, args.seed)
            print(f"Wrote generation packets to {args.out}")
        elif args.command == "blind":
            blind(args.cases, args.rubric, args.responses, args.out, args.seed)
            print(f"Wrote packet.json and private_key.json to {args.out}; share only packet.json")
        else:
            print(json.dumps(summarize(args.judgments, args.key), ensure_ascii=False, indent=2))
    except (ValueError, OSError) as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()
