---
type: Отчёт
---
# Поиск по своей библиотеке: photometric redshift training set representativeness

[источник] OpenAlex, запрос: https://api.openalex.org/works?search=photometric+redshift+training+set+representativeness&per_page=50&filter=has_abstract%3Atrue&select=id%2Cdoi%2Cdisplay_name%2Cpublication_year%2Ccited_by_count%2Cabstract_inverted_index, дата: 2026-10-18, работ: 20

## k nearest neighbours photometric redshift

| место | BM25 | вектор |
|---|---|---|
| 1 | Optimizing Photometric Redshift Training Sets. I. Efficient  (W4417288889) | Optimizing Photometric Redshift Training Sets. I. Efficient  (W4417288889) |
| 2 | Estimating the redshift distribution of photometric galaxy s (W2145550174) | Photometric redshifts for the Kilo-Degree Survey (W4289726834) |
| 3 | QUANTIFYING PHOTOMETRIC REDSHIFT ERRORS IN THE ABSENCE OF SP (W2030697221) | Photometric redshift calibration with self-organising maps (W2973810890) |

[написано] Обе модели первой ставят Ashmead 2026 (kNN в координатах UMAP). Дальше BM25 берёт Lima et al. 2008 — там ближайшие соседи в пространстве цветов, а векторный поиск — KiDS и SOM: тема photo-z, но не kNN. На точном термине выдача BM25 ближе к запросу.

## spectroscopic training sample is not representative of the photometric sample

| место | BM25 | вектор |
|---|---|---|
| 1 | Estimating the redshift distribution of photometric galaxy s (W2145550174) | Diagnosing the Effects of Spectroscopic Training Set Imperfe (W7124747949) |
| 2 | Degradation analysis in the estimation of photometric redshi (W2796135634) | Optimizing Photometric Redshift Training Sets. I. Efficient  (W4417288889) |
| 3 | CNN photometric redshifts in the SDSS at r ≤ 20 (W4387731078) | Data-driven, Interpretable Photometric Redshifts Trained on  (W2560721689) |

[написано] Векторный поиск первым даёт работу 2026 г. о несовершенстве спектроскопических обучающих выборок — совпадает с темой проекта; BM25 первым ставит Lima 2008 (тоже о нерепрезентативности, через веса), но на третьем месте — CNN photo-z для SDSS, где слово representative встречается мимоходом.

## self-organizing map color redshift calibration

| место | BM25 | вектор |
|---|---|---|
| 1 | Optimizing Photometric Redshift Training Sets. I. Efficient  (W4417288889) | Photometric redshift calibration with self-organising maps (W3105893637) |
| 2 | Photometric redshift calibration with self-organising maps (W2973810890) | Photometric redshift calibration with self-organising maps (W2973810890) |
| 3 | Photometric redshift calibration with self-organising maps (W3105893637) | Optimizing Photometric Redshift Training Sets. I. Efficient  (W4417288889) |

[написано] Обе выдачи нашли работу о калибровке photo-z самоорганизующимися картами (KiDS, 2020), причём дважды: в OpenAlex две записи одной статьи — W2973810890 и W3105893637 с тем же DOI (у второй /pdf).

## reweighting training galaxies to correct covariate shift

| место | BM25 | вектор |
|---|---|---|
| 1 | Bayesian photometric redshifts with empirical training sets (W2157396371) | Data-driven, Interpretable Photometric Redshifts Trained on  (W2560721689) |
| 2 | Degradation analysis in the estimation of photometric redshi (W2796135634) | Estimating the redshift distribution of photometric galaxy s (W2145550174) |
| 3 | Data-driven, Interpretable Photometric Redshifts Trained on  (W2560721689) | Optimizing Photometric Redshift Training Sets. I. Efficient  (W4417288889) |

[написано] Термина covariate shift в аннотациях библиотеки нет, поэтому обе модели ищут «по соседству»: вектор вторым ставит Lima 2008 — метод перевзвешивания, нужный здесь; BM25 первыми ставит работы со словами training и weight без перевзвешивания. Работы Kremer et al. 2015 (веса для Happy) в библиотеке нет — нужна отдельная выборка.

## почему photo-z хуже для тусклых галактик

| место | BM25 | вектор |
|---|---|---|
| 1 | Photometric Redshift Error Estimators (W2105919768) | On the realistic validation of photometric redshifts (W2584691382) |
| 2 | Photometric redshifts for the Kilo-Degree Survey (W4289726834) | EAZY: A Fast, Public Photometric Redshift Code (W2080173214) |
| 3 | Diagnosing the Effects of Spectroscopic Training Set Imperfe (W7124747949) | Diagnosing the Effects of Spectroscopic Training Set Imperfe (W7124747949) |

[написано] Русский запрос: у BM25 совпал только токен photo, случайная выдача; векторный поиск находит Beck et al. 2017 (неполное покрытие пространства признаков спектроскопией) и EAZY — по смыслу ближе.

## Связи
- тип: [[Отчёт]]
- выполняет: [[Собрать литературу к проекту]]
- ссылаетсяНа: [[Ashmead 2026]]
- ссылаетсяНа: [[Beck 2017]]
- ссылаетсяНа: [[Lima 2008]]
- ссылаетсяНа: [[Brammer 2008]]
