# Katkı rehberi

En kolay katkı sözlüğe bir terim eklemek ya da var olanı düzeltmek. Bunun için Python kurmana gerek yok, her şey GitHub'ın web arayüzünden yapılır.

## Terim eklemek

1. [Sözlük sayfasında](https://misutesu.com/terimce/) terimi ara. Yoksa çıkan Bu terimi ekle bağlantısına tıkla. GitHub'da dosya hazır açılır.
2. Alanları doldur:

   ```yaml
   en: parry
   tr: savuştur
   alt: [karşıla]
   avoid: []
   tags: [savas]
   note: Saldırıyı doğru anda karşılayıp düşmanı açıkta bırakma.
   ```

   - `en`: İngilizce terim, küçük harfle. Aynı anlamda birden çok yazım varsa liste ver: `[medkit, health pack]`.
   - `tr`: Önerdiğin karşılık. Tek bir karşılık yaz.
   - `alt`: Kabul edilebilir diğer karşılıklar. Denetleyici bunları hata saymaz.
   - `avoid`: Yanlış ya da kötü bulduğun karşılıklar. Çeviride geçerse hata verilir. Yalnızca gerçekten yanlış olanları yaz, tartışmalı olanları `alt` ya da `note` içine koy.
   - `tags`: `arayuz`, `ayarlar`, `savas`, `rpg`, `rekabet` ya da yeni bir tür.
   - `note`: Terim belirsizse hangi anlamda kullanıldığını bir cümleyle yaz.
3. Dosya adı İngilizce terimin küçük harfli, tireli hali olmalı: `parry.yml`, `field-of-view.yml`.
4. Propose changes ile PR aç. Açıklamada bu karşılığı nerede gördüğünü yaz: hangi oyunun resmi çevirisi, hangi yama ekibi ya da neden bunu önerdiğin.

## Terim düzeltmek

Sözlük sayfasında terimin yanındaki Düzenle bağlantısı dosyayı GitHub'da açar. Değiştir, PR'da nedenini yaz. Bir karşılığı `avoid` listesine taşımak tartışma çıkarabilir. Önce bir issue açıp sormak iyi olur.

## Neler kabul edilir

- Oyunlarda gerçekten geçen terimler. Genel sözlük kelimeleri değil.
- Resmi Türkçe çevirilerde ya da yaygın yamalarda kullanılan karşılıklar. Tek kişinin zevkine dayanan karşılık `alt` olarak eklenir.
- Oyun metinlerinden uzun alıntı değil. Örnek gerekiyorsa birkaç kelimelik kendi cümleni yaz.

## İ harfi listesi

[sozluk/tr/i-kelimeleri.txt](sozluk/tr/i-kelimeleri.txt), büyük harfli metinde GIRIŞ gibi hataları bulmak için kullanılır. Oyun arayüzlerinde sık geçen, içinde i olan bir kelime eksikse satır olarak ekle. Hem I hem ı ile geçerli olan kelimeleri ekleme.

## Kod katkısı

```
git clone https://github.com/misutesu-desu/terimce
cd terimce
pip install -e ".[test]"
pytest
terimce check-glossary
```

İyi başlangıç işleri [good first issue](https://github.com/misutesu-desu/terimce/labels/good%20first%20issue) etiketinde. Sık istenenler:

- Yeni format okuyucusu: Ren'Py, RPG Maker, Unity I2 Localization, Paradox `.yml`, Bethesda `.strings`. `src/terimce/formats.py` içindeki `read_xunity` en kısa örnek. Her format için `tests/test_formats.py` içine bir test ekle.
- Yeni dil: `src/terimce/diller/tr.py` dosyasını örnek al. `lower()` fonksiyonu ve `CHECKS` listesi yeterli. Sözlüğü `sozluk/<dil>/` altına koy.
- Yeni denetim: önce bir issue aç, hangi hatayı yakalayacağını ve yanlış alarm riskini yaz.

## Lisans

Sözlüğe yaptığın katkı CC BY 4.0, koda yaptığın katkı MIT lisansıyla yayımlanır.
