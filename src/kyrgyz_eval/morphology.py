from __future__ import annotations

VOWELS = set("аоуыэеиөү")
VOICELESS = set("птксшчхфцщ")

LOW_VOWELS = ["а", "о", "е", "ө"]
HIGH_VOWELS = ["ы", "у", "и", "ү"]

LOW_BY_VOWEL = {
    "а": "а", "ы": "а", "о": "о", "у": "а",
    "э": "е", "е": "е", "и": "е", "ө": "ө", "ү": "ө",
}
HIGH_BY_VOWEL = {
    "а": "ы", "ы": "ы", "о": "у", "у": "у",
    "э": "и", "е": "и", "и": "и", "ө": "ү", "ү": "ү",
}

VOICING = {"п": "б", "к": "г"}
IOTATION = (("йу", "ю"), ("йа", "я"))

CASES = ("genitive", "dative", "accusative", "locative", "ablative")
POSSESSIVES = ("poss_1sg", "poss_2sg", "poss_3sg")

FEATURE_LABELS_KY = {
    "plural": "көптүк",
    "genitive": "илик жөндөмө",
    "dative": "барыш жөндөмө",
    "accusative": "табыш жөндөмө",
    "locative": "жатыш жөндөмө",
    "ablative": "чыгыш жөндөмө",
    "poss_1sg": "«менин» таандык",
    "poss_2sg": "«сенин» таандык",
    "poss_3sg": "«анын» таандык",
}


def _last_vowel(stem: str) -> str:
    for ch in reversed(stem):
        if ch in VOWELS:
            return ch
    raise ValueError(f"no vowel in stem: {stem}")


def _low(stem: str, force: str | None = None) -> str:
    return force if force is not None else LOW_BY_VOWEL[_last_vowel(stem)]


def _high(stem: str, force: str | None = None) -> str:
    return force if force is not None else HIGH_BY_VOWEL[_last_vowel(stem)]


def _orth(form: str) -> str:
    for src, dst in IOTATION:
        form = form.replace(src, dst)
    return form


def _ends_in_vowel(stem: str) -> bool:
    return stem[-1] in VOWELS


def _voice_final(stem: str) -> str:
    last = stem[-1]
    if last in VOICING:
        return stem[:-1] + VOICING[last]
    return stem


def _initial_two_way(stem: str, voiced: str, voiceless: str) -> str:
    return voiceless if stem[-1] in VOICELESS else voiced


def _initial_three_way(stem: str, sonorant: str, voiced: str, voiceless: str) -> str:
    if _ends_in_vowel(stem) or stem[-1] in "рй":
        return sonorant
    if stem[-1] in VOICELESS:
        return voiceless
    return voiced


def _initial_after_vowel(stem: str, after_vowel: str, voiced: str, voiceless: str) -> str:
    if _ends_in_vowel(stem):
        return after_vowel
    if stem[-1] in VOICELESS:
        return voiceless
    return voiced


def plural(stem: str, force=None, irregular: str | None = None) -> str:
    if irregular and force is None:
        return irregular
    c = _initial_three_way(stem, "л", "д", "т")
    return _orth(stem + c + _low(stem, force) + "р")


def genitive(stem: str, force=None) -> str:
    c = _initial_after_vowel(stem, "н", "д", "т")
    return _orth(stem + c + _high(stem, force) + "н")


def dative(stem: str, force=None) -> str:
    c = _initial_two_way(stem, "г", "к")
    return _orth(stem + c + _low(stem, force))


def accusative(stem: str, force=None) -> str:
    c = _initial_after_vowel(stem, "н", "д", "т")
    return _orth(stem + c + _high(stem, force))


def locative(stem: str, force=None) -> str:
    c = _initial_two_way(stem, "д", "т")
    return _orth(stem + c + _low(stem, force))


def ablative(stem: str, force=None) -> str:
    c = _initial_two_way(stem, "д", "т")
    return _orth(stem + c + _low(stem, force) + "н")


def poss_1sg(stem: str, force=None) -> str:
    if _ends_in_vowel(stem):
        return stem + "м"
    return _orth(_voice_final(stem) + _high(stem, force) + "м")


def poss_2sg(stem: str, force=None) -> str:
    if _ends_in_vowel(stem):
        return stem + "ң"
    return _orth(_voice_final(stem) + _high(stem, force) + "ң")


def poss_3sg(stem: str, force=None) -> str:
    if _ends_in_vowel(stem):
        return _orth(stem + "с" + _high(stem, force))
    return _orth(_voice_final(stem) + _high(stem, force))


GENERATORS = {
    "plural": plural,
    "genitive": genitive,
    "dative": dative,
    "accusative": accusative,
    "locative": locative,
    "ablative": ablative,
    "poss_1sg": poss_1sg,
    "poss_2sg": poss_2sg,
    "poss_3sg": poss_3sg,
}


def inflect(stem: str, feature: str, irregular: str | None = None) -> str:
    if feature == "plural":
        return plural(stem, irregular=irregular)
    return GENERATORS[feature](stem)


FILL_ORDER = ("plural", "accusative", "genitive", "dative", "locative", "ablative", "poss_1sg", "poss_3sg")

LOW_FEATURES = {"plural", "dative", "locative", "ablative"}


def distractors(stem: str, feature: str, n: int = 3) -> list[str]:
    fn = GENERATORS[feature]
    correct = inflect(stem, feature)
    pool: list[str] = []

    for vowel in (LOW_VOWELS if feature in LOW_FEATURES else HIGH_VOWELS):
        form = fn(stem, force=vowel)
        if form != correct and form not in pool:
            pool.append(form)

    for other in FILL_ORDER:
        if len(pool) >= n:
            break
        if other == feature:
            continue
        form = inflect(stem, other)
        if form != correct and form not in pool:
            pool.append(form)

    return pool[:n]
