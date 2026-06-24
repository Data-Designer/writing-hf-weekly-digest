# Editorial modes

## Mode selection

| Mode | Use for | Default length | Voice |
|---|---|---:|---|
| `research-intel` | technical teams, investors, researchers, internal briefings | 2,000–4,000 Chinese characters | restrained, compact, evidence-led |
| `publication-grade` | article references, public accounts, illustrated newsletters, publishable drafts | complete week: 10,000–18,000 non-whitespace characters; 3-day partial week: 7,000–14,000 | vivid, detailed, visual, and explicit about inference |
| `paperscope-editorial` | the supplied PaperScope reference, strong-opinion tech-media columns, “same style” requests | complete week: 15,000–20,000; partial week: 12,000–17,000 | decisive, conversational, thesis-driven, high-rhythm |

## `research-intel` structure

1. **Title:** describe the strongest supported change; avoid declaring an era
   over from a single week.
2. **Executive summary:** three findings, one sentence each.
3. **Data snapshot:** dates, total papers, analyzed subset, upvote distribution,
   artifact availability, and comparison period if available.
4. **Three to five themes:** for each theme include:
   - what changed;
   - evidence from multiple papers;
   - one or two representative papers;
   - technical mechanism;
   - limitation or counter-signal;
   - practical implication.
5. **What to watch next week:** observable indicators, not confident prophecy.
6. **Methodology and references.**

## `publication-grade` requirements

These are completion gates, not aspirations:

- deep-read 8–12 representative papers;
- include at least 8 full paper cards;
- include at least 8 explicit `🤔 真正的 insight` passages;
- include 3–5 narrative themes;
- include at least 6 attributed visuals;
- include an original cover, two data charts, one synthesis diagram, and two
  paper-mechanism or source-backed visuals;
- generate both Markdown and WeChat HTML;
- pass `audit_publication.py`;
- inspect the rendered mobile layout before delivery.

Do not count decorative emoji, tables, or horizontal rules as visuals. A partial
week changes the certainty and length range, not the need for depth.

## `paperscope-editorial` requirements

Read `paperscope-editorial.md`. In addition to all publication deliverables:

- use exactly five numbered themes;
- repeat the complete six-part editorial engine for every theme;
- include at least ten paper cards and ten real editorial insights;
- use at least four forward transitions;
- finish with action list, three questions, summary, quotations, and “关于这篇”;
- pass `audit_editorial_style.py`.

## `publication-grade` structure

1. **Headline:** sharp but falsifiable.
2. **30-second opening:** the week’s strongest number plus the central tension.
3. **Two or three structural observations:** distinguish `DATA` from
   `INFERENCE`.
4. **Data snapshot:** show corpus and subset denominators.
5. **Three to five narrative themes:** use transitions and concrete examples.
6. **Representative paper cards:**

   ```markdown
   ### Paper title · upvotes N

   一句话：它解决了什么问题。

   - 💡 机制：paper-backed mechanism
   - 📈 结果：paper-backed result, including evaluation context
   - ⚠️ 局限：stated or carefully inferred limitation
   - 🛠 启示：practical editorial interpretation
   - 🤔 真正的 insight：clearly labeled editorial inference

   [HF](...) · [arXiv](...) · [GitHub](...)
   ```

7. **Action list:** only actions supported by the reviewed papers; avoid
   fabricated speedups, savings, or timelines.
8. **Technical synthesis:** connect the papers into one mechanism, workflow, or
   architecture diagram.
9. **What the headline does not explain:** counterexamples and quieter signals.
10. **Three questions or observable indicators for the next issue.**
11. **One-sentence conclusion and shareable quotations.**
12. **Methodology, correction promise, and references.**

## WeChat HTML guidance

- Use inline CSS only.
- Keep body text around 15px with 1.75–1.9 line height.
- Use one accent color and neutral backgrounds.
- Use real headings rather than converting the whole article into images.
- Preserve clickable HF, arXiv, GitHub, and project links.
- Do not hotlink paper figures without checking reuse rights; prefer official
  project media or original charts with attribution.
- Alternate visual and text-heavy sections; avoid more than 900 Chinese
  characters without a chart, figure, table, or paper-card break.
- Use captions that explain what the reader should notice, not merely repeat
  the image title.
- Keep every paper card self-contained enough to be screenshot and shared.
