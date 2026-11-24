import csv
import json
import re
from pathlib import Path
from typing import Dict, List, Optional

from .model import Entry


class FormatError(Exception):
    pass


SOURCE_COLUMNS = ("source", "en", "english", "original", "src")
TARGET_COLUMNS = ("target", "tr", "turkish", "translation", "dst")
KEY_COLUMNS = ("key", "id", "name")

EXTENSIONS = {
    ".po": "po",
    ".pot": "po",
    ".csv": "csv",
    ".tsv": "csv",
    ".json": "json",
    ".txt": "xunity",
}


def detect(path: Path) -> str:
    fmt = EXTENSIONS.get(path.suffix.lower())
    if fmt is None:
        raise FormatError(f"{path}: uzantıdan format anlaşılmadı, --format ile belirt")
    return fmt


def read(path: Path, fmt: Optional[str] = None, source: Optional[Path] = None,
         source_col: Optional[str] = None, target_col: Optional[str] = None) -> List[Entry]:
    fmt = fmt or detect(path)
    if fmt == "po":
        return read_po(path)
    if fmt == "csv":
        return read_csv(path, source_col, target_col)
    if fmt == "json":
        if source is None:
            raise FormatError(f"{path}: JSON için kaynak dil dosyasını --source ile ver")
        return read_json_pair(source, path)
    if fmt == "xunity":
        return read_xunity(path)
    raise FormatError(f"bilinmeyen format: {fmt}")


def _text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8-sig")
    except UnicodeDecodeError as e:
        raise FormatError(f"{path}: UTF-8 değil ({e.reason})") from e


_PO_ESCAPES = {"n": "\n", "t": "\t", '"': '"', "\\": "\\", "r": "\r"}


def _po_unquote(s: str) -> str:
    s = s.strip()
    if len(s) < 2 or s[0] != '"' or s[-1] != '"':
        raise ValueError(s)
    return re.sub(r'\\(.)', lambda m: _PO_ESCAPES.get(m.group(1), m.group(0)), s[1:-1])


def read_po(path: Path) -> List[Entry]:
    entries: List[Entry] = []
    fields: Dict[str, str] = {}
    current: Optional[str] = None
    start_line = 0

    def flush():
        msgid = fields.get("msgid", "")
        if msgid:
            key = fields.get("msgctxt", msgid)
            if "msgid_plural" in fields:
                pairs = [(msgid, fields.get("msgstr[0]", ""))]
                for name, value in sorted(fields.items()):
                    if name.startswith("msgstr[") and name != "msgstr[0]":
                        pairs.append((fields["msgid_plural"], value))
            else:
                pairs = [(msgid, fields.get("msgstr", ""))]
            for src, tgt in pairs:
                entries.append(Entry(key, src, tgt, str(path), start_line))
        fields.clear()

    for no, raw in enumerate(_text(path).splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            if not line and fields:
                flush()
                current = None
            continue
        if line.startswith('"'):
            if current is None:
                raise FormatError(f"{path}:{no}: başıboş satır")
            fields[current] += _po_unquote(line)
            continue
        name, _, rest = line.partition(" ")
        if name in ("msgctxt", "msgid") and any(k.startswith("msgstr") for k in fields):
            flush()
        if not fields:
            start_line = no
        try:
            fields[name] = _po_unquote(rest)
        except ValueError:
            raise FormatError(f"{path}:{no}: okunamayan satır") from None
        current = name
    if fields:
        flush()
    return entries


def _pick(header: List[str], wanted: Optional[str], candidates, what: str, path: Path) -> int:
    lowered = [h.strip().lower() for h in header]
    if wanted is not None:
        if wanted.isdigit():
            return int(wanted)
        if wanted.lower() in lowered:
            return lowered.index(wanted.lower())
        raise FormatError(f"{path}: {wanted} sütunu yok")
    for c in candidates:
        if c in lowered:
            return lowered.index(c)
    raise FormatError(f"{path}: {what} sütunu bulunamadı, --{what}-col ile belirt")


def read_csv(path: Path, source_col: Optional[str] = None,
             target_col: Optional[str] = None) -> List[Entry]:
    delimiter = "\t" if path.suffix.lower() == ".tsv" else ","
    reader = csv.reader(_text(path).splitlines(keepends=True), delimiter=delimiter)
    try:
        header = next(reader)
    except StopIteration:
        return []
    si = _pick(header, source_col, SOURCE_COLUMNS, "source", path)
    ti = _pick(header, target_col, TARGET_COLUMNS, "target", path)
    lowered = [h.strip().lower() for h in header]
    ki = next((lowered.index(c) for c in KEY_COLUMNS if c in lowered), None)
    entries = []
    for row in reader:
        if len(row) <= max(si, ti):
            continue
        key = row[ki] if ki is not None and ki < len(row) else str(reader.line_num)
        entries.append(Entry(key, row[si], row[ti], str(path), reader.line_num))
    return entries


def _flatten(value, prefix: str, out: Dict[str, str]) -> None:
    if isinstance(value, dict):
        for k, v in value.items():
            _flatten(v, f"{prefix}.{k}" if prefix else str(k), out)
    elif isinstance(value, list):
        for i, v in enumerate(value):
            _flatten(v, f"{prefix}[{i}]", out)
    elif isinstance(value, str):
        out[prefix] = value


def _load_json(path: Path) -> Dict[str, str]:
    try:
        data = json.loads(_text(path))
    except json.JSONDecodeError as e:
        raise FormatError(f"{path}:{e.lineno}: geçersiz JSON ({e.msg})") from e
    out: Dict[str, str] = {}
    _flatten(data, "", out)
    return out


def read_json_pair(source: Path, target: Path) -> List[Entry]:
    src = _load_json(source)
    tgt = _load_json(target)
    return [Entry(k, src[k], v, str(target)) for k, v in tgt.items() if k in src]


_XUNITY_SPLIT = re.compile(r"(?<!\\)=")


def read_xunity(path: Path) -> List[Entry]:
    entries = []
    for no, line in enumerate(_text(path).splitlines(), 1):
        if not line.strip() or line.lstrip().startswith("//"):
            continue
        parts = _XUNITY_SPLIT.split(line, maxsplit=1)
        if len(parts) != 2:
            continue
        src, tgt = (p.replace("\\=", "=") for p in parts)
        entries.append(Entry(src, src, tgt, str(path), no))
    return entries
