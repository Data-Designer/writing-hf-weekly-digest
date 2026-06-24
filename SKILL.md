---
name: writing-hf-weekly-digest
description: Use when creating or revising a Chinese weekly review, detailed newsletter, research-intelligence report, visual trend analysis, publication-ready WeChat article, or illustrated HF/arXiv paper digest for a requested week or date range.
---

# Writing HF Weekly Digest

## Overview

Turn a frozen Hugging Face Daily Papers period into an auditable Chinese
digest. Match the requested artifact: concise intelligence stays concise, while
article references, “图文并茂,” “详细,” “成稿,” and “可发布” require a full
publication bundle with visuals, HTML, and rendered QA.

**REQUIRED SUB-SKILL:** Use `huggingface-papers` to inspect shortlisted paper
pages, structured metadata, linked repositories, and original paper text.

## Workflow

1. **Resolve the period.** Convert relative dates to absolute inclusive dates.
   Use the latest *completed* ISO week unless the user explicitly requests the
   current partial week.
2. **Choose the mode.** Read `references/editorial-modes.md`.
   - Use `paperscope-editorial` when the user supplies the PaperScope-style
     reference, asks for its style, or explicitly wants strong-opinion Chinese
     technology-media writing. Read `references/paperscope-editorial.md`.
   - Use `publication-grade` for other detailed visual public-account articles.
   - Use `research-intel` only for explicitly concise/internal output.
3. **Freeze the source data.** From this skill directory run:

   ```bash
   python3 scripts/fetch_hf_week.py \
     --week 2026-W24 \
     --output-dir /absolute/path/to/hf-week-2026-W24
   ```

   For custom dates use `--start YYYY-MM-DD --end YYYY-MM-DD`. Preserve both
   `source.json` and `papers.json`; never silently replace them mid-draft.
4. **Triage the whole corpus.** Classify every normalized record at a coarse
   level using title, abstract, keywords, and links. Record the population and
   numerator behind every count or percentage.
5. **Build a diverse shortlist.** Combine popularity, technical novelty,
   practical relevance, open artifacts, and theme coverage. Do not select only
   by upvotes. Include counterexamples that could weaken the headline.
6. **Deep-read representatives.** For each paper used substantively, verify the
   mechanism, result, limitation, and artifact links against its HF page or
   original paper. Do not infer affiliations from author names or email
   domains.
   For `publication-grade`, deep-read 8–12 papers and write at least 8 complete
   paper cards. For `paperscope-editorial`, deep-read enough papers to support
   exactly five themes and at least 10 full cards.
7. **Form themes bottom-up.** Prefer 3–5 themes that explain multiple papers.
   Broad trends require at least three papers from at least two independent
   groups; otherwise label them `weak signal`.
8. **Create a claim ledger.** Read `references/evidence-rules.md`. Mark each
   important statement as `DATA`, `PAPER`, `INFERENCE`, or `FORECAST`, with its
   source and confidence.
9. **Build the visual plan.** For `publication-grade` or
   `paperscope-editorial`, read
   `references/visual-workflow.md`. First select and collect native figures
   from official project pages, arXiv HTML, or the paper PDF. Create original
   cover/statistical visuals only after the paper-native visual plan exists.
   Include at least six attributed visuals.
10. **Draft from evidence.** Lead with the strongest supported observation, not
   the most dramatic possible headline. Include source links and a methodology
   note. Publication drafts must meet the depth requirements in
   `references/editorial-modes.md`; never shorten them merely because the
   period is partial.
11. **Render publication HTML.** Run `scripts/render_wechat.py` for
   `publication-grade` and `paperscope-editorial`.
12. **Audit before delivery.** Recompute arithmetic from `papers.json`, search
    for repeated paper names and conflicting numbers, verify denominators,
    soften unsupported causality, and ensure forecasts are visibly labeled.
    Then run `scripts/audit_publication.py` with the matching partial/complete
    profile. Do not deliver a failing publication bundle.
    For `paperscope-editorial`, also run `scripts/audit_editorial_style.py`.
    Run `scripts/audit_figure_sources.py` for every visual publication. Do not
    deliver if native-paper figures are below the required ratio or provenance
    fields are missing.
13. **Perform visual QA.** Open the generated HTML at a mobile-width viewport,
    inspect the full page, and fix overflow, unreadable charts, broken image
    paths, weak spacing, or repetitive visual rhythm.

## Required Deliverables

For `research-intel`, produce:

- `digest.md`: final Chinese article;
- `audit.md`: period, corpus size, selection method, exclusions, and claim
  ledger;
- preserved `source.json` and `papers.json`;

For `publication-grade` and `paperscope-editorial`, always produce:

- `digest.md`;
- `digest-wechat.html`;
- `audit.md`;
- `editorial.json`;
- `assets/manifest.json` and at least six visual assets;
- preserved `source.json` and `papers.json`;
- a rendered preview or screenshot used for visual QA.

If live fetching or paper verification fails, report the exact coverage gap and
produce a partial draft labeled as incomplete. Never fill gaps with plausible
numbers.
