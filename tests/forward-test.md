# Forward test

## Prompt

> Use the skill to prepare a research-intelligence digest for ISO week
> 2026-W24, and identify the strongest supported opening observation.

## Live execution

Command:

```bash
python3 scripts/fetch_hf_week.py \
  --week 2026-W24 \
  --output-dir /tmp/hf-weekly-skill-live
```

Observed on 2026-06-24:

- resolved period: 2026-06-08 through 2026-06-14;
- raw API records: 238;
- normalized unique papers: 238;
- missing titles or Daily submission dates: 0;
- frozen top paper: `2606.09967`, ABot-Earth 0.5, 480 upvotes;
- frozen second paper: `2606.05405`, Agents' Last Exam, 360 upvotes;
- frozen MiniMax Sparse Attention count: 145 upvotes.

The representative paper IDs, titles, repositories, project pages, and current
upvotes were independently checked through `/api/papers/{id}`.

## Acceptance review

- **Complete-period resolution:** pass.
- **Raw and normalized snapshots preserved:** pass.
- **Pagination and deduplication:** pass.
- **Arithmetic reproducible from one snapshot:** pass.
- **Paper links available for deep reading:** pass.
- **Transient API connection handling:** pass; simulated URL failures are
  retried three times with bounded backoff.
- **Protection against mutable upvotes:** pass; the supplied reference article
  showed 462 upvotes for ABot-Earth, while the later frozen snapshot showed 480.
- **Protection against unsupported article numbers:** pass; the reference
  article stated 239 papers, while the current API snapshot returned 238. The
  skill requires reporting retrieval time rather than silently forcing the old
  count.
- **Fact/inference separation:** pass in instruction review.
- **Counter-signal requirement:** pass in instruction review.

## Result

The skill should open with a statement scoped to the frozen corpus, such as
“本期抓取到 238 篇 HF Daily Papers；Agent 评测和长上下文基础设施在高热度论文中形成明显聚类,” only after classification confirms the second clause. It should not open with “学术界卷模型的时代终结了” because one week of publication data does not establish that causal conclusion.
