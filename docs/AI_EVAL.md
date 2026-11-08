# Twist-card reader evaluation

Backend: **offline**. A card is correct only if every expected field is right and no other shock is invented.
Tuned cards: the rules were fixed against them. Dev cards: the first held-out set (rules scored 8/16 on it), whose misses were
then used to generalise the rules. Held-out v2: frozen before that change and never used to tune; it is the honest number.

| Reader and card set | Correct | Accuracy | Answered by | Median time | Slowest |
|---|---|---|---|---|---|
| Rules, tuned cards | 22 of 22 | 100% | rules 22 | 0.00 s | 0.00 s |
| Rules, dev cards (old held-out) | 16 of 16 | 100% | rules 16 | 0.00 s | 0.00 s |
| Rules, held-out v2 (never tuned on) | 15 of 16 | 94% | rules 16 | 0.00 s | 0.00 s |

## Misses

- **Rules, held-out v2 (never tuned on)**: "Unemployed for 4 months with EI at 55%, then back to work": return_to_work_month: got None, want 4

_Gemini was not configured for this run. Run on a machine with `GOOGLE_CLOUD_PROJECT` (Vertex AI) set to add the AI rows._
