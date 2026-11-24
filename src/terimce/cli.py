import argparse
import json
import sys
from pathlib import Path
from typing import List, Optional

from . import __version__, checks, diller, formats
from .glossary import Glossary, GlossaryError
from .model import HATA, Finding


def _github_annotation(f: Finding) -> str:
    kind = "error" if f.level == HATA else "warning"
    line = f",line={f.entry.line}" if f.entry.line else ""
    msg = f"{f.code}: {f.message}".replace("%", "%25").replace("\n", "%0A")
    return f"::{kind} file={f.entry.file}{line}::{msg}"


def cmd_lint(args) -> int:
    lang = diller.get(args.lang)
    glossary = None
    if not args.no_glossary:
        glossary = Glossary.load(args.lang, lang.lower,
                                 Path(args.glossary) if args.glossary else None)
    findings: List[Finding] = []
    total = 0
    for name in args.files:
        entries = formats.read(Path(name), args.format,
                               Path(args.source) if args.source else None,
                               args.source_col, args.target_col)
        total += len(entries)
        findings += checks.run(entries, lang.CHECKS, glossary, args.max_ratio, args.ignore)

    errors = sum(f.level == HATA for f in findings)
    warnings = len(findings) - errors
    if args.output == "json":
        json.dump([{"file": f.entry.file, "line": f.entry.line, "key": f.entry.key,
                    "code": f.code, "level": f.level, "message": f.message}
                   for f in findings], sys.stdout, ensure_ascii=False, indent=2)
        print()
    else:
        for f in findings:
            if args.output == "github":
                print(_github_annotation(f))
            label = "hata" if f.level == HATA else "uyarı"
            print(f"{f.location()}: {label} {f.code}: {f.message}")
            print(f"    kaynak: {f.entry.source!r}")
            print(f"    çeviri: {f.entry.target!r}")
        print(f"{total} satır, {errors} hata, {warnings} uyarı", file=sys.stderr)
    if errors or (args.strict and warnings):
        return 1
    return 0


def cmd_search(args) -> int:
    lang = diller.get(args.lang)
    glossary = Glossary.load(args.lang, lang.lower)
    found = glossary.search(args.query)
    for t in found:
        line = f"{', '.join(t.en)}: {t.target}"
        if t.alt:
            line += f" ya da {', '.join(t.alt)}"
        print(line)
        if t.avoid:
            print(f"    kaçın: {', '.join(t.avoid)}")
        if t.note:
            print(f"    {t.note}")
    if not found:
        print(f"{args.query} sözlükte yok", file=sys.stderr)
        return 1
    return 0


def cmd_check_glossary(args) -> int:
    lang = diller.get(args.lang)
    directory = Path(args.directory) if args.directory else None
    glossary = Glossary.load(args.lang, lang.lower, directory)
    problems = glossary.problems()
    for p in problems:
        print(p)
    print(f"{len(glossary.terms)} terim, {len(problems)} sorun", file=sys.stderr)
    return 1 if problems else 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="terimce",
                                description="Oyun çevirileri için denetleyici ve terim sözlüğü")
    p.add_argument("--version", action="version", version=f"terimce {__version__}")
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--lang", default="tr", help="hedef dil, varsayılan tr")
    sub = p.add_subparsers(dest="command", required=True)

    lint = sub.add_parser("lint", parents=[common], help="çeviri dosyalarını denetle")
    lint.add_argument("files", nargs="+")
    lint.add_argument("--format", choices=sorted(set(formats.EXTENSIONS.values())))
    lint.add_argument("--source", help="JSON için kaynak dil dosyası")
    lint.add_argument("--source-col", help="CSV kaynak sütunu, ad ya da sıra numarası")
    lint.add_argument("--target-col", help="CSV çeviri sütunu, ad ya da sıra numarası")
    lint.add_argument("--glossary", help="kendi sözlük klasörün")
    lint.add_argument("--no-glossary", action="store_true", help="sözlük denetimini kapat")
    lint.add_argument("--max-ratio", type=float, help="çeviri kaynağın bu katından uzunsa uyar")
    lint.add_argument("--ignore", action="append", default=[], metavar="KOD",
                      help="bu kodu raporlama, birden çok kez verilebilir")
    lint.add_argument("--strict", action="store_true", help="uyarıda da hata koduyla çık")
    lint.add_argument("--output", choices=["text", "json", "github"], default="text")
    lint.set_defaults(func=cmd_lint)

    search = sub.add_parser("search", parents=[common], help="sözlükte terim ara")
    search.add_argument("query")
    search.set_defaults(func=cmd_search)

    cg = sub.add_parser("check-glossary", parents=[common], help="sözlük dosyalarını doğrula")
    cg.add_argument("directory", nargs="?")
    cg.set_defaults(func=cmd_check_glossary)
    return p


def main(argv: Optional[List[str]] = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    args = build_parser().parse_args(argv)
    try:
        return args.func(args)
    except (formats.FormatError, GlossaryError, OSError) as e:
        print(f"terimce: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
