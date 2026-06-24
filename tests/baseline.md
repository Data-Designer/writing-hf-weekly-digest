# Baseline observations

## Scenario

> Write a Chinese weekly analysis of all Hugging Face Daily Papers from
> 2026-06-08 through 2026-06-14. Identify major themes, select representative
> papers, explain their practical implications, and make the article engaging
> enough for a WeChat public account.

## Observed failure modes without this skill

The supplied reference article is polished, but it exposes failure modes a
general-purpose agent can reproduce without explicit controls:

1. **Internal numeric contradiction:** `LatentSkill` is labeled `upvotes 62`
   and later described as having `458` votes.
2. **Unbounded denominator:** percentages such as “69%” alternate between the
   full 239-paper corpus and a Top-35 subset.
3. **Inference stated as fact:** “industrial labs have completely moved model
   training into closed source” is not directly established by one quiet week.
4. **Forecast stated too confidently:** claims that named companies “will all
   follow within three months” are predictions, not observed facts.
5. **Causal claims without evidence:** low publication counts are used to infer
   why academia changed direction without alternative explanations.
6. **Upvote/quality conflation:** popularity is treated as evidence of technical
   importance in some passages and dismissed in others.
7. **Paper-detail risk:** mechanism, limitation, affiliation, and performance
   claims can be copied from summaries without checking the paper.

## Acceptance checks

- Every percentage names its population and numerator.
- Every representative-paper number is drawn from one frozen data snapshot.
- Facts, paper claims, editorial inference, and forecasts use distinct labels.
- Broad trend claims require multiple papers and multiple independent groups.
- Every representative paper is checked against its paper page or original text.
- Missing affiliation data remains unknown rather than being inferred.
- The final audit recomputes counts and scans for contradictory numbers.

