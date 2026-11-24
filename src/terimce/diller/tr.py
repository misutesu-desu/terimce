import re
from functools import lru_cache
from typing import Iterable, Set

from ..glossary import data_dir
from ..model import HATA, UYARI, Entry, Finding

WORD = re.compile(r"[A-Za-zÇĞİÖŞÜçğıöşü]+")
SUFFIX_AFTER_PLACEHOLDER = re.compile(
    r"(\{[^{}\s]*\}|%(?:\d+\$)?[sd]|\$[A-Za-z_][A-Za-z0-9_|]*\$)['’]([a-zçğıöşü]+)")


def lower(text: str) -> str:
    return text.replace("I", "ı").replace("İ", "i").lower()


@lru_cache(maxsize=1)
def i_words() -> Set[str]:
    path = data_dir() / "tr" / "i-kelimeleri.txt"
    if not path.is_file():
        return set()
    words = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.split("#", 1)[0].strip()
        if line:
            words.add(line)
    return words


def check_combining_dot(e: Entry) -> Iterable[Finding]:
    # "İ".lower() Python'da "i" + U+0307 verir; ekranda çift noktalı ya da kutu görünür.
    if "̇" in e.target:
        yield Finding("tr-noktali-i", HATA,
                      "İ harfi yanlış küçültülmüş, i ile birleşik nokta U+0307 var", e)


def check_dotless_capital(e: Entry) -> Iterable[Finding]:
    # İngilizce yerel ayarla upper() yapılınca i harfi İ yerine I olur: GİRİŞ yerine GIRIŞ.
    words = i_words()
    for word in WORD.findall(e.target):
        if "I" not in word:
            continue
        as_i = lower(word.replace("I", "i"))
        as_dotless = lower(word)
        if as_i in words and as_dotless not in words:
            fixed = word.replace("I", "İ") if word.isupper() else word.replace("I", "İ", 1)
            yield Finding("tr-buyuk-i", HATA, f"{word} yerine {fixed} olmalı", e)


def check_suffix_on_placeholder(e: Entry) -> Iterable[Finding]:
    for m in SUFFIX_AFTER_PLACEHOLDER.finditer(e.target):
        yield Finding("tr-degisken-eki", UYARI,
                      f"{m.group(0)}: ek değişkenin değerine göre değişir, "
                      f"cümleyi değişkene ek gerekmeyecek biçimde kur", e)


CHECKS = [check_combining_dot, check_dotless_capital, check_suffix_on_placeholder]
