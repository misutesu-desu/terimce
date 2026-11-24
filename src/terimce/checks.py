import re
from collections import Counter
from typing import Callable, Iterable, List, Optional

from .glossary import Glossary
from .model import HATA, UYARI, Entry, Finding

PLACEHOLDER = re.compile(
    r"\{\{[^{}]*\}\}"                              # {{var}}
    r"|\{[^{}\s]*\}"                               # {0} {name}
    r"|%(?:\d+\$)?[-+0#]*\d*(?:\.\d+)?[sdifuxXc@]" # %s %1$d %.2f
    r"|\$[A-Za-z_][A-Za-z0-9_|]*\$"                # Paradox $VAR$
    r"|</?[A-Za-z][^<>]*>"                         # <color=red> </b>
    r"|\[/?[A-Za-z][^\[\]]*\]"                     # [b] [/color]
    r"|\\[nrt]"                                    # yazı olarak \n
)

END_PUNCT = {".", "!", "?", ":", "…"}


def placeholders(text: str) -> Counter:
    return Counter(m.group(0) for m in PLACEHOLDER.finditer(text))


def _end(text: str) -> Optional[str]:
    text = PLACEHOLDER.sub("", text).rstrip()
    if text.endswith("..."):
        return "…"
    if text and text[-1] in END_PUNCT:
        return text[-1]
    return None


def check_placeholders(e: Entry) -> Iterable[Finding]:
    src, tgt = placeholders(e.source), placeholders(e.target)
    missing = src - tgt
    extra = tgt - src
    if missing:
        yield Finding("degisken-eksik", HATA,
                      "çeviride eksik: " + " ".join(sorted(missing.elements())), e)
    if extra:
        yield Finding("degisken-fazla", HATA,
                      "kaynakta olmayan: " + " ".join(sorted(extra.elements())), e)


def check_newlines(e: Entry) -> Iterable[Finding]:
    if e.source.count("\n") != e.target.count("\n"):
        yield Finding("satir-sayisi", UYARI,
                      f"satır sayısı farklı: kaynak {e.source.count(chr(10)) + 1}, "
                      f"çeviri {e.target.count(chr(10)) + 1}", e)


def check_whitespace(e: Entry) -> Iterable[Finding]:
    if e.source[:1].isspace() != e.target[:1].isspace() or \
            e.source[-1:].isspace() != e.target[-1:].isspace():
        yield Finding("bosluk-kenar", UYARI, "baştaki ya da sondaki boşluk kaynakla uyuşmuyor", e)
    if "  " in e.target and "  " not in e.source:
        yield Finding("bosluk-cift", UYARI, "çeviride çift boşluk var", e)


def check_end_punctuation(e: Entry) -> Iterable[Finding]:
    a, b = _end(e.source), _end(e.target)
    if a != b and a is not None:
        ending = f"{b} ile bitiyor" if b else "noktalama işaretiyle bitmiyor"
        yield Finding("noktalama-son", UYARI, f"kaynak {a} ile bitiyor, çeviri {ending}", e)


def check_untranslated(e: Entry) -> Iterable[Finding]:
    if e.source == e.target and len(PLACEHOLDER.sub("", e.source).split()) >= 2:
        yield Finding("cevrilmemis", UYARI, "çeviri kaynakla aynı", e)


GENERIC_CHECKS: List[Callable[[Entry], Iterable[Finding]]] = [
    check_placeholders,
    check_newlines,
    check_whitespace,
    check_end_punctuation,
    check_untranslated,
]


def check_length(e: Entry, max_ratio: float) -> Iterable[Finding]:
    if len(e.source) >= 4 and len(e.target) > len(e.source) * max_ratio:
        yield Finding("uzunluk", UYARI,
                      f"çeviri kaynağın {len(e.target) / len(e.source):.1f} katı uzun", e)


def check_glossary(e: Entry, glossary: Glossary) -> Iterable[Finding]:
    target = glossary.lower(e.target)
    for term in glossary.matches(e.source):
        # Önce kabul edilenlere bak: kaçınılan "başarı", önerilen "başarım" ile başlıyor.
        if any(glossary.contains(target, w) for w in term.accepted()):
            continue
        avoided = [w for w in term.avoid if glossary.contains(target, w)]
        if avoided:
            yield Finding("terim-kacin", HATA,
                          f"{term.en[0]}: {avoided[0]} yerine {term.target} kullan", e)
        else:
            yield Finding("terim-eksik", UYARI,
                          f"{term.en[0]} için sözlükte {term.target} var", e)


def run(entries: Iterable[Entry], lang_checks, glossary: Optional[Glossary] = None,
        max_ratio: Optional[float] = None, ignore: Iterable[str] = ()) -> List[Finding]:
    ignored = set(ignore)
    findings: List[Finding] = []
    for e in entries:
        if not e.target.strip():
            continue
        for check in list(GENERIC_CHECKS) + list(lang_checks):
            findings.extend(check(e))
        if max_ratio:
            findings.extend(check_length(e, max_ratio))
        if glossary is not None:
            findings.extend(check_glossary(e, glossary))
    return [f for f in findings if f.code not in ignored]
