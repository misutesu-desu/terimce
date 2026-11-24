# terimce

Türkçe oyun çevirisi dosyalarını kaynakla satır satır karşılaştırıp oyunu bozacak hataları listeleyen küçük bir araç.

```
$ terimce lint ornekler/tr.po
ornekler/tr.po:9: hata degisken-eksik: çeviride eksik: {count}
    kaynak: 'You picked up {count} potions.'
    çeviri: 'İksirleri topladın.'
ornekler/tr.po:12: hata tr-buyuk-i: GIRIŞ yerine GİRİŞ olmalı
    kaynak: 'LOGIN'
    çeviri: 'GIRIŞ'
ornekler/tr.po:15: hata terim-kacin: frame rate: çerçeve hızı yerine kare hızı kullan
    kaynak: 'Frame rate limit'
    çeviri: 'Çerçeve hızı sınırı'
```

GIRIŞ hatası genelde metin İngilizce yerel ayarla büyük harfe çevrilince çıkıyor. Kaybolan ya da fazladan eklenen `{0}`, `%s` ve `<color>` gibi parçalar ise bazı oyunları o ekranda çökertiyor.

`.po`, `.csv`, `.tsv` ve XUnity.AutoTranslator'ın `.txt` dosyalarını okuyor. JSON için İngilizce dosyayı da vermek gerekiyor: `terimce lint tr.json --source en.json`.

```
pip install git+https://github.com/misutesu-desu/terimce
terimce lint tr.po
```

Python 3.10 ve üstünde çalışıyor. Bir denetimi istemiyorsan çıktıdaki kodunu `--ignore` ile ver, örneğin `--ignore noktalama-son`. Diğer seçenekler için `terimce lint --help`.

## Sözlük

Terim denetimi [sozluk/tr](sozluk/tr) altındaki dosyalara bakıyor. Her terim ayrı bir dosya, `avoid` altına yazılan karşılık çeviride geçerse hata veriyor. Şimdilik 107 terim var, çoğu menü, ayar ve savaş terimi.

Hepsini [misutesu.com/terimce](https://misutesu.com/terimce/) adresinde arayabilirsin. Katılmadığın bir karşılık ya da eksik bir terim varsa dosyayı GitHub'da düzenleyip PR açman yeterli, nasıl yapılacağı [CONTRIBUTING.md](CONTRIBUTING.md) içinde.

## GitHub Actions

```yaml
- uses: misutesu-desu/terimce@v0
  with:
    files: locale/tr.po
```

Bulduklarını PR'da ilgili satırın yanına yazıyor.

## Bilinen eksikler

- İ denetimi [bir kelime listesine](sozluk/tr/i-kelimeleri.txt) bakıyor. Listede olmayan kelimedeki hatayı kaçırır.
- Terim denetimi Türkçe ekleri kabaca ele alıyor. Ünsüz yumuşaması olan kelimelerde, mesela kitap ve kitabı gibi, boşuna uyarı verebilir.
- Ren'Py, Paradox ve XLIFF dosyaları henüz okunmuyor.

`--lang de` gibi başka bir dil verilirse yalnızca dilden bağımsız denetimler çalışır.

Kod MIT, sözlük CC BY 4.0 lisanslı.
