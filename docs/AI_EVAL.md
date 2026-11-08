# Twist-card reader evaluation

Backend: **Gemini on Vertex AI (gemini-3.5-flash)**. A card is correct only if every expected field is right and no other shock is invented.
Tuned cards: the rules were fixed against them. Dev cards: the first held-out set (rules scored 8/16 on it), whose misses were
then used to generalise the rules. Held-out v2: frozen before that change and never used to tune; it is the honest number.

| Reader and card set | Correct | Accuracy | Answered by | Median time | Slowest |
|---|---|---|---|---|---|
| Rules, tuned cards | 22 of 22 | 100% | rules 22 | 0.00 s | 0.00 s |
| Rules, dev cards (old held-out) | 16 of 16 | 100% | rules 16 | 0.00 s | 0.00 s |
| Rules, held-out v2 (never tuned on) | 15 of 16 | 94% | rules 16 | 0.00 s | 0.00 s |
| Gemini on Vertex AI (gemini-3.5-flash), tuned cards | 22 of 22 | 100% | AI 20, rules 2 | 1.47 s | 6.01 s |
| Gemini on Vertex AI (gemini-3.5-flash), dev cards (old held-out) | 15 of 16 | 94% | AI 16 | 1.35 s | 3.07 s |
| Gemini on Vertex AI (gemini-3.5-flash), held-out v2 (never tuned on) | 14 of 16 | 88% | AI 16 | 1.32 s | 4.16 s |

## Misses

- **Rules, held-out v2 (never tuned on)**: "Unemployed for 4 months with EI at 55%, then back to work": return_to_work_month: got None, want 4
- **Gemini on Vertex AI (gemini-3.5-flash), dev cards (old held-out)**: "They're furloughed for three months with EI at 55%": return_to_work_month: invented 4
- **Gemini on Vertex AI (gemini-3.5-flash), held-out v2 (never tuned on)**: "Hours reduced by a third": income_cut: got 0.33, want 0.3333333333333333
- **Gemini on Vertex AI (gemini-3.5-flash), held-out v2 (never tuned on)**: "Unemployed for 4 months with EI at 55%, then back to work": ei_months: got 6, want 4; return_to_work_month: got 5, want 4

## Note (Nov 8): field definitions clarified after the Gemini run
Gemini's two held-out misses came from ambiguous schema definitions, not model errors: "a third" read as 0.33 (the
schema didn't ask for exact decimals) and "unemployed for 4 months, then back to work" read as month 5 (the schema didn't
say the field counts months out of work, which is how `engine.simulate` uses it). The definitions in `ai.SCENARIO_FIELDS`
were clarified afterwards, so a re-run of Gemini on those two v2 cards is no longer blind: report any change on them
separately, not as a held-out improvement.
