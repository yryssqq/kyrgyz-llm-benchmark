# Paper draft

Two versions of the same paper:

- `main.tex` — readable working draft (named author, plain `article` class, GitHub link). Use this to read and edit.
- `neurips_submission.tex` — **anonymized** version formatted for the NeurIPS 2026 workshop **LP4FM** (Linguistic Principles for Foundation Models). Use this to submit.

Both share `refs.bib` and the same figures.

## Target venue

**LP4FM @ NeurIPS 2026** (Sydney). A near-exact topical fit: its scope explicitly covers low-resource languages and "how tokenization and morphological complexity shape capability", and "benchmarks beyond surface accuracy ... cross-linguistic competence".

- Deadline: **August 29, 2026**
- Length: short 4 pages / full 9 pages (references and appendices excluded)
- Non-archival, **double-blind** (anonymization mandatory)
- Backup venue: AI4GOOD @ NeurIPS 2026 (social-good framing).

## Compiling the NeurIPS submission

1. Get the official `neurips_2026.sty` (from the workshop site or the built-in Overleaf "NeurIPS 2026" template) and put it next to `neurips_submission.tex`.
2. Upload `neurips_submission.tex`, `refs.bib`, and the three figure PNGs to Overleaf.
3. The style is used in **anonymous** mode (`\usepackage{neurips_2026}`, no option), which prints "Anonymous Author(s)". For the camera-ready after acceptance, switch to `\usepackage[final]{neurips_2026}` and restore the author block, GitHub link, and acknowledgements.

## Anonymization checklist (done in `neurips_submission.tex`)

- [x] Author name and email removed (placeholder "Anonymous Author(s)").
- [x] GitHub link removed from Availability ("released upon acceptance").
- [x] No acknowledgements (they would deanonymize; add them only in the camera-ready).
- [ ] Before submitting, double-check the PDF for any remaining identifying text.

## How to compile the readable draft (`main.tex`)

No local LaTeX is needed. Upload `main.tex`, `refs.bib`, and the figures to
[Overleaf](https://overleaf.com) (New Project -> Upload). The figures are referenced
at `../results/report/*.png`, so either keep that relative layout or move the
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
