from terimce import checks, diller
from terimce.glossary import Glossary, Term
from terimce.model import Entry

tr = diller.get("tr")


def codes(source, target, glossary=None, max_ratio=None):
    e = Entry("k", source, target, "f")
    return [f.code for f in checks.run([e], tr.CHECKS, glossary, max_ratio)]


def test_clean_line_has_no_findings():
    assert codes("You picked up {count} potions.", "{count} iksir topladın.") == []


def test_missing_and_extra_placeholders():
    assert codes("Hello {name}!", "Merhaba!") == ["degisken-eksik"]
    assert codes("Hello!", "Merhaba {name}!") == ["degisken-fazla"]


def test_placeholder_kinds():
    for ph in ["%s", "%1$d", "%.2f", "{{player}}", "<color=red>", "[b]", "$GOLD$", "\\n"]:
        assert "degisken-eksik" in codes(f"a {ph} b", "a b"), ph


def test_placeholder_order_does_not_matter():
    assert codes("%1$s hit %2$s.", "%2$s, %1$s tarafından vuruldu.") == []


def test_percent_sign_in_text_is_not_a_placeholder():
    assert codes("50% damage", "%50 hasar") == []


def test_empty_target_is_skipped():
    assert codes("Hello {name}", "") == []


def test_whitespace_and_punctuation():
    assert codes("Save?", "Kaydet") == ["noktalama-son"]
    assert codes("Loading...", "Yükleniyor…") == []
    assert codes("Name: ", "Ad:") == ["bosluk-kenar"]
    assert codes("Play now", "Şimdi  oyna") == ["bosluk-cift"]


def test_newline_count():
    assert codes("a\nb", "a b") == ["satir-sayisi"]


def test_untranslated_needs_two_words():
    assert codes("Start game", "Start game") == ["cevrilmemis"]
    assert codes("OK", "OK") == []


def test_length_ratio():
    assert codes("Save", "Oyunu şimdi kaydet", max_ratio=2.0) == ["uzunluk"]
    assert codes("Save", "Kaydet", max_ratio=2.0) == []


def test_turkish_dotless_capital():
    assert codes("LOGIN", "GIRIŞ") == ["tr-buyuk-i"]
    assert codes("LOGIN", "GİRİŞ") == []
    assert codes("LIGHT", "IŞIK") == []
    assert codes("Cancel", "Iptal") == ["tr-buyuk-i"]


def test_turkish_combining_dot():
    assert codes("INFO", "i̇ptal") == ["tr-noktali-i"]


def test_suffix_on_placeholder():
    assert codes("{name}'s sword", "{name}'ın kılıcı") == ["tr-degisken-eki"]
    assert codes("{name}'s sword", "{name} adlı karakterin kılıcı") == []


def glossary():
    return Glossary([
        Term(en=["frame rate"], target="kare hızı", avoid=["çerçeve hızı"]),
        Term(en=["achievement"], target="başarım", avoid=["başarı"]),
        Term(en=["cooldown"], target="bekleme süresi", alt=["yenilenme süresi"]),
    ], tr.lower)


def test_glossary_avoid_is_an_error():
    assert codes("Frame rate limit", "Çerçeve hızı sınırı", glossary()) == ["terim-kacin"]


def test_glossary_accepts_suffixes_and_alternatives():
    assert codes("Frame rate limit", "Kare hızı sınırı", glossary()) == []
    assert codes("Reset the cooldown", "Bekleme süresini sıfırla", glossary()) == []
    assert codes("Cooldown", "Yenilenme süresi", glossary()) == []
    assert codes("Cooldowns", "Bekleme süreleri", glossary()) == []


def test_glossary_accepted_wins_over_avoided_prefix():
    assert codes("Achievement unlocked", "Başarım açıldı", glossary()) == []


def test_glossary_missing_term_is_a_warning():
    assert codes("Cooldowns reduced", "Süreler azaldı", glossary()) == ["terim-eksik"]


def test_glossary_matches_whole_words_only():
    assert codes("Frame rates", "Kare hızları", glossary()) == []
    assert codes("Achievements", "Başarımlar", glossary()) == []
    assert codes("Overachievement", "Aşırı başarı", glossary()) == []
