---
type: ЗапросКГрафу
source: Wikidata
retrieved: 2026-10-18
---
# Запрос 2026-10-18 Wikidata photometric redshift

Инструмент и аргументы: `wikidata_search(text="photometric redshift", language="en")` → Q3967221; затем `wikidata_sparql`:

```sparql
SELECT ?prop ?propLabel ?value ?valueLabel WHERE {
  VALUES ?p { wdt:P31 wdt:P279 wdt:P361 wdt:P2579 }
  wd:Q3967221 ?p ?value .
  ?prop wikibase:directClaim ?p .
  SERVICE wikibase:label { bd:serviceParam wikibase:language "ru,en". }
}
```
Найдено: 3; отобрано в проект: 3 строки; сведения внесены в заметку [[kNN photo-z в пространстве признаков feat]]

- [источник] это частный случай понятия: Q2695280 — техника
- [источник] это частный случай понятия: Q4373292 — физическое свойство
- [источник] подкласс от: Q76250 — красное смещение

## Связи
- тип: [[ЗапросКГрафу]]
- решает: [[Собрать литературу к проекту]]
