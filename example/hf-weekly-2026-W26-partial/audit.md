# Audit — HF Weekly Digest Partial Week Test

## PaperScope editorial regression

This bundle is the regression artifact for the PaperScope editorial-mode upgrade.
It intentionally reuses the same frozen 89-paper snapshot as the earlier
text-only test so improvements are attributable to the workflow rather than a
different corpus.

Required output files:

- `digest.md`
- `digest-wechat.html`
- `editorial.json`
- `assets/manifest.json`
- two original editorial SVGs
- ten paper-native PNG figures with source provenance
- `source.json`
- `papers.json`

Publication metrics after the upgrade:

| Metric | Earlier test | PaperScope editorial test |
|---|---:|---:|
| Non-whitespace article characters | 4,097 | 15,444 |
| Numbered themes | 0 | 5 |
| Visuals | 0 | 12 |
| Complete paper cards | 0 | 13 |
| Paper-card headings detected | 6 | 14 |
| “真正的 insight” passages | 0 | 15 |
| Forward transitions | 0 | 4 |
| `判断/为什么/技术综观/落地实战` engines | 0 | 5 complete cycles |
| WeChat HTML | absent | generated |

The visual system now uses two original editorial assets (cover and daily-count
chart) plus ten native figures from ten papers. Native figures are downloaded
from official project pages or arXiv HTML, stored locally, and recorded with
paper ID, Figure number, original caption, source page, and direct image URL.
No image was copied from the reference public-account article.

Native-paper coverage is 10/11 non-cover visuals (90.9%), above the 70%
publication threshold. Every numbered theme contains at least one native paper
figure. The native sources are PlanBench-XL, OpenRath, CLI-Universe, DataClaw0,
Qwen-AgentWorld, World Action Models, Foresight, Grouped Query Experts,
PerceptionDLM, and Unlimited OCR.

PaperScope-mode mobile visual QA was performed at a 390×844 viewport:

- document width and body width both remained 390px; no horizontal overflow;
- all twelve images loaded successfully and scaled to the article container;
- the DOM contained twelve figures and twelve captions;
- all ten paper-native figures expose a visible `点击查看高清原图` link, and
  both the image and caption link to the local high-resolution file;
- browser console contained no warnings or errors;
- representative wide and dense framework figures were visually inspected at
  mobile width after rendering.

## Scope

- Requested interpretation: current week to date.
- Absolute period: 2026-06-22 through 2026-06-24, inclusive.
- ISO week: 2026-W26, partial.
- Source snapshot: Hugging Face Daily Papers API.
- Retrieved at: 2026-06-24T08:01:56.875029+00:00.
- Raw entries: 89.
- Normalized unique papers: 89.
- Frozen files: `source.json` and `papers.json`.

This is not comparable to a completed seven-day issue without normalization for
the shorter collection window.

## Triage and selection

All 89 titles and abstracts received a coarse semantic pass. Because topics
overlap, no full-corpus topic percentage is asserted in the article.

The Top 20 by frozen upvotes received a manual binary classification for the
specific statement “directly concerns agents, agent runtimes, agent training
data, or agent evaluation.” Thirteen papers met that criterion:

1. PlanBench-XL
2. OpenRath
3. DataClaw0
4. EnterpriseClawBench
5. Qwen-AgentWorld
6. MemSlides
7. NatureBench
8. CLI-Universe
9. EvoEmbedding
10. MobileForge
11. AOHP
12. MemGUI-Agent
13. LingxiDiagBench

`World Action Models: A Survey` was excluded from the binary count because its
title-level scope is broader than agent system engineering. Including it would
raise the result to 14/20; the article uses the conservative count.

Deep-read representatives were chosen for theme coverage, not only popularity:
PlanBench-XL, EnterpriseClawBench, NatureBench, OpenRath, CLI-Universe,
Qwen-AgentWorld, Grouped Query Experts, PerceptionDLM, and Unlimited OCR.

## Reproducible arithmetic

| Claim | Calculation |
|---|---|
| GitHub availability | 62/89 = 69.7% |
| Project-page availability | 55/89 = 61.8% |
| Top-20 Agent-related share | 13/20 = 65.0% |
| Top-20 frozen upvotes | 782 |
| Agent-related Top-20 frozen upvotes | 538/782 = 68.8% |
| Upvote median | 5 |

Upvotes are taken only from `papers.json`. Live HF pages changed during the
test—for example, DataClaw0 moved from the frozen 66 to 67—so live values were
not mixed into article statistics.

## Claim ledger

| ID | Claim | Class | Evidence | Confidence |
|---|---|---|---|---|
| C01 | 89 unique papers were collected | DATA | `papers.json` | high |
| C02 | 13/20 of the frozen Top 20 are Agent-related | DATA + manual classification | Top-20 list above | medium-high |
| C03 | Agent research shows a shift toward system engineering | INFERENCE | PlanBench-XL, EnterpriseClawBench, OpenRath, CLI-Universe, Qwen-AgentWorld | medium |
| C04 | GPT-5.4 falls from 51.90% to 11.36% in PlanBench-XL blocking conditions | PAPER | PlanBench-XL abstract | high |
| C05 | EnterpriseClawBench contains 852 tasks and best score is 0.663 | PAPER | paper abstract/HF page | high |
| C06 | NatureBench strongest system surpasses SOTA on 17.8% of 90 tasks | PAPER | arXiv abstract | high |
| C07 | CLI-Universe-6K fine-tuned Qwen3-32B reaches 33.4% on Terminal-Bench 2.0 | PAPER | HF paper page | high |
| C08 | Qwen-AgentWorld-397B scores 58.71 on AgentWorldBench | PAPER | paper Table 5 | high |
| C09 | Agent training may adopt mixed real/simulated environments | FORECAST | Qwen-AgentWorld Sim RL results | medium-low |
| C10 | Non-Agent architecture research remains active | INFERENCE | GQE, PerceptionDLM, Unlimited OCR | medium |

## Limitations and counter-signals

- Only the first three days of the week are included.
- Hugging Face submission timing differs from arXiv publication timing.
- Upvotes measure engagement and are mutable.
- The Top-20 Agent classification involves editorial judgment.
- Several quantitative findings come from newly released, author-built
  benchmarks without independent replication.
- EnterpriseClawBench does not release its proprietary task data.
- OpenRath deliberately leaves broad quantitative comparison for future work.
- GQE is evaluated at 250M parameter scale; large-model behavior is unknown.
- Qwen-AgentWorld is weaker than leading frontier models on some GUI-domain
  averages, despite leading its own overall benchmark.

## Verification checklist

- [x] Absolute dates stated.
- [x] Partial-week status stated in title and methodology.
- [x] Raw and normalized snapshots preserved.
- [x] Percentages include numerator and denominator.
- [x] Representative technical claims checked against paper pages/original text.
- [x] Live and frozen upvote values not mixed.
- [x] Broad claims softened to signals/inference.
- [x] Counterexamples included.
- [x] No affiliation inferred from names.
- [x] No future prediction presented as established fact.
- [x] Publication profile meets minimum length.
- [x] At least six attributed visuals are present.
- [x] At least 70% of non-cover visuals are paper-native.
- [x] Every numbered theme contains a paper-native figure.
- [x] Every paper-native figure records complete provenance.
- [x] Dense paper figures link to a high-resolution local original.
- [x] At least eight complete paper cards are present.
- [x] WeChat HTML is generated from the same Markdown source.
- [x] Visual manifest records every local asset.
- [x] Article and HTML use only frozen upvotes.
- [x] Exactly five numbered themes are present.
- [x] Every theme contains judgment, timing, papers, technical synthesis, and
  practical application.
- [x] Four forward transitions connect the five themes.
- [x] Action list, three questions, summary, quotations, and final methodology
  are present.
- [x] PaperScope editorial style audit passes.
