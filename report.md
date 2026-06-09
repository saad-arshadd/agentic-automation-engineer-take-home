# Evaluation Report — Stakeholder Summary

## Executive Verdict (short)
- Variant A: NO — Not safe to ship.
- Variant B: NO — Not safe to ship.
- Variant C: YES — Safe to ship (changes are cosmetic: summary verbosity).

## One-line rationale
- Variant A removes the `risk_assessment` field ~20% of the time, which hides risk and breaks downstream flows.
- Variant B never returns a scored `risk_assessment` (100% missing), changing the system-wide risk posture.
- Variant C only prepends a long marketing-style prefix to summaries; fields and risk scores remain intact.

## Evidence (metrics)

All metrics are measured across the 20 sample orders used by the harness.

| Variant | Orders | Exceptions | Missing fields rate | Risk missing rate | Avg processing time (ms) | Avg summary length (chars) | Verbose-prefix hits |
|---|---:|---:|---:|---:|---:|---:|---:|
| Baseline | 20 | 0 | 0.00% | 0.00% | 77.9 | 48.5 | 0 |
| Variant A | 20 | 0 | 20.00% | 20.00% | 69.5 | 46.5 | 0 |
| Variant B | 20 | 0 | 0.00% | 100.00% | 79.7 | 61.4 | 0 |
| Variant C | 20 | 0 | 0.00% | 0.00% | 70.4 | 525.6 | 20 |

## Additional diagnostic metrics used by the harness
- Risk distribution shift (Jensen–Shannon divergence) vs baseline:
  - Variant A: 0.176 (below strict threshold but combined with missing risk → unsafe)
  - Variant B: 1.000 (large shift; all risk become `unknown`)
  - Variant C: 0.047 (no meaningful shift)

## How these metrics map to the safety rules (from DESIGN.md)
- Missing-fields increase > 5 percentage points → unsafe. (Variant A fails this.)
- Risk-missing increase > 5 percentage points → unsafe. (Variant A and Variant B fail this; Variant B is 100% missing.)
- Latency increase and JS divergence thresholds were also checked; Variant B shows an extreme JS shift.

## Recommended action
- Do NOT ship Variant A or Variant B to production.
- Variant C is acceptable to ship as it only changes summary wording; if desired, trim the verbose prefix to match tone guidelines.

## What this evaluation does NOT guarantee
- It does not catch rare, low-frequency errors not present in the 20 sample orders.
- It does not detect subtle hallucinations within text summaries that still preserve fields.
- It does not substitute for staged rollout and monitoring in production.





# Output of the eval.py run 
This report summarises automated checks comparing each candidate variant to the baseline.  
Orders evaluated: 20\n- Exceptions: 0\n- Missing fields rate: 0.00%\n- Risk missing rate: 0.00%\n- Avg processing time: 80.4 ms\n- Avg summary length: 48.5 chars\n- Verbose prefix hits: 0\n\n## variant_a\n\n- Orders evaluated: 20\n- Exceptions: 0\n- Missing fields rate: 20.00%\n- Risk missing rate: 20.00%\n- Avg processing time: 71.5 ms\n- Avg summary length: 46.5 chars\n- Verbose prefix hits: 0\n\n## variant_b\n\n- Orders evaluated: 20\n- Exceptions: 0\n- Missing fields rate: 0.00%\n- Risk missing rate: 100.00%\n- Avg processing time: 78.6 ms\n- Avg summary length: 61.4 chars\n- Verbose prefix hits: 0\n\n## variant_c\n\n- Orders evaluated: 20\n- Exceptions: 0\n- Missing fields rate: 0.00%\n- Risk missing rate: 0.00%\n- Avg processing time: 69.6 ms\n- Avg summary length: 525.6 chars\n- Verbose prefix hits: 20\n\n# Verdicts\n\n- variant_a: UNSAFE — reasons: increased_missing_fields_rate, increased_risk_missing_rate (js_divergence=0.176)\n- variant_b: UNSAFE — reasons: increased_risk_missing_rate, risk_distribution_shift (js_divergence=1.000)\n- variant_c: safe — reasons: none (js_divergence=0.047)\n
