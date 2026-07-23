# Paper draft

`main.tex` is the working draft, now filled with the real numbers from this repo. It
compiles with plain LaTeX; for submission, swap the preamble for the venue's style
file.

## How to compile

No local LaTeX is needed. Upload `main.tex`, `refs.bib`, and the figures to
[Overleaf](https://overleaf.com) (New Project -> Upload). The figures are referenced
at `../results/report/*.png`, so either keep that relative layout or move the four
PNGs next to `main.tex` and drop the `../results/report/` prefix.

Figures used:
- `results/report/model_category_heatmap.png`
- `results/report/generated_by_feature.png`
- `results/report/mcq_four_models.png`
- (optional) `results/report/finetune_scaling.png`, `accuracy_by_category.png`

## What is written vs. still TODO

Filled with real results: Abstract, Introduction, Benchmark Construction (except
agreement), Experimental Setup, Results, Analysis, rule engine and data section,
Fine-Tuning, Limitations, Conclusion.

Still TODO, and why:
1. **Related Work** — a stub. Needs an actual literature review; it decides whether
   the contribution reads as novel. This is reading you have to do.
2. **Inter-annotator agreement** — needs 2--3 more native speakers to check the answer
   keys independently, reported as Cohen's or Fleiss' kappa. Biggest reviewer target.
3. **Model versions and dates** — fix the exact version strings and access dates.
4. **More frontier models** — adding Gemini/Claude to the benchmark would show the
   dissociation is not provider-specific.
5. **`refs.bib`** — empty; fill as Related Work is written.

## Targets

| venue | fit | notes |
|---|---|---|
| SIGTURK (ACL workshop) | best | Turkic-specific, exactly this topic |
| LoResMT | strong | low-resource languages |
| Field Matters | strong | field linguistics and NLP |
| NeurIPS workshops | possible | favour method novelty; lead with the finding |
| LREC / COLING | reach | needs the expanded benchmark and agreement |

Check each call for papers for current deadlines and page limits.

## Framing

The contribution that carries the paper is the **knowledge--grammar dissociation**:
models answer questions about Kyrgyz well while failing to produce its morphology, a
single aggregate score hides it, and the gap is learnable rather than intrinsic. Lead
with that in the abstract and introduction; use the fine-tuning result to show the gap
is fixable.
