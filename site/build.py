# Sözlükten GitHub Pages için tek sayfa üretir: python site/build.py _site
import html
import sys
from itertools import groupby
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from terimce import diller  # noqa: E402
from terimce.glossary import Glossary  # noqa: E402

REPO = "https://github.com/misutesu-desu/terimce"
TEMPLATE = (ROOT / "site" / "index.html").read_text(encoding="utf-8")


def esc(s: str) -> str:
    return html.escape(s, quote=True)


def entry(t, lower) -> str:
    rel = t.path.relative_to(ROOT).as_posix()
    haystack = " ".join(lower(w) for w in t.en + t.accepted() + t.avoid)
    parts = [f'<b>{esc(t.target)}</b>']
    parts += [f'<span class="alt">{esc(a)}</span>' for a in t.alt]
    parts += [f'<s title="kullanma">{esc(a)}</s>' for a in t.avoid]
    note = f'<p class="note">{esc(t.note)}</p>' if t.note else ""
    return (f'<div class="term" data-q="{esc(haystack)}">'
            f'<dt lang="en">{esc(", ".join(t.en))}'
            f'<a class="edit" href="{REPO}/edit/main/{rel}">düzenle</a></dt>'
            f'<dd><span class="tr">{", ".join(parts)}</span>{note}</dd></div>')


def main(out: Path) -> None:
    lang = diller.get("tr")
    terms = sorted(Glossary.load("tr", lang.lower).terms, key=lambda t: t.en[0].lower())
    sections, letters = [], []
    for letter, group in groupby(terms, key=lambda t: t.en[0][0].upper()):
        letters.append(f'<a href="#{letter}">{letter}</a>')
        body = "\n".join(entry(t, lang.lower) for t in group)
        sections.append(f'<section id="{letter}"><h2>{letter}</h2><dl>{body}</dl></section>')
    page = (TEMPLATE
            .replace("{{sections}}", "\n".join(sections))
            .replace("{{letters}}", "".join(letters))
            .replace("{{count}}", str(len(terms)))
            .replace("{{repo}}", REPO))
    out.mkdir(parents=True, exist_ok=True)
    (out / "index.html").write_text(page, encoding="utf-8")
    print(f"{out / 'index.html'}: {len(terms)} terim")


if __name__ == "__main__":
    main(Path(sys.argv[1] if len(sys.argv) > 1 else "_site"))
