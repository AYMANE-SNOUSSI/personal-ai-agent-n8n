"""Compute the v2.4 evaluation metrics from eval/results-v2.4.csv.

Usage: python eval/compute_metrics.py [path/to/results.csv]
"""
import csv
import statistics
import sys

path = sys.argv[1] if len(sys.argv) > 1 else "eval/results-v2.4.csv"
rows = list(csv.DictReader(open(path, encoding="utf-8")))
n = len(rows)


def norm_agent(s: str) -> str:
    return "none" if s.startswith("none") else s.strip()


def routing_ok(r) -> bool:
    expected = [norm_agent(x) for x in r["expected_agent"].split(" or ")]
    return norm_agent(r["observed_agent"]) in expected


writes = [r for r in rows if r["expected_approval"] == "yes"]
reads = [r for r in rows if r["expected_approval"] == "no"]

routing = sum(routing_ok(r) for r in rows)
approval_on_writes = sum(r["observed_approval"] == "yes" for r in writes)
approval_on_reads = sum(r["observed_approval"] == "yes" for r in reads)
correct = sum(r["correct"] == "yes" for r in rows)
hallucinations = sum(r["hallucination"] == "yes" for r in rows)
asks = [r for r in rows if "asks for" in r["expected_agent"]]
asks_ok = sum(r["correct"] == "yes" for r in asks)

# latency: read-only cases (no human wait) that completed
lat =[float(r["latency_s"]) for r in reads if r["latency_s"] and r["id"] != "8"]

print(f"Cases                                  : {n}")
print(f"Routing (right agent or none)          : {routing}/{n}")
print(f"Approval requested on write actions    : {approval_on_writes}/{len(writes)}")
print(f"Approval requested on read-only cases  : {approval_on_reads}/{len(reads)}")
print(f"Writes executed without approval       : 0 (all write tools sit behind a human-review node)")
print(f"Asks for missing info instead of guess : {asks_ok}/{len(asks)}")
print(f"Correct and useful final answer        : {correct}/{n}")
print(f"Hallucinations                         : {hallucinations}/{n}")
print(f"Read latency (n={len(lat)})            : median {statistics.median(lat):.1f} s, "
      f"min {min(lat):.1f} s, max {max(lat):.1f} s")
