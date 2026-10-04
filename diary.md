# Журнал проекта

## 2026-09-30 — Initial project

- Созданы проект, AGENT.md, каталоги data, paper, src и memory, исходный дневник.
- Добавлены каталоги Happy A–D и статья paper/paper.pdf. Happy A — обучение; B/C/D — проверка.
- Запуска ai4science в этом коммите не зафиксировано; учтённый расход ai4science — 0 токенов.

## 2026-10-01 — First agent cycle

- Запрос: посчитать число галактик Happy A, медиану z_spec и долю z_spec > 0.5; записать results/week1_summary.txt.
- Результат: 74 950 галактик; median_z_spec=0.374342; frac_z_gt_0_5=0.319346.
- Проверка: независимые команды awk дали те же числа. По проверке человеком результат принят с замечанием: агент сам заполнил поле приёмки.
- Запуск: ai4science run, режим auto; data закрыт от записи. Расход ai4science — 103 961 токен.

## 2026-10-04 — Compare AGENTS runs

- Сравнены два прогона station_trends в ../w2_test/: без AGENTS.md и с ним. Логи — log_without.txt и log_with.txt.
- Без инструкции: compute_trends.py и trends.csv в корне, проверка check_trends.py — код 1, итоговый файл results/trends.csv отсутствовал; 5 шагов, 15 с, 36 025 токенов.
- С инструкцией: src/trend.py и results/trends.csv, проверка — код 0; станция D помечена flag=1; 15 шагов, 16 с, 88 443 токена.
- Оба запуска — ai4science --no-lean run, qwen3.6-35b-a3b, AI4SCIENCE_WEB_DISABLED=1.
- Замечание: во втором прогоне агент прочитал checks/check_trends.py вопреки запрету. Имена выходных файлов и критерий проверки существенно изменили поведение.

## 2026-10-04 — Add AGENTS check

- AGENT.md переименован в AGENTS.md, добавлена проверка checks/check.py.
- Зафиксированы схема результатов photo-z, ограничения на обучение и команда проверки.
- Отдельный расход ai4science на настройку проверки не зафиксирован; в учёте ai4science — 0 токенов.

