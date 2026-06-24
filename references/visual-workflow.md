# Visual workflow

## Source priority

Use visuals in this order:

1. official project-page framework/overview image;
2. arXiv HTML figure with its original figcaption;
3. PDF page rendering and high-resolution figure crop using the `pdf` skill;
4. Hugging Face media or official repository asset;
5. original explanatory diagram only when no usable native figure exists.

**REQUIRED SUB-SKILLS:** Use `huggingface-papers` for canonical links and
project metadata. Use `pdf` when arXiv HTML/project media is unavailable. Use
browser inspection and local image viewing to verify relevance and readability.

For a publication article:

- at least 70% of non-cover visuals must be `paper-native`;
- all five themes need at least one native figure;
- at least five distinct papers must contribute figures;
- original visuals are limited to the cover, corpus statistics, and one
  cross-paper synthesis visual.

## Required visual set

For `publication-grade`, plan visuals before drafting:

1. **Cover:** original editorial title, subtitle, and date range.
2. **Corpus chart:** daily counts, artifact availability, or upvote
   distribution computed from `papers.json`.
3. **Theme chart:** paper count and engagement for the editorial themes; state
   when themes overlap.
4. **Synthesis diagram:** show how the week's papers form a workflow,
   architecture, failure chain, or decision tree.
5. **Paper-native figures:** framework, pipeline, result, or qualitative figures
   from the representative papers.

Run:

```bash
python3 scripts/build_visuals.py \
  --papers /absolute/bundle/papers.json \
  --editorial /absolute/bundle/editorial.json \
  --output-dir /absolute/bundle/assets
```

`editorial.json` must contain:

```json
{
  "title": "Issue title",
  "subtitle": "Issue subtitle",
  "period": "YYYY-MM-DD—YYYY-MM-DD",
  "themes": [
    {"name": "Theme", "papers": 4, "upvotes": 120}
  ],
  "pipeline": ["Failure", "State", "Simulation", "Learning"],
  "paper_diagrams": [
    {
      "paper_id": "2606.00000",
      "title": "Mechanism title",
      "subtitle": "What the paper changes",
      "steps": ["Input", "Mechanism", "Output"],
      "takeaway": "What readers should remember",
      "caption": "图4：Mechanism explanation. 来源：根据论文原理原创绘制。"
    }
  ]
}
```

## Collecting paper-native media

Create `figure-selection.json`, then run:

```bash
python3 scripts/collect_paper_figures.py \
  --selection /absolute/bundle/figure-selection.json \
  --assets-dir /absolute/bundle/assets \
  --manifest /absolute/bundle/assets/manifest.json
```

For arXiv HTML, specify a paper ID and `Figure N`; the collector matches the
original image and figcaption. For official project images, provide the
explicit image URL, project-page URL, figure name, and original alt/caption.

Every native manifest entry must include:

- `kind: paper-native`;
- numbered theme;
- paper ID;
- figure number/name;
- original caption;
- article caption;
- source page URL;
- original image URL;
- source type.

Run:

```bash
python3 scripts/audit_figure_sources.py /absolute/bundle
```

## Source-backed media

Use an existing paper/project image only when all are true:

- it materially improves understanding over an original diagram;
- the source is an official paper, project, repository, or HF media asset;
- the manifest records paper ID, source URL, local file, and caption;
- the article attributes it immediately below the image;
- the image is cropped or scaled for explanation, not used as decoration.

If reuse status is unclear, create an original explanatory diagram instead.
Never copy images from another newsletter or public-account article.

Do not select a paper image merely because it exists. Prefer Figure 1/framework,
then a result figure directly discussed in the paper card. Reject logos,
equations, unreadable tables, decorative banners, and figures that become
illegible at mobile width.

## Captions and accessibility

- Caption every image with `图N`, the point to notice, and its source.
- For paper-native figures, state the paper name and original Figure number.
- Render every local `assets/papers/` figure as a link to its high-resolution
  file and add a visible `点击查看高清原图` affordance.
- Write meaningful alt text.
- Use readable labels at mobile width; avoid dense legends and tiny axes.
- A semantically essential framework may remain compact in the article only
  when its high-resolution file is one click away; otherwise crop or replace it.
- Prefer 1080px-wide SVG or PNG assets.
- Make charts truthful: start quantitative axes at zero unless a justified
  exception is stated.

## Rendering and QA

Render:

```bash
python3 scripts/render_wechat.py \
  --input /absolute/bundle/digest.md \
  --output /absolute/bundle/digest-wechat.html
```

Audit:

```bash
python3 scripts/audit_publication.py /absolute/bundle \
  --profile publication-partial
```

Use `publication-complete` for a completed seven-day issue. After automation
passes, inspect the HTML at approximately 390px mobile width and verify:

- no horizontal overflow;
- charts and labels remain legible;
- images resolve locally;
- visual cadence breaks up long text;
- paper cards are visibly distinct;
- title, callouts, tables, and captions have sufficient contrast.
