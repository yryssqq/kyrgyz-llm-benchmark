# kyrgyz-llm-benchmark

A small benchmark for how well LLMs handle Kyrgyz.

## Abstract

Kyrgyz has ~5M speakers and barely shows up in LLM evaluation. Most "multilingual" numbers for low-resource Turkic languages come from machine-translated test sets, which test the translator as much as the model. Here every question is written by hand by a native speaker and targets a specific thing a model tends to get wrong: vowel harmony, suffix stacking, idioms, spelling of ң/ө/ү, and cultural knowledge.

## Methodology

Questions are 4-option multiple choice in Kyrgyz; the model replies with one digit. Digits instead of A/B/C/D avoid Latin/Cyrillic lookalike issues. If a reply parses to neither a digit nor an exact option, it counts as wrong but is tracked as `unparseable` separately. Random guessing gets 25%, and scores are checked against that baseline with a one-sided binomial test. The validator enforces 4 distinct options and a valid key, and flags if correct answers cluster in one position; in this set the answer is spread exactly 25% per slot.

## Empirical Results & Key Findings

64 questions, 8 categories, run on two OpenAI models.

| model | score | vs. chance |
|---|---|---|
| gpt-4o | 59/64 (92%) | p ≈ 6e-30 |
| gpt-4o-mini | 55/64 (86%) | p ≈ 2e-24 |

![accuracy by model and category](results/report/model_category_heatmap.png)

Both models are strong overall. The interesting part is the split:

- Facts are easy. Idioms, vocabulary, translation, culture: ~100%.
- Grammar is hard. Morphology drops to **62%** (same for both models), vowel harmony to **75%**.

Two questions both models got wrong show it best. For `дос` + plural + possessive both answered `достарым`; the correct form is `досторум` (the rounded vowel forces rounded suffixes down the whole word). For the accusative of `китеп` both missed `китепти`. These are first-year grammar rules, not trivia.

So a single "90% on Kyrgyz" number hides the real gap: the model knows things about Kyrgyz but can't reliably inflect a noun. You only see it if you test morphology on its own.

## Categories

| category | tests |
|---|---|
| `vowel_harmony` | picking the suffix the vowels require |
| `morphology` | stacking case / possessive / number |
| `syntax` | which sentence is well-formed |
| `lexical_semantics` | word meaning, synonyms |
| `idioms` | fixed expressions, non-literal meaning |
| `culture` | Manas, traditions, history, geography |
| `translation` | meaning across ky/ru/en |
| `orthography` | ң, ө, ү and easy-to-miss spellings |

## Morphology generator

Since morphology is where models fail, `morphology.py` encodes Kyrgyz noun inflection as rules: vowel harmony (4-way), consonant assimilation, and final-obstruent voicing. Given a list of stems it produces plural, five cases, and three possessives, plus multiple-choice items whose wrong options are real harmony violations. Its rules are unit-tested against the hand-verified forms in the benchmark.

```bash
python generate_morphology.py --sample 30      # print forms to eyeball
python generate_morphology.py                  # write training pairs + MCQ items
```

Stems come from the Apertium Kyrgyz dictionary ([apertium-kir](https://github.com/apertium/apertium-kir), GPL). `extract_stems.py` pulls common nouns out of its `lexc` file, drops entries the maintainers flagged as uncertain, drops Russian loanwords by orthography, and samples a set balanced across all sixteen combinations of vowel-harmony class and final-segment type, so no cell of the paradigm is starved.

```bash
git clone https://github.com/apertium/apertium-kir /tmp/apertium-kir
python extract_stems.py /tmp/apertium-kir/apertium-kir.kir.lexc
python stem_coverage.py data/stems_apertium.txt
```

Apertium's own two-level rules were also used to check the engine. Its `N Desonorisation` rule confirmed that the genitive and accusative onset is `д` rather than `н` after stems ending in `й`, `л`, `з`, `р`, which corrected a bug the fine-tuned model had been flagging by disagreeing with the gold forms.

This turns a small verified stem list into thousands of items, for expanding the test set and for fine-tuning experiments. A native speaker still checks the stem list and a sample of the output; the rounding-harmony edge cases are the ones to watch.

`finetune_qlora.ipynb` uses the generator to teach an open model this morphology: it holds out a fifth of the stems, trains a QLoRA adapter on the rest, and scores the model on the held-out words before and after. Runs on a free Kaggle GPU.

The same experiment runs locally on Apple Silicon with MLX, no cloud account needed:

```bash
python export_mlx_data.py
python -m mlx_lm lora --model mlx-community/Qwen2.5-0.5B-Instruct-4bit \
  --train --data mlx_data --iters 400 --batch-size 4 --num-layers 8 \
  --mask-prompt --adapter-path adapters
python eval_local.py                      # base
python eval_local.py --adapter adapters   # fine-tuned
```

On 22 training stems, Qwen2.5-0.5B goes from 0% to 16.7% on held-out words. The base model does not inflect at all, it echoes the stem; after training it produces inflected forms but often picks the wrong harmony class. The stem list is the bottleneck, not the method.

## Files

```
data/items.json         the benchmark
data/stems.example.txt  stem list for the generator
src/kyrgyz_eval/         loading, prompting, scoring, stats, morphology
validate_items.py       check the item file
run_benchmark.py        items -> model -> results/*.csv
analyze.py              results -> summary.json + charts
generate_morphology.py  stems -> training pairs + generated items
```

## Run

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export OPENAI_API_KEY=...

python run_benchmark.py --provider openai --model gpt-4o
python analyze.py results/gpt-4o.csv
```

Adding questions: see [AUTHORING.md](AUTHORING.md). Tests: `pytest`.

## License

MIT
