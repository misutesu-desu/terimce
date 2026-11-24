# Sözlükten GitHub Pages için tek sayfa üretir: python site/build.py _site
import html
import sys
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from terimce import diller  # noqa: E402
from terimce.glossary import Glossary  # noqa: E402

REPO = "https://github.com/misutesu-desu/terimce"
TEMPLATE = (ROOT / "site" / "index.html").read_text(encoding="utf-8")
NEW_TERM = "en: {en}\ntr: \nalt: []\navoid: []\ntags: []\nnote: \n"


def esc(s: str) -> str:
    return html.escape(s, quote=True)


def row(t, lower) -> str:
    rel = t.path.relative_to(ROOT).as_posix()
    haystack = " ".join(lower(w) for w in t.en + t.accepted() + t.avoid)
    cells = [
        f'<td lang="en">{esc(", ".join(t.en))}</td>',
        f'<td class="tr">{esc(t.target)}</td>',
        f'<td>{esc(", ".join(t.alt))}</td>',
        f'<td class="avoid">{esc(", ".join(t.avoid))}</td>',
        f'<td class="note">{esc(t.note)}</td>',
        f'<td><a class="edit" href="{REPO}/edit/main/{rel}" '
        f'aria-label="{esc(t.en[0])} terimini düzenle">Düzenle</a></td>',
    ]
    return (f'<tr data-q="{esc(haystack)}" data-tags="{esc(" ".join(t.tags))}">'
            + "".join(cells) + "</tr>")


def main(out: Path) -> None:
    lang = diller.get("tr")
    glossary = Glossary.load("tr", lang.lower)
    terms = sorted(glossary.terms, key=lambda t: t.en[0].lower())
    tags = sorted({tag for t in terms for tag in t.tags})
    page = (TEMPLATE
            .replace("{{rows}}", "\n".join(row(t, lang.lower) for t in terms))
            .replace("{{count}}", str(len(terms)))
            .replace("{{tags}}", "".join(f'<option value="{esc(t)}">{esc(t)}</option>'
                                         for t in tags))
            .replace("{{repo}}", REPO)
            .replace("{{new_url}}", f"{REPO}/new/main/sozluk/tr?filename=terim.yml&value="
                     + quote(NEW_TERM.format(en=""))))
    out.mkdir(parents=True, exist_ok=True)
    (out / "index.html").write_text(page, encoding="utf-8")
    print(f"{out / 'index.html'}: {len(terms)} terim")


if __name__ == "__main__":
    main(Path(sys.argv[1] if len(sys.argv) > 1 else "_site"))
