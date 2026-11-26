# Temel Eaverse

Global Capital Radar’ın sermaye akışı gözlemleri ile Tier-1 Quant Terminal’in kısa vadeli bağımsız denetimini aynı kanıt matrisinde birleştiren araştırma sistemi.

Sistem ilk çalıştırmada 12 varlık × 6 vade için 72 hücre üretir. Eksik veri `0` sayılmaz. Kanıtı yetersiz bir hücre yatırım başarısı olarak işaretlenmez. Kaynak repolar salt okunur kullanılır ve kendi strateji mantıkları değiştirilmez.

## Varlıklar ve vadeler

SPY, QQQ, DIA, IWM, SGOV, SHY, GLD, SLV, CPER, USO, IBIT ve ETHA aynı anda izlenir. Vadeler 4 saat, 1 gün, 1 hafta, 1 ay, 3 ay ve 1 yıldır.

4 saat ve 1 günlük hücrelerde Tier-1’in bağımsız denetimi kullanılır. Bir hafta ile bir yıl arasındaki hücreler Radar’ın akış büyüklüğü, yön sürekliliği ve geçmiş referans dönemlerini taşır. Bire bir Tier-1 eşleşmesi bulunmayan hücreler açıkça belirtilir.

## Çalıştırma

```bash
python -m venv .venv
. .venv/bin/activate
pip install -e '.[test]'
pytest
python run.py
streamlit run app.py
```

`python run.py`, kaynakların mevcut anlık JSON kayıtlarını indirir ve `state/latest.json` dosyasını atomik biçimde yeniler. Kaynak kanıtı değiştiğinde aynı kayıt `state/observations.jsonl` günlüğüne yalnızca bir kez eklenir. Zamanlanmış iş dört saatte bir çalışır. Aynı anda ikinci çalışmayı başlatmaz.

## Karar sınırı

Bu sürüm PAPER araştırmasıdır. Bir hücrenin görünmesi, giriş izni veya kanıtlanmış kârlılık anlamına gelmez. Altı yöntem adayı her hücrede gölge olarak hesaplanır. İleri günlükte en az 30 geçerli ve en az %80 kapsamalı maliyet sonrası sonuç olmadan hiçbir yöntem seçilmez. Model karşılaştırması yalnızca aynı karar zamanı, aynı çıkış zamanı, aynı maliyet varsayımı ve aynı gözlem kimliğiyle yazılmış sonuçları kullanır.

Birleşimin gerçek ek katkısı, aynı karar anı ve çıkışta birleşik hesap eksi Radar hesabının maliyet sonrası getirisiyle ölçülecektir. Olgunlaşmış ileri sonuç birikmeden sistem kazanan yöntem ilan etmez.

