import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Dict, List, Optional

import yaml

PACKAGE_DIR = Path(__file__).resolve().parent
OPTIONAL_KEYS = {"alt", "avoid", "tags", "note"}


def data_dir() -> Path:
    bundled = PACKAGE_DIR / "sozluk"
    if bundled.is_dir():
        return bundled
    return PACKAGE_DIR.parent.parent / "sozluk"


@dataclass
class Term:
    en: List[str]
    target: str
    alt: List[str] = field(default_factory=list)
    avoid: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    note: str = ""
    path: Optional[Path] = None

    def accepted(self) -> List[str]:
        return [self.target] + self.alt


class GlossaryError(Exception):
    pass


def _as_list(value, what: str, path: Path) -> List[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    if isinstance(value, list) and all(isinstance(v, str) for v in value):
        return value
    raise GlossaryError(f"{path}: {what} yazı ya da yazı listesi olmalı")


def load_term(path: Path, lang: str) -> Term:
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as e:
        raise GlossaryError(f"{path}: YAML okunamadı: {e}") from e
    if not isinstance(data, dict):
        raise GlossaryError(f"{path}: dosya bir eşleme olmalı")
    unknown = set(data) - OPTIONAL_KEYS - {"en", lang}
    if unknown:
        raise GlossaryError(f"{path}: bilinmeyen alan: {', '.join(sorted(unknown))}")
    for key in ("en", lang):
        if not data.get(key):
            raise GlossaryError(f"{path}: {key} alanı boş ya da yok")
    if not isinstance(data[lang], str):
        raise GlossaryError(f"{path}: {lang} tek bir yazı olmalı, seçenekleri alt altına yaz")
    note = data.get("note") or ""
    if not isinstance(note, str):
        raise GlossaryError(f"{path}: note yazı olmalı")
    return Term(
        en=_as_list(data["en"], "en", path),
        target=data[lang],
        alt=_as_list(data.get("alt"), "alt", path),
        avoid=_as_list(data.get("avoid"), "avoid", path),
        tags=_as_list(data.get("tags"), "tags", path),
        note=note.strip(),
        path=path,
    )


class Glossary:
    def __init__(self, terms: List[Term], lower: Callable[[str], str]):
        self.terms = terms
        self.lower = lower
        self._patterns = [
            (re.compile(r"(?<![\w-])(?:" + "|".join(re.escape(w) for w in t.en)
                        + r")(?:s|es|d|ed|ing)?(?![\w-])", re.IGNORECASE), t)
            for t in terms
        ]

    @classmethod
    def load(cls, lang: str, lower: Callable[[str], str],
             directory: Optional[Path] = None) -> "Glossary":
        directory = directory or data_dir() / lang
        if not directory.is_dir():
            return cls([], lower)
        terms = [load_term(p, lang) for p in sorted(directory.glob("*.yml"))]
        return cls(terms, lower)

    def matches(self, source: str) -> List[Term]:
        return [t for pattern, t in self._patterns if pattern.search(source)]

    def contains(self, lowered_target: str, word: str) -> bool:
        # Kelimenin başı sınırda olmalı, sonuna ek gelebilir: "bekleme süresini" eşleşir.
        word = self.lower(word)
        variants = [word]
        # Tamlamada iyelik eki çoğulda düşer: "kare hızı" -> "kare hızları".
        if " " in word:
            stem = re.sub(r"s?[ıiuü]$", "", word)
            if stem != word and len(stem.rsplit(" ", 1)[1]) >= 3:
                variants.append(stem)
        return any(re.search(r"(?<!\w)" + re.escape(v), lowered_target) for v in variants)

    def search(self, query: str) -> List[Term]:
        q = self.lower(query)
        return [t for t in self.terms
                if any(q in self.lower(w) for w in t.en + t.accepted())]

    def problems(self) -> List[str]:
        out = []
        seen: Dict[str, str] = {}
        for t in self.terms:
            name = t.path.name if t.path else "?"
            for w in t.en:
                key = w.lower()
                if key in seen:
                    out.append(f"{t.path}: {w} zaten {seen[key]} içinde var")
                seen[key] = name
            clash = [a for a in t.avoid if self.lower(a) in map(self.lower, t.accepted())]
            if clash:
                out.append(f"{t.path}: {clash[0]} hem önerilen hem kaçınılan listede")
            expected = slug(t.en[0]) + ".yml"
            if t.path is not None and t.path.name != expected:
                out.append(f"{t.path}: dosya adı {expected} olmalı")
        return out


def slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
