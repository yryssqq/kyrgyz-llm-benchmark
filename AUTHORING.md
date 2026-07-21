# Writing benchmark items

This is the guide for filling in `data/items.json`, the one part of the project that has to be written by a native speaker.

## Format

`data/items.json` is a JSON list. Each item looks like this:

```json
{
  "item_id": "vh_001",
  "category": "vowel_harmony",
  "difficulty": "easy",
  "question": "«китеп» сөзүнүн көптүк түрү кайсы?",
  "options": ["китептер", "китеплер", "китептар", "китеплар"],
  "answer_index": 0,
  "explanation": "The final syllable is front, so the suffix must be -тер."
}
```

Fields:

| field | meaning |
|---|---|
| `item_id` | unique ID, conventionally `<category prefix>_001` |
| `category` | one of the 8 categories below |
| `difficulty` | `easy` / `medium` / `hard` |
| `question` | the question itself, in Kyrgyz |
| `options` | exactly 4 options, all distinct |
| `answer_index` | index of the correct option: `0`, `1`, `2`, or `3` |
| `explanation` | why that answer is correct (write this in English) |

Questions and options are in Kyrgyz because that is what is being tested. Everything else (explanations, IDs, documentation) is in English, so the benchmark stays readable to reviewers who do not speak Kyrgyz.

`explanation` does not affect scoring, but it is a valuable part of the dataset: the error analysis in the README is built from these.

## Categories

| category | what it tests | example idea |
|---|---|---|
| `vowel_harmony` | үндөштүк: selecting the suffix form the vowels require | correct plural or case ending |
| `morphology` | stacking several suffixes in sequence | case + possessive + number on one word |
| `syntax` | whether a sentence is well-formed | which of 4 sentences is grammatical |
| `lexical_semantics` | word meaning, synonymy, polysemy | which word fits the context |
| `idioms` | макал-лакап and fixed expressions | what an expression means, non-literally |
| `culture` | Kyrgyz-specific knowledge | Manas, traditions, history, geography |
| `translation` | whether meaning survives ky↔ru/en | which translation preserves the meaning |
| `orthography` | ң, ө, ү and other easy-to-miss spellings | which spelling is correct |

Target: 8 items per category, 64 total.

## What makes an item good

**The difficulty belongs in the language, not the wording.** Any native speaker should understand the question in a couple of seconds. The challenge should be that the model does not know Kyrgyz morphology, not that the question is convoluted.

**Distractors have to be plausible.** If the 3 wrong options are obvious nonsense, a model can pick the right one without knowing any Kyrgyz. A good distractor is exactly the mistake someone without a feel for vowel harmony would make: `китеплер` instead of `китептер`.

**One item, one phenomenon.** Do not combine vowel harmony and idiom knowledge in a single question. If you do, it is impossible to tell what the model actually failed at, and the per-category breakdown loses its meaning.

**Vary the position of the correct answer.** If the answer is always first, a model that always replies "1" scores 100%. The validator checks this and warns you.

**Resolve anything you are unsure about.** If you are not certain of the correct answer, either drop the item or check it against a dictionary. A single disputed item out of 64 undermines the whole benchmark, because the first question any reviewer asks is whether the answer key is right.

## Checking your work

```bash
python validate_items.py
```

This checks the structure (unique IDs, exactly 4 options, valid `answer_index`, no duplicate options), reports how many items each category has, and warns if correct answers cluster in one position.

Run it as you go, not only at the end.

## About `items.example.json`

`data/items.example.json` holds 3 items that exist **only to demonstrate the format**. They were not written by a native speaker, so they are not part of the benchmark and should not be treated as a model for content. Write your items in `data/items.json`.
