Evaluation design (one page)

What I measure
- Completeness: fraction of outputs missing critical fields (`pricing`, `shipping`, `risk_assessment`).
- Risk availability: fraction of outputs with missing or `None` risk scores.
- Latency: average `processing_time_ms` reported by the agent.
- Summary characteristics: average summary length and detection of verbose prefix (Variant C).
- Risk distribution shift: Jensen–Shannon divergence between risk-level distributions.

Safety Decisons are based on follow:
- If a candidate increases missing-fields rate by > 5 percentage points vs baseline → unsafe.
- If a candidate increases risk-missing rate by > 5 percentage points → unsafe.
- If average latency > 2x baseline and > 500ms absolute → unsafe.
- If JS divergence on risk-levels > 0.2 → unsafe.

Why these metrics
- They catch regressions that would break downstream processors (missing fields), hide risk (missing risk), slow processing, or change overall risk posture.

What this eval does not catch
- Subtle semantic changes inside `summary` that preserve field names but introduce hallucinations.
- Low-frequency regressions that do not appear in the 20 fixture orders.
- Issues that only appear under production traffic patterns or different locales.

Reproducibility
- Runs are deterministic by seeding the RNG per variant+order.
- Runtime: single run on the 20 fixtures should complete in < 10s on a dev laptop.

Extensions (if more time)
- Add an LLM-based semantic judge for summaries (detect hallucination or tone).
- Run more randomized trials and bootstrap confidence intervals.
- Add unit tests asserting no missing required fields for the baseline.

Rough cost estimate
- CPU-only run: negligible — a single run on a small cloud VM or developer laptop costs << $0.01 in CPU time.
- If you add an LLM-based summary judge: cost depends on model and tokens; expect roughly $0.01–$2.00 per run depending on model choice and prompt size.
