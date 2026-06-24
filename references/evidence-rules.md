# Evidence rules

## Claim classes

| Label | Meaning | Minimum support |
|---|---|---|
| `DATA` | Directly computed corpus fact | frozen `papers.json` and reproducible arithmetic |
| `PAPER` | Claim made or demonstrated by a paper | HF paper page or original paper section/table |
| `INFERENCE` | Editorial synthesis or causal interpretation | cited observations plus alternatives or caveat |
| `FORECAST` | Prediction about future research/products | explicit forecast language and observable trigger |

Write the label in `audit.md`. The final article may omit visual labels when the
wording already makes the epistemic status unmistakable.

## Trend threshold

A broad trend normally needs:

- at least three relevant papers;
- at least two independent institutions or author groups;
- a stated denominator or corpus scope;
- no obvious counterexample omitted from the same period.

If one condition fails, call it a `weak signal`, `early cluster`, or
`notable paper`, not an industry-wide turn.

## Population rules

- Distinguish `all papers`, `Top N by frozen upvotes`, and `deep-read shortlist`.
- Write percentages as “X/Y (Z%) of Top N” on first use.
- Do not compare weeks unless both were fetched and normalized by the same
  method.
- Upvotes are engagement at retrieval time, not paper quality.
- Preserve retrieval timestamp because upvotes can change.

## Paper verification

For every representative paper, capture:

- paper ID and canonical links;
- problem and proposed mechanism;
- evaluation datasets or settings;
- main result with baseline/context;
- limitations stated by authors;
- linked code/model/data availability;
- affiliation only when explicitly available.

Do not use an AI-generated paper summary as the sole source for technical or
quantitative claims.

## Claim ledger template

```markdown
| ID | Claim | Class | Evidence | Confidence | Final wording |
|---|---|---|---|---|---|
| C01 | 9 of Top 35 are benchmarks | DATA | papers.json + classification.csv | high | Top 35 中有 9 篇（26%）... |
| C02 | evaluation is becoming fragmented | INFERENCE | C01 + papers A/B/C | medium | 本周出现了评测分化的信号... |
| C03 | this will become standard next quarter | FORECAST | C02 | low | 值得观察下一季度是否... |
```

## Final audit

1. Recompute every total, percentage, rank, and upvote from one snapshot.
2. Search each representative paper title and confirm all repeated numbers
   match.
3. Confirm every superlative states its scope: “this week,” “within Top N,” etc.
4. Replace “proves,” “ends,” “all,” and “will” unless evidence warrants them.
5. Check whether a quieter counterexample changes the headline.
6. Verify every link and paper ID.
7. List incomplete reads, unavailable pages, and classification ambiguity in
   `audit.md`.

