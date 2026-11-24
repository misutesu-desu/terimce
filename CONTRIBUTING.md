# Katkı

## Terim eklemek ya da düzeltmek

Python gerekmiyor. [Sözlük sayfasında](https://misutesu.com/terimce/) terimi ara. Varsa yanındaki düzenle bağlantısı, yoksa çıkan ekleme bağlantısı dosyayı GitHub'da açar. Dosya şöyle görünüyor:

```yaml
en: parry
tr: savuştur
alt: [karşıla]
avoid: []
tags: [savas]
note: Saldırıyı doğru anda karşılayıp düşmanı açıkta bırakma.
```

`tr` önerilen tek karşılık. `alt` da doğru sayılan diğerleri. `avoid` denetleyicinin hata vereceği karşılıklar, oraya yalnızca açıkça yanlış olanları yaz. Tartışmalı bir karşılık `alt` ya da `note` içinde kalsın. Dosya adı İngilizce terimin tireli hali: `field-of-view.yml`.

PR açıklamasına karşılığı nerede gördüğünü yaz. Bir oyunun resmi Türkçesi ya da bilinen bir yama işe yarar. Var olan bir karşılığı `avoid`'a taşımak istiyorsan önce issue açman daha iyi, orada tartışırız.

Oyun metninden uzun alıntı koyma, not için kendi cümleni yaz.

## İ listesi

GIRIŞ denetimi [sozluk/tr/i-kelimeleri.txt](sozluk/tr/i-kelimeleri.txt) dosyasına bakıyor. İçinde i geçen bir arayüz kelimesi eksikse satır olarak ekle. Hem I hem ı ile anlamlı olan kelimeleri ekleme, yanlış alarm verir.

## Kod

```
pip install -e ".[test]"
pytest
terimce check-glossary
```

Yeni bir dosya biçimi eklemek için `src/terimce/formats.py` içindeki `read_xunity` en kısa örnek. Yeni bir dil için `src/terimce/diller/tr.py` dosyasına bak, `lower()` ve `CHECKS` yetiyor. Yeni bir denetim düşünüyorsan önce issue aç, yanlış alarm riskini birlikte konuşalım.

Sözlüğe katkın CC BY 4.0, koda katkın MIT lisansıyla yayımlanır.
