# PaperScope editorial mode

Use this mode when the user provides the PaperScope-style reference article,
asks for the same editorial style, or wants a sharp Chinese technology-media
column rather than a balanced research brief.

## Core editorial promise

Do not merely summarize papers. Use the week's papers to make one arguable
claim about where the field is moving, then defend it through data, mechanisms,
counter-signals, and practical consequences.

The article should feel like an editor has read the whole week and decided what
the reader must care about.

## Opening engine

Use this sequence:

1. A bold title stating the central interpretation.
2. A one-line deck: corpus size, number of themes, and the special value offered.
3. A “30 seconds” heading.
4. A visible contradiction:
   - what product/news feeds appeared to say;
   - what the paper corpus actually shows.
5. Two or three short paragraphs using constructions such as:
   - “不是A，是B。”
   - “票数掩盖了真正的信号。”
   - “这不是统计噪声，是……”
6. Three structural observations before the data snapshot.

Move methodology, incomplete-week warnings, and evidence caveats into a compact
opening badge and the final “关于这篇” section. Do not let them become the
opening argument.

## Five-theme engine

Create exactly five numbered sections. Every section must contain:

```markdown
## 01

## Theme title

判断：one sharp sentence.

### 为什么这件事现在发生

Explain the timing and shared conditions.

### 代表论文

[two or three full paper cards]

### 🔍 技术综观

Synthesize the mechanism from a different angle.

### 💼 落地实战

场景一：reader role/problem。 → concrete action.
场景二：reader role/problem。 → concrete action.

[forward transition ending in ↓]
```

Do not replace “为什么现在发生” with a generic introduction. Do not replace
“技术综观” with another paper summary. Do not replace “落地实战” with vague
advice.

## Paper-card voice

Each card contains:

- one-sentence positioning;
- `💡 机制`;
- `📈 结果`;
- `⚠️ 局限`;
- `🛠 你能学到什么`;
- `🤔 真正的 insight`.

The final insight is not a second abstract. It should answer one of:

- what uncomfortable fact does the paper expose?
- why is its vote count misleading?
- what will product teams get wrong if they ignore it?
- what research direction does its mechanism unlock?
- what part of the paper title is less important than the implementation?

Use direct language. Examples of the *kind* of move, not reusable sentences:

- “真正值得看的不是X，是Y。”
- “这篇暴露了一个被忽略的脏秘密：……”
- “票数低估了它，因为……”
- “产品团队最容易抄错的是……”

## Rhythm

- Alternate evidence-heavy paragraphs with short judgment paragraphs.
- Use arrows for actionable transformations and transitions.
- Address the reader by role: product PM, founder, researcher, model engineer,
  infrastructure team.
- End each theme by creating curiosity for the next one.
- Use strong language only when the article can show the supporting evidence.
- Avoid academic filler: “值得注意的是,” “在一定程度上,” “本文认为.”

## Paper figures

The body should look like a paper-reading column, not a consulting deck.

- Use the paper's own framework/overview figure near the first major card in
  each theme.
- Use result plots or qualitative examples when the text discusses those exact
  findings.
- Preserve original figure identity and caption in the manifest; write a
  shorter Chinese article caption beneath it.
- Keep original editorial graphics for cover, corpus snapshot, and one
  cross-paper summary only.
- Do not replace available paper figures with redrawn mechanism diagrams merely
  for visual consistency.

## Closing engine

After the five themes, include:

1. `📋 本周可以做什么：8条行动清单`
2. `给你的三个思考问题`
3. `一句话总结`
4. `💬 五句可以直接截图发X/朋友圈的金句`
5. `关于这篇` with dates, frozen data, method, corrections, and limitations
6. canonical paper links

## Originality boundary

Match the editorial mechanics and energy, not the reference article's exact
phrasing. Do not copy its jokes, sentences, branded labels, conclusions, or
images. Build the argument from the current frozen corpus.
