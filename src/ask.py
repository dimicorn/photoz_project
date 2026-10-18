"""Ответы на компетентностные вопросы ontology.yaml по графу проекта.

    .venv/bin/python -m src.ask          # все пять вопросов
    .venv/bin/python -m src.ask 4        # один вопрос

Данные: notes/, tasks/, reports/ (только чтение). Проверка графа — checks/check_graph.py.
"""
import re
import sys
from collections import defaultdict
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def load():
    nodes = {}
    for folder in ["notes", "tasks", "reports"]:
        for p in sorted((ROOT / folder).glob("*.md")):
            text = p.read_text(encoding="utf-8")
            m = re.match(r"---\n(.*?)\n---\n", text, re.S)
            front = yaml.safe_load(m.group(1)) if m else {}
            links = defaultdict(list)
            for rel, tgt in re.findall(r"^- ([^:\n]+): \[\[([^\]|]+)\]\]", text.split("## Связи", 1)[-1], re.M):
                links[rel.strip()].append(tgt.strip())
            nodes[p.stem] = {"type": front.get("type"), "front": front, "links": links}
    return nodes


def of(nodes, cls):
    return {k: v for k, v in nodes.items() if v["type"] == cls}


def q1(n):
    print("1. На какой выборке обучен и на каких оценён каждый результат photo-z?")
    for name, e in of(n, "Эксперимент").items():
        for r in e["links"]["даёт"]:
            print(f"   {r}: обучение — {', '.join(e['links']['обучаетсяНа'])}; оценка — "
                  f"{', '.join(e['links']['оцениваетсяНа'])} (эксперимент «{name}»)")


def q2(n):
    print("2. Какие результаты прошли независимую проверку?")
    for name, r in of(n, "Результат").items():
        checks = r["links"]["проверенЧерез"]
        print(f"   {name}: {', '.join(checks) if checks else 'НЕ проверен'}")


def q3(n):
    print("3. Какие ограничения действуют на результаты и данные?")
    for name, c in of(n, "Ограничение").items():
        print(f"   {name} → {', '.join(c['links']['ограничивает'])}")


def q4(n):
    print("4. На какие источники опираются гипотезы и методы и каким запросом найден каждый источник?")
    for cls in ["Гипотеза", "Метод", "Метрика", "Выборка"]:
        for name, x in of(n, cls).items():
            src = x["links"]["основанаНа"] + x["links"]["описанаВ"]
            if src:
                print(f"   {cls} «{name}» ← {', '.join(sorted(set(src)))}")
    for name, s in of(n, "Источник").items():
        print(f"   {name} (openalex_id {s['front'].get('openalex_id', '—')}) найден: {'; '.join(s['links']['найденЗапросом'])}")


def q5(n):
    print("5. Какие задачи поставлены, в каком они статусе и чем закрыты?")
    closers = defaultdict(list)
    for name, x in n.items():
        for rel in ("решает", "выполняет"):
            for t in x["links"][rel]:
                closers[t].append(f"{x['type']} «{name}»")
    for name, t in of(n, "Задача").items():
        print(f"   [{t['front'].get('status')}] {name}: {', '.join(closers[name]) or '—'}")


if __name__ == "__main__":
    nodes = load()
    qs = [q1, q2, q3, q4, q5]
    for i in ([int(sys.argv[1])] if len(sys.argv) > 1 else range(1, 6)):
        qs[i - 1](nodes)
