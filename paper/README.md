# Paper draft

`main.tex` is the working draft. It compiles with plain LaTeX as-is; for submission,
swap the preamble for the venue's style file.

## Targets

| venue | fit | notes |
|---|---|---|
| SIGTURK (ACL workshop) | best | Turkic-specific, exactly this topic |
| LoResMT | strong | low-resource languages |
| Field Matters | strong | field linguistics and NLP |
| NeurIPS workshops | possible | favour method novelty; frame the finding, not the dataset |
| LREC / COLING | reach | needs the full expanded benchmark |

Check each call for papers for current deadlines and page limits.

## What the draft still needs

1. **Scale**: expand the benchmark from 64 items toward 300-600.
2. **Inter-annotator agreement**: at least two more native speakers over the answer
   keys, reported as Cohen's or Fleiss' kappa. This is the biggest reviewer target.
3. **More models**: 6-10 across families and sizes, including open-weight models.
4. **Fine-tuning numbers**: fill Table 4 from the local MLX run.
5. **Related work**: the section is a stub; it decides whether the contribution reads
   as novel.
6. **Figures**: uncomment the heatmap include once paths are set.

## Framing advice

The contribution that carries the paper is not the benchmark itself but the
**knowledge-grammar dissociation**: models answer questions *about* Kyrgyz well while
failing to *produce* correct morphology, and a single aggregate score hides this.
Lead with that in the abstract and the introduction, and use the fine-tuning result
to show the gap is fixable rather than intrinsic.
