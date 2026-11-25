"""Focused offline checks; no API calls or model execution."""

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "evaluate.py"
SPEC = importlib.util.spec_from_file_location("evaluate", SCRIPT)
evaluate = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(evaluate)


class EvaluationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.cases = self.root / "cases.jsonl"
        self.rows = [{"id": f"case-{i}", "messages": [{"role": "user", "content": f"Request {i}"}]}
                     for i in range(3)]
        self.write_rows(self.cases, self.rows)
        self.rubric = self.root / "rubric.json"
        evaluate.write_json(self.rubric, {"criterion": "Answers the user's request accurately."})
        self.responses = self.root / "responses"
        self.responses.mkdir()
        self.names = ["a_secret_baseline", "b_secret_generic", "c_secret_skill"]
        for number, name in enumerate(self.names):
            self.write_rows(self.responses / f"{name}.jsonl",
                            [{"id": row["id"], "response": f"Answer {number}/{row['id']}"}
                             for row in self.rows])

    @staticmethod
    def write_rows(path, rows):
        path.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")

    def make_blind(self, name="blind", seed=41):
        return evaluate.blind(self.cases, self.rubric, self.responses, self.root / name, seed)

    def test_blinded_packet_has_no_condition_or_source_metadata(self):
        packet, key = self.make_blind()
        encoded = json.dumps(packet)
        for name in self.names:
            self.assertNotIn(name, encoded)
        self.assertNotIn(str(self.root), encoded)
        self.assertNotIn("input_sha256", packet)
        self.assertEqual(packet["rubric"], evaluate.read_json(self.rubric))
        self.assertEqual(set(packet), {"schema_version", "instructions", "rubric", "cases"})
        for case in packet["cases"]:
            self.assertEqual([candidate["label"] for candidate in case["candidates"]], ["X", "Y", "Z"])
            self.assertEqual({record["condition"] for record in key["cases"][case["id"]].values()},
                             set(self.names))
        self.assertEqual(len(key["input_sha256"]), 5)
        self.assertTrue(all(len(digest) == 64 for digest in key["input_sha256"].values()))

    def test_stable_seed_and_one_shared_generation_order(self):
        first = self.make_blind("first")
        second = self.make_blind("second")
        self.assertEqual(first, second)
        conditions = self.root / "conditions"
        conditions.mkdir()
        for name, text in zip(self.names, ["", "Be concise.", "PRIVATE SKILL INSTRUCTION"]):
            (conditions / f"{name}.txt").write_text(text, encoding="utf-8")
        manifest = evaluate.prepare(self.cases, conditions, self.root / "prepared", 19)
        other = evaluate.prepare(self.cases, conditions, self.root / "prepared_again", 19)
        self.assertEqual(manifest, other)
        orders = []
        for name in self.names:
            text = (self.root / "prepared" / f"{name}.md").read_text(encoding="utf-8")
            tasks = json.loads(text.split("## Conversations\n\n```json\n")[1].rsplit("\n```", 1)[0])
            orders.append([case["id"] for case in tasks])
            self.assertNotIn("rubric", text)
        self.assertEqual(orders, [manifest["case_ids"]] * len(self.names))

    def test_rejects_missing_extra_duplicate_and_nonstring_responses(self):
        original = [{"id": row["id"], "response": "Answer"} for row in self.rows]
        variants = {
            "missing": original[:-1],
            "extra": original + [{"id": "unexpected", "response": "Answer"}],
            "duplicate": original + [original[0]],
            "nonstring": [{"id": row["id"], "response": None} for row in self.rows],
        }
        for name, rows in variants.items():
            with self.subTest(name=name):
                self.write_rows(self.responses / f"{self.names[0]}.jsonl", rows)
                with self.assertRaises(ValueError):
                    self.make_blind(name)
                self.assertFalse((self.root / name).exists())

    def test_rejects_duplicate_cases_and_private_case_fields(self):
        for rows in (self.rows + [self.rows[0]],
                     [{**row, "private_rubric": "secret"} for row in self.rows]):
            with self.subTest(rows=rows):
                self.write_rows(self.cases, rows)
                with self.assertRaises(ValueError):
                    self.make_blind()

    def test_existing_output_is_preserved(self):
        out = self.root / "existing"
        out.mkdir()
        sentinel = out / "keep.txt"
        sentinel.write_text("keep", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "already exists"):
            self.make_blind("existing")
        self.assertEqual(sentinel.read_text(encoding="utf-8"), "keep")
        self.assertEqual(list(out.iterdir()), [sentinel])

    def make_judgments(self, packet, key):
        a, b, c = self.names
        best = [{a}, {b, c}, {a, b}]
        rejected = [set(), {a}, {c}]
        rows = []
        for index, case in enumerate(packet["cases"]):
            mapping = key["cases"][case["id"]]
            rows.append({"id": case["id"], "candidates": [
                {"label": label, "acceptable": record["condition"] not in rejected[index], "issues": []}
                for label, record in mapping.items()],
                "preferred": [label for label, record in mapping.items() if record["condition"] in best[index]]})
        return {"cases": rows}

    def test_summary_ties_and_unobserved_pairs(self):
        packet, key = self.make_blind()
        judgments = self.root / "judgments.json"
        evaluate.write_json(judgments, self.make_judgments(packet, key))
        result = evaluate.summarize(judgments, self.root / "blind" / "private_key.json")
        a, b, c = self.names
        self.assertEqual(result["case_count"], 3)
        self.assertEqual(result["conditions"][a],
                         {"acceptable": 2, "unacceptable": 1, "sole_best": 1, "shared_best": 1})
        self.assertEqual(result["conditions"][b],
                         {"acceptable": 3, "unacceptable": 0, "sole_best": 0, "shared_best": 2})
        pair = next(pair for pair in result["pairwise"] if pair["conditions"] == [b, c])
        self.assertEqual(pair, {"conditions": [b, c], "wins": {b: 1, c: 0}, "ties": 1, "unobserved": 1})
        self.assertEqual(result, evaluate.summarize(judgments, self.root / "blind" / "private_key.json"))

    def test_summary_rejects_duplicate_or_missing_judgments(self):
        packet, key = self.make_blind()
        valid = self.make_judgments(packet, key)
        variants = []
        for change in ("duplicate_case", "missing_case", "duplicate_candidate", "unknown_preferred", "nonboolean"):
            data = json.loads(json.dumps(valid))
            if change == "duplicate_case":
                data["cases"].append(data["cases"][0])
            elif change == "missing_case":
                data["cases"].pop()
            elif change == "duplicate_candidate":
                data["cases"][0]["candidates"].append(data["cases"][0]["candidates"][0])
            elif change == "unknown_preferred":
                data["cases"][0]["preferred"] = ["unknown"]
            else:
                data["cases"][0]["candidates"][0]["acceptable"] = 1
            variants.append((change, data))
        judgments = self.root / "judgments.json"
        for name, data in variants:
            with self.subTest(name=name):
                evaluate.write_json(judgments, data)
                with self.assertRaises(ValueError):
                    evaluate.summarize(judgments, self.root / "blind" / "private_key.json")


if __name__ == "__main__":
    unittest.main()
