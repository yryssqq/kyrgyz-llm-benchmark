#!/usr/bin/env python3
from __future__ import annotations

import argparse
import glob
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from kyrgyz_eval import morphology as m

LEXC_ENTRY = re.compile(r'^([а-яёөүң]+):([^ \t]+)\s+N-INFL\s*;(?:\s*!\s*"?([^"!]*)"?)?', re.IGNORECASE)
CYRILLIC = re.compile(r"^[а-яёөүң]+$")

RUSSIAN_ONLY = set("вфцщьъё")
CONSONANTS = set("бгдjжзйклмнңпрстчшх")
BACK_VOWELS = set("аоуы")
FRONT_VOWELS = set("еиэөү")

INTERNATIONAL_SUFFIXES = (
    "изм", "ист", "ия", "ий", "лог", "метр", "скоп", "тор", "сор",
    "ент", "ант", "аж", "ура", "ика",
)

INTERNATIONAL_WORDS = {
    "абонент", "аборт", "агарот", "атлет", "барит", "батир", "битон", "гарнизон",
    "гестапо", "грамм", "демагог", "догма", "доктур", "дума", "идеал", "интернат",
    "кабинет", "казино", "канал", "катион", "корпус", "кран", "материал",
    "миллиард", "монолог", "нектар", "неон", "отряд", "парк", "пилот", "пионер",
    "планета", "помидор", "принтер", "рентген", "ресурс", "сайт", "сезон",
    "семестр", "синдикат", "склероз", "спонсор", "танго", "театр", "телескоп",
    "том", "тост", "турнир", "хор", "эталон", "этил", "юбилей", "юмор", "электр",
    "эпос", "бактерия", "интернет", "радио", "футбол", "автобус", "поезд",
    "абсолют", "база", "балкон", "герб", "гипс", "гормон", "дубляж", "душ",
    "жилет", "жюри", "заказ", "зал", "инжинер", "кадр", "кекс", "колхоз",
    "командо", "кит", "литр", "майор", "менеджер", "министр", "мэр", "радар",
    "рапорт", "ринг", "сюрприз", "тендер", "тип", "тиски", "указ", "гезит",
    "жокей", "хоккей", "оркестр", "музей", "коридор", "период", "сенат",
    "сироп", "солдат", "союз", "тенор", "террор", "туалет", "хирург", "ядро",
    "бампер", "бензин", "галош", "гарнитур", "депозит", "диплом", "импорт",
    "йод", "каникул", "карантин", "кило", "легионер", "лимит", "лорд",
    "макияж", "микроб", "минибус", "онлайн", "реестр", "ритм", "актер",
    "акушер", "аккорд", "электрон", "эксперт", "пол", "обо", "бюджет", "гол",
    "дилер", "имидж", "комсомол", "паром", "режим", "термин", "зона", "баланс",
    "род", "раса", "бокс", "старт", "экран", "аренда", "билет", "доллар",
    "банк", "район", "офис", "процент", "фонд", "сом",
    "январь", "февраль", "март", "апрель", "июнь", "июль", "август",
    "сентябрь", "октябрь", "ноябрь", "декабрь",
    "лидер", "рейтинг", "рынок", "тонна", "куб", "кубок", "курс", "округ",
    "облус", "пул", "офис", "митинг", "лагер", "штаб", "смена",
}

PLURAL_SUFFIXES = tuple(c + v + "р" for c in "лдт" for v in "аоеө")

ENDINGS = ["vowel", "sonorant", "voiced", "voiceless"]


def looks_plural(word: str, lexicon: set[str]) -> bool:
    for suffix in PLURAL_SUFFIXES:
        if word.endswith(suffix) and len(word) - len(suffix) >= 2:
            if word[: -len(suffix)] in lexicon:
                return True
    return False
HARMONIES = [("back", "unrounded"), ("back", "rounded"), ("front", "unrounded"), ("front", "rounded")]


def is_internally_harmonic(word: str) -> bool:
    vowels = [c for c in word if c in m.VOWELS]
    if not vowels:
        return False
    return all(v in BACK_VOWELS for v in vowels) or all(v in FRONT_VOWELS for v in vowels)


def looks_borrowed(word: str) -> bool:
    if word in INTERNATIONAL_WORDS or word.endswith(INTERNATIONAL_SUFFIXES):
        return True
    if len(word) > 1 and word[0] in CONSONANTS and word[1] in CONSONANTS:
        return True
    if not is_internally_harmonic(word) or "э" in word[1:]:
        return True
    return False


def acceptable(word: str, min_len: int, max_len: int) -> bool:
    if not CYRILLIC.match(word) or not min_len <= len(word) <= max_len:
        return False
    if RUSSIAN_ONLY & set(word) or looks_borrowed(word):
        return False
    try:
        m._last_vowel(word)
    except ValueError:
        return False
    return True


def harmony_of(stem: str) -> tuple[str, str]:
    vowel = m._last_vowel(stem)
    return ("back" if vowel in BACK_VOWELS else "front",
            "rounded" if vowel in "оуөү" else "unrounded")


def ending_of(stem: str) -> str:
    last = stem[-1]
    if last in m.VOWELS:
        return "vowel"
    if last in "рй":
        return "sonorant"
    if last in m.VOICELESS:
        return "voiceless"
    return "voiced"


def load_apertium(path: Path) -> dict[str, str]:
    found = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("!"):
            continue
        match = LEXC_ENTRY.match(line)
        if not match:
            continue
        lemma, stem, gloss = match.group(1), match.group(2), (match.group(3) or "").strip()
        if lemma != stem or "%" in stem:
            continue
        if "FIXME" in gloss.upper() or "CHECK" in gloss.upper() or "?" in gloss:
            continue
        found.setdefault(lemma, gloss)
    return found


def load_ud(directory: Path) -> Counter:
    counts: Counter = Counter()
    for filename in glob.glob(str(directory / "**" / "*.conllu"), recursive=True):
        for line in open(filename, encoding="utf-8"):
            if line.startswith("#") or not line.strip():
                continue
            parts = line.split("\t")
            if len(parts) > 3 and parts[3] == "NOUN":
                counts[parts[2].lower()] += 1
    return counts


def load_wiktionary(path: Path) -> dict[str, str]:
    found = {}
    with path.open(encoding="utf-8") as f:
        for line in f:
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue
            if entry.get("lang_code") != "ky" or entry.get("pos") != "noun":
                continue
            word = entry.get("word", "").lower()
            if not word or word in found:
                continue
            glosses = [g for sense in entry.get("senses", []) for g in sense.get("glosses", [])]
            found[word] = glosses[0] if glosses else ""
    return found


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apertium", help="path to apertium-kir.kir.lexc")
    parser.add_argument("--ud", help="directory containing UD .conllu files")
    parser.add_argument("--wiktionary", help="path to kaikki Kyrgyz .jsonl")
    parser.add_argument("--out", default="data/stems_multi.txt")
    parser.add_argument("--per-cell", type=int, default=20)
    parser.add_argument("--min-sources", type=int, default=2)
    parser.add_argument("--min-len", type=int, default=3)
    parser.add_argument("--max-len", type=int, default=8)
    args = parser.parse_args()

    apertium = load_apertium(Path(args.apertium)) if args.apertium else {}
    ud = load_ud(Path(args.ud)) if args.ud else Counter()
    wiktionary = load_wiktionary(Path(args.wiktionary)) if args.wiktionary else {}
    print(f"apertium {len(apertium)} | ud {len(ud)} | wiktionary {len(wiktionary)}")

    sources: dict[str, set[str]] = defaultdict(set)
    glosses: dict[str, str] = {}
    for word in apertium:
        sources[word].add("apertium")
        glosses.setdefault(word, apertium[word])
    for word in ud:
        sources[word].add("ud")
    for word in wiktionary:
        sources[word].add("wikt")
        if not glosses.get(word):
            glosses[word] = wiktionary[word]

    lexicon = set(sources)
    candidates = [
        w for w, srcs in sources.items()
        if len(srcs) >= args.min_sources
        and acceptable(w, args.min_len, args.max_len)
        and not looks_plural(w, lexicon)
    ]
    print(f"{len(candidates)} candidates in >= {args.min_sources} sources and passing filters")

    buckets: dict[tuple, list[str]] = defaultdict(list)
    for word in candidates:
        buckets[(harmony_of(word), ending_of(word))].append(word)

    selected: list[str] = []
    print(f"\n{'harmony':<24}" + "".join(f"{e:>12}" for e in ENDINGS))
    for harmony in HARMONIES:
        row = f"{harmony[0] + ' ' + harmony[1]:<24}"
        for ending in ENDINGS:
            pool = sorted(buckets[(harmony, ending)], key=lambda w: (-ud[w], -len(sources[w]), w))
            take = pool[:args.per_cell]
            selected.extend(take)
            row += f"{len(take):>12}"
        print(row)

    selected.sort()
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as f:
        f.write("# Kyrgyz noun stems attested in multiple independent resources.\n")
        f.write("# Sources: apertium-kir (GPL), Universal Dependencies Kyrgyz treebanks,\n")
        f.write("# and Wiktionary via kaikki.org. Ranked by corpus frequency, then balanced\n")
        f.write("# across vowel-harmony and final-segment classes.\n")
        f.write("# Columns after '#': gloss, sources, corpus frequency.\n#\n")
        for word in selected:
            note = f"{glosses.get(word, '')} [{'+'.join(sorted(sources[word]))}, freq {ud[word]}]"
            f.write(f"{word}  # {note.strip()}\n")

    covered = sum(1 for w in selected if ud[w] > 0)
    print(f"\nselected {len(selected)} stems ({covered} attested in the corpus) -> {out}")


if __name__ == "__main__":
    main()
