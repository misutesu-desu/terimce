from dataclasses import dataclass
from typing import Optional

HATA = "hata"
UYARI = "uyari"


@dataclass
class Entry:
    key: str
    source: str
    target: str
    file: str
    line: Optional[int] = None


@dataclass
class Finding:
    code: str
    level: str
    message: str
    entry: Entry

    def location(self) -> str:
        if self.entry.line is not None:
            return f"{self.entry.file}:{self.entry.line}"
        return f"{self.entry.file} [{self.entry.key}]"
