"""Граф проекта в формате Obsidian: заметки классов, объектов и задач одной командой.

    .venv/bin/python -m src.graph classes            # ontology/<Класс>.md и .obsidian/ по ontology.yaml
    .venv/bin/python -m src.graph apply <spec.yaml>  # создать или переписать заметки из YAML
    .venv/bin/python -m src.graph status <путь> <статус> [--itog "<текст>"]

Формат spec.yaml — список заметок:

    - path: notes/Эксперимент kNN по Happy C.md     # путь от корня проекта
      type: Эксперимент
      fields: {status: открыта}                      # поля в начале заметки, кроме type
      body: |                                        # текст под заголовком
        2–4 строки: что это, откуда, числа с единицами.
      links:                                         # связи по ontology.yaml; файлы — путём от корня
        - [обучаетсяНа, Выборка Happy A]
        - [реализованВ, src/photoz.py]

Заголовок заметки — имя файла без .md. Строка «- тип: [[<type>]]» пишется сама.
Данные: ontology.yaml (чтение). Проверка: checks/check_graph.py.
"""
import json
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def _as_list(x):
    return x if isinstance(x, list) else [x]


def render(path, type_, fields, body, links, itog=None):
    front = {"type": type_, **(fields or {})}
    lines = ["---"] + [f"{k}: {v}" for k, v in front.items()] + ["---", f"# {Path(path).stem}", ""]
    if body:
        lines += [body.rstrip(), ""]
    if itog:
        lines += ["## Итог", "", itog.rstrip(), ""]
    lines += ["## Связи", f"- тип: [[{type_}]]"]
    lines += [f"- {rel}: [[{target}]]" for rel, target in links or []]
    return "\n".join(lines) + "\n"


def classes():
    onto = yaml.safe_load(open(ROOT / "ontology.yaml", encoding="utf-8"))
    out = ROOT / "ontology"
    out.mkdir(exist_ok=True)
    for name, c in onto["classes"].items():
        props = [p for p, d in onto["properties"].items() if name in _as_list(d["domain"])]
        attrs = [f"{a} ({', '.join(d['values'])})" for a, d in (onto.get("attributes") or {}).items()
                 if name in _as_list(d["domain"])]
        text = ["---", "kind: класс", "---", f"# {name}", "", c["definition"], "",
                f"Отношения от этого класса: {', '.join(props) or 'нет'}.",
                f"Атрибуты: {', '.join(attrs) or 'нет'}.", "", "## Связи"]
        if c.get("parent"):
            text.append(f"- подклассОт: [[{c['parent']}]]")
        (out / f"{name}.md").write_text("\n".join(text) + "\n", encoding="utf-8")
    obs = ROOT / ".obsidian"
    obs.mkdir(exist_ok=True)
    want = {
        "app.json": {"showUnsupportedFiles": True},
        "graph.json": {"showAttachments": True, "showOrphans": True, "showArrow": True, "colorGroups": [
            {"query": "path:ontology", "color": {"a": 1, "rgb": 9474192}},
            {"query": "[status:открыта OR \"в работе\" OR заблокирована]", "color": {"a": 1, "rgb": 14254635}},
            {"query": "path:tasks", "color": {"a": 1, "rgb": 16761685}},
            {"query": "[type:Эксперимент OR Проверка OR ЗапросКГрафу]", "color": {"a": 1, "rgb": 1153422}},
            {"query": "path:notes OR path:reports", "color": {"a": 1, "rgb": 5987296}}]},
    }
    for fname, keys in want.items():
        p = obs / fname
        cur = json.loads(p.read_text()) if p.exists() else {}
        for k, v in keys.items():
            cur.setdefault(k, v)
        p.write_text(json.dumps(cur, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"заметок классов: {len(onto['classes'])}; .obsidian/ готов")


def apply(spec_path):
    spec = yaml.safe_load(open(spec_path, encoding="utf-8"))
    for n in spec:
        for link in n.get("links") or []:
            if len(link) != 2:
                sys.exit(f"{n['path']}: связь {link} — нужна пара [отношение, цель]; цель с запятой — в кавычках")
        p = ROOT / n["path"]
        if re.search(r"[\\:#|\[\]]", p.stem):
            sys.exit(f"недопустимый символ в названии: {p.stem}")
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(render(n["path"], n["type"], n.get("fields"), n.get("body"), n.get("links"), n.get("itog")),
                     encoding="utf-8")
        print("записано:", n["path"])


def status(path, new, itog=None):
    p = ROOT / path
    text = p.read_text(encoding="utf-8")
    text = re.sub(r"^status: .*$", f"status: {new}", text, count=1, flags=re.M)
    if itog:
        text = re.sub(r"## Итог\n.*?(?=## Связи)", "", text, flags=re.S)
        text = text.replace("## Связи", f"## Итог\n\n{itog.rstrip()}\n\n## Связи", 1)
    p.write_text(text, encoding="utf-8")
    print(f"{path}: status = {new}")


if __name__ == "__main__":
    cmd, args = sys.argv[1], sys.argv[2:]
    if cmd == "classes":
        classes()
    elif cmd == "apply":
        apply(args[0])
    elif cmd == "status":
        itog = args[args.index("--itog") + 1] if "--itog" in args else None
        status(args[0], args[1], itog)
    else:
        sys.exit(__doc__)
