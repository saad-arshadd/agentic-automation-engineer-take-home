
import json
import math
import hashlib
import random
from collections import Counter, defaultdict

from variants import baseline, variant_a, variant_b, variant_c


def load_orders(path):
    orders = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            orders.append(json.loads(line))
    return orders


def seed_for(variant_name, order_id):
    h = hashlib.md5(f"{variant_name}:{order_id}".encode()).hexdigest()
    return int(h[:8], 16)


def safe_get(d, key):
    v = d.get(key)
    return v if v is not None else None


def jensen_shannon(p, q):
    
    keys = set(p) | set(q)
    p_total = sum(p.values()) or 1
    q_total = sum(q.values()) or 1
    P = [p.get(k, 0) / p_total for k in keys]
    Q = [q.get(k, 0) / q_total for k in keys]
    M = [(pi + qi) / 2 for pi, qi in zip(P, Q)]
    def kld(a, b):
        s = 0.0
        for ai, bi in zip(a, b):
            if ai == 0:
                continue
            s += ai * math.log(ai / (bi or 1e-12), 2)
        return s
    return (kld(P, M) + kld(Q, M)) / 2


def analyze_variant(name, fn, orders):
    metrics = defaultdict(list)
    exceptions = 0
    risk_levels = Counter()
    recommendations = Counter()
    verbose_prefix_hits = 0

    for o in orders:
        order_id = o.get("order_id", "")
        random.seed(seed_for(name, order_id))
        try:
            out = fn.enrich_order(o) if hasattr(fn, "enrich_order") else fn(o)
        except Exception as e:
            exceptions += 1
            continue

        
        missing = 0
        for required in ("pricing", "shipping", "risk_assessment"):
            if required not in out or out.get(required) is None:
                missing += 1
        metrics["missing_fields"].append(missing > 0)

        # risk
        risk = out.get("risk_assessment", {}) or {}
        if risk.get("risk_score") is None:
            metrics["risk_missing"].append(1)
        else:
            metrics["risk_missing"].append(0)

        rl = risk.get("risk_level") or "unknown"
        risk_levels[rl] += 1
        recommendations[risk.get("recommendation") or "unknown"] += 1

        # timing
        metrics["processing_time_ms"].append(out.get("processing_time_ms") or 0)

        # summary characteristics
        summary = out.get("summary") or ""
        metrics["summary_len"].append(len(summary))
        if isinstance(summary, str) and summary.startswith("In the rapidly evolving landscape"):
            verbose_prefix_hits += 1

    results = {
        "variant": name,
        "n_orders": len(orders),
        "exceptions": exceptions,
        "missing_fields_rate": sum(metrics["missing_fields"]) / max(1, len(orders)),
        "risk_missing_rate": sum(metrics["risk_missing"]) / max(1, len(orders)),
        "avg_processing_time_ms": (sum(metrics["processing_time_ms"]) / max(1, len(metrics["processing_time_ms"]))) if metrics["processing_time_ms"] else None,
        "summary_avg_len": (sum(metrics["summary_len"]) / max(1, len(metrics["summary_len"]))) if metrics["summary_len"] else 0,
        "verbose_prefix_hits": verbose_prefix_hits,
        "risk_level_counts": dict(risk_levels),
        "recommendation_counts": dict(recommendations),
    }
    return results


def verdict_against(baseline_res, cand_res):
    # Simple heuristics to decide whether candidate is safe relative to baseline.
    reasons = []
    unsafe = False

    # Missing fields
    if cand_res["missing_fields_rate"] > baseline_res["missing_fields_rate"] + 0.05:
        unsafe = True
        reasons.append("increased_missing_fields_rate")

    # Risk missing rate
    if cand_res["risk_missing_rate"] > baseline_res["risk_missing_rate"] + 0.05:
        unsafe = True
        reasons.append("increased_risk_missing_rate")

    # Latency
    if baseline_res["avg_processing_time_ms"] and cand_res["avg_processing_time_ms"]:
        if cand_res["avg_processing_time_ms"] > baseline_res["avg_processing_time_ms"] * 2 and cand_res["avg_processing_time_ms"] > 500:
            unsafe = True
            reasons.append("significant_latency_increase")

    
    js = jensen_shannon(baseline_res["risk_level_counts"], cand_res["risk_level_counts"])
    if js > 0.2:
        unsafe = True
        reasons.append("risk_distribution_shift")

    return {"unsafe": unsafe, "reasons": reasons, "js_divergence": js}


def main():
    orders = load_orders("c:\\Users\\pc\\Desktop\\Keeyu\\agentic-automation-engineer-take-home\\fixtures\\orders.jsonl")

    variants = {
        "baseline": baseline,
        "variant_a": variant_a,
        "variant_b": variant_b,
        "variant_c": variant_c,
    }

    results = {}
    for name, fn in variants.items():
        print(f"Evaluating {name} ...")
        results[name] = analyze_variant(name, fn, orders)

    
    baseline_res = results["baseline"]
    verdicts = {}
    for name, res in results.items():
        if name == "baseline":
            continue
        verdicts[name] = verdict_against(baseline_res, res)

    out = {"results": results, "verdicts": verdicts}
    with open("c:\\Users\\pc\\Desktop\\Keeyu\\agentic-automation-engineer-take-home\\results.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)

    # Reportts
    with open("c:\\Users\\pc\\Desktop\\Keeyu\\agentic-automation-engineer-take-home\\report.md", "w", encoding="utf-8") as f:
        f.write("# Evaluation Report\\n\\n")
        f.write("This report summarises automated checks comparing each candidate variant to the baseline.\\n\\n")
        for name, res in results.items():
            f.write(f"## {name}\\n\\n")
            f.write(f"- Orders evaluated: {res['n_orders']}\\n")
            f.write(f"- Exceptions: {res['exceptions']}\\n")
            f.write(f"- Missing fields rate: {res['missing_fields_rate']:.2%}\\n")
            f.write(f"- Risk missing rate: {res['risk_missing_rate']:.2%}\\n")
            f.write(f"- Avg processing time: {res['avg_processing_time_ms']:.1f} ms\\n")
            f.write(f"- Avg summary length: {res['summary_avg_len']:.1f} chars\\n")
            f.write(f"- Verbose prefix hits: {res['verbose_prefix_hits']}\\n")
            f.write("\\n")
        f.write("# Verdicts\\n\\n")
        for name, v in verdicts.items():
            safe_str = "UNSAFE" if v["unsafe"] else "safe"
            f.write(f"- {name}: {safe_str} — reasons: {', '.join(v['reasons']) or 'none'} (js_divergence={v['js_divergence']:.3f})\\n")


if __name__ == "__main__":
    main()
