# Twist-card reader evaluation

Backend: **offline**. A card is correct only if every expected field is right and no other shock is invented.
Tuned cards are the ones the rules were fixed against; held-out cards were written afterwards and never used to tune.

| Reader and card set | Correct | Accuracy | Answered by | Median time | Slowest |
|---|---|---|---|---|---|
| Rules, tuned cards | 22 of 22 | 100% | rules 22 | 0.00 s | 0.00 s |
| Rules, held-out cards | 8 of 16 | 50% | rules 16 | 0.00 s | 0.00 s |

## Misses

- **Rules, held-out cards**: "Their hours are cut in half": income_cut: got 0.0, want 0.5
- **Rules, held-out cards**: "They're furloughed for three months with EI at 55%": job_loss: got False, want True; ei_months: got 6, want 3
- **Rules, held-out cards**: "Rent jumps 8%": bills_increase_pct: got 0.0, want 0.08
- **Rules, held-out cards**: "Utilities go up ten percent": bills_increase_pct: got 0.0, want 0.1
- **Rules, held-out cards**: "They take a 15% pay cut": income_cut: got 0.0, want 0.15
- **Rules, held-out cards**: "Laid off in a downturn, EI 55%, back at work after 5 months": return_to_work_month: got None, want 5
- **Rules, held-out cards**: "They lose half their income": income_cut: got 0.0, want 0.5
- **Rules, held-out cards**: "Their household bills double": bills_increase_pct: got 0.0, want 1.0

_Gemini was not configured for this run. Run on a machine with `GOOGLE_CLOUD_PROJECT` (Vertex AI) set to add the AI rows._
