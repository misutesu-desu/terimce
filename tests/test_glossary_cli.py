import json

import pytest

from terimce import diller
from terimce.cli import main
from terimce.glossary import Glossary, GlossaryError, data_dir, load_term


def test_bundled_glossary_is_valid():
    g = Glossary.load("tr", diller.get("tr").lower)
    assert len(g.terms) >= 100
    assert g.problems() == []


def test_load_term_rejects_bad_files(tmp_path):
    p = tmp_path / "x.yml"
    p.write_text("en: x\ntr: y\nnotes: typo\n", encoding="utf-8")
    with pytest.raises(GlossaryError, match="notes"):
        load_term(p, "tr")
    p.write_text("en: x\ntr: [a, b]\n", encoding="utf-8")
    with pytest.raises(GlossaryError, match="tek bir yazı"):
        load_term(p, "tr")
    p.write_text("en: x\n", encoding="utf-8")
    with pytest.raises(GlossaryError, match="tr alanı"):
        load_term(p, "tr")


def test_problems_finds_duplicates_clashes_and_names(tmp_path):
    (tmp_path / "loot.yml").write_text("en: loot\ntr: ganimet\n", encoding="utf-8")
    (tmp_path / "other.yml").write_text("en: Loot\ntr: yağma\navoid: [Yağma]\n",
                                        encoding="utf-8")
    problems = Glossary.load("tr", diller.get("tr").lower, tmp_path).problems()
    assert any("zaten loot.yml" in p for p in problems)
    assert any("hem önerilen hem kaçınılan" in p for p in problems)
    assert any("dosya adı loot.yml olmalı" in p for p in problems)


def test_unknown_language_gets_generic_checks(tmp_path, capsys):
    p = tmp_path / "de.csv"
    p.write_text("source,target\nHello {name},Hallo\n", encoding="utf-8")
    assert main(["lint", "--lang", "de", str(p)]) == 1
    assert "degisken-eksik" in capsys.readouterr().out


def test_cli_exit_codes_and_json(tmp_path, capsys):
    p = tmp_path / "t.csv"
    p.write_text("source,target\nSave?,Kaydet\n", encoding="utf-8")
    assert main(["lint", str(p)]) == 0
    assert main(["lint", "--strict", str(p)]) == 1
    capsys.readouterr()
    assert main(["lint", "--output", "json", str(p)]) == 0
    out = json.loads(capsys.readouterr().out)
    assert out[0]["code"] == "noktalama-son" and out[0]["line"] == 2
    assert main(["lint", "--ignore", "noktalama-son", "--strict", str(p)]) == 0


def test_cli_github_annotations(tmp_path, capsys):
    p = tmp_path / "t.csv"
    p.write_text("source,target\nFrame rate,Çerçeve hızı\n", encoding="utf-8")
    assert main(["lint", "--output", "github", str(p)]) == 1
    assert f"::error file={p},line=2::terim-kacin" in capsys.readouterr().out


def test_cli_reports_format_errors(tmp_path, capsys):
    assert main(["lint", str(tmp_path / "yok.po")]) == 2
    assert "terimce:" in capsys.readouterr().err


def test_cli_search(capsys):
    assert main(["search", "bekleme"]) == 0
    assert "cooldown" in capsys.readouterr().out
    assert main(["search", "zzzz"]) == 1


def test_data_dir_points_at_repo_or_package():
    assert (data_dir() / "tr" / "cooldown.yml").is_file()
