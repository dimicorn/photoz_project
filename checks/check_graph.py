"""Проверка онтологии и графа проекта: .venv/bin/python checks/check_graph.py [--strict]

Замена check_week4.py курса (его нет в общей папке). Код 0 — обязательные пункты
выполнены; с --strict нарушения правил онтологии тоже считаются ошибками.
Мир закрытый: «не найдено» значит «не записано в заметках».
"""
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
STRICT = "--strict" in sys.argv
errors, rule_viol, tips = [], [], []
ok = lambda msg: print(f"[OK]    {msg}")
L = lambda x: x if isinstance(x, list) else [x]

onto = yaml.safe_load(open(ROOT / "ontology.yaml", encoding="utf-8"))
C, P, A = onto["classes"], onto["properties"], onto.get("attributes") or {}

# --- онтология
print("== Онтология")
for name, c in C.items():
    if c.get("parent") and c["parent"] not in C:
        errors.append(f"класс {name}: надкласс {c['parent']} не определён")
for p, d in P.items():
    for cl in L(d["domain"]) + L(d["range"]):
        if cl not in C:
            errors.append(f"отношение {p}: класс {cl} не определён")
n_rules = len(onto.get("rules") or [])
(ok if len(C) >= 3 and n_rules >= 2 else errors.append)(f"классов — {len(C)}, отношений — {len(P)}, правил — {n_rules}")
missing = [n for n in C if not (ROOT / "ontology" / f"{n}.md").is_file()]
if missing:
    errors.append(f"классы без заметки в ontology/: {', '.join(missing)}")
else:
    ok(f"заметки классов в ontology/ — {len(C)}")


def ancestors(cl):
    out = []
    while cl:
        out.append(cl)
        cl = C.get(cl, {}).get("parent")
    return out


def isa(cl, targets):
    return any(t in ancestors(cl) for t in L(targets))


# --- граф
print("== Граф")
for f in [".obsidian/app.json", ".obsidian/graph.json"]:
    if not (ROOT / f).is_file():
        errors.append(f"нет {f}")
nodes = {}
for folder in ["notes", "tasks", "reports"]:
    for p in sorted((ROOT / folder).glob("*.md")) if (ROOT / folder).is_dir() else []:
        text = p.read_text(encoding="utf-8")
        m = re.match(r"---\n(.*?)\n---\n", text, re.S)
        front = yaml.safe_load(m.group(1)) if m else {}
        links = []
        if "## Связи" in text:
            for rel, tgt in re.findall(r"^- ([^:\n]+): \[\[([^\]|]+)(?:\|[^\]]*)?\]\]", text.split("## Связи", 1)[1], re.M):
                links.append((rel.strip(), tgt.strip()))
        nodes[p.stem] = {"path": p.relative_to(ROOT), "type": (front or {}).get("type"), "front": front or {},
                         "links": links, "text": text}

typed = {k: v for k, v in nodes.items() if v["type"]}
for name, n in nodes.items():
    t = n["type"]
    if not t:
        errors.append(f"{n['path']}: нет поля type")
        continue
    if t not in C:
        tips.append(f"тип «{t}» ({n['path']}) — нет в онтологии")
    if name in C:
        errors.append(f"{n['path']}: заметка названа как класс")
    if ("тип", t) not in n["links"]:
        errors.append(f"{n['path']}: нет строки «- тип: [[{t}]]»")
    for attr, d in A.items():
        if attr in n["front"] and isa(t, d["domain"]) and str(n["front"][attr]) not in map(str, d["values"]):
            errors.append(f"{n['path']}: {attr} = {n['front'][attr]} — вне списка {d['values']}")
    if t == "Задача" and "status" not in n["front"]:
        errors.append(f"{n['path']}: у задачи нет status")

edges = []        # (источник, отношение, цель, класс цели)
n_files = set()
for name, n in typed.items():
    for rel, tgt in n["links"]:
        if rel == "тип":
            if tgt not in C:
                tips.append(f"{n['path']}: тип [[{tgt}]] не класс онтологии")
            continue
        if rel not in P:
            errors.append(f"{n['path']}: отношение «{rel}» нет в онтологии")
            continue
        if tgt in C:
            errors.append(f"{n['path']}: {rel} ведёт к классу [[{tgt}]] — нужен экземпляр")
            continue
        if tgt in typed:
            tcl = typed[tgt]["type"]
        elif (ROOT / tgt).exists():
            tcl = "Файл"
            n_files.add(tgt)
        else:
            errors.append(f"{n['path']}: {rel}: [[{tgt}]] — нет ни заметки, ни файла")
            continue
        d = P[rel]
        if not isa(n["type"], d["domain"]):
            errors.append(f"{n['path']}: {rel} — тип {n['type']} вне области определения {d['domain']}")
        if not isa(tcl, d["range"]):
            errors.append(f"{n['path']}: {rel} → [[{tgt}]] ({tcl}) вне области значений {d['range']}")
        edges.append((name, rel, tgt, tcl))

(ok if len(typed) >= 10 else errors.append)(f"объектов с типом — {len(typed)}; файлов в связях — {len(n_files)}")
ok(f"типизированных связей — {len(edges)}")
by_status = Counter(n["front"].get("status") for n in typed.values() if n["type"] == "Задача")
if by_status:
    ok("задачи по статусам: " + ", ".join(f"{s} — {c}" for s, c in by_status.items()))

# --- правила
print("== Правила")
out = defaultdict(set)    # (узел, отношение) -> цели
inc = defaultdict(set)    # (узел, отношение) -> источники
for s, r, t, _ in edges:
    out[(s, r)].add(t)
    inc[(t, r)].add(s)
derived = {}


def members(cl):
    if cl in derived:
        return derived[cl]
    return {k for k, v in typed.items() if isa(v["type"], cl)}


def tclass(x):
    return typed[x]["type"] if x in typed else "Файл"


for rule in onto.get("rules") or []:
    ch = rule.get("check")
    if not ch:
        continue
    k, rid = ch["kind"], rule["id"]
    bad = []
    if k == "some":
        bad = [x for x in members(ch["class"]) if not any(isa(tclass(t), ch["target"]) for t in out[(x, ch["property"])])]
    elif k == "some_all":
        bad = [x for x in members(ch["class"]) for p in ch["properties"]
               if not any(isa(tclass(t), ch["target"]) for t in out[(x, p)])]
    elif k == "some_inverse":
        bad = [x for x in members(ch["class"]) if not any(isa(tclass(s), ch["source"]) for s in inc[(x, ch["property"])])]
    elif k == "defined":
        derived[ch["name"]] = {x for x in members(ch["class"])
                               if any(isa(tclass(t), ch["target"]) for t in out[(x, ch["property"])])}
        ok(f"вывод по {rid}: {ch['name']} = {{{', '.join(sorted(derived[ch['name']])) or '∅'}}}")
        continue
    elif k == "defined_value":
        derived[ch["name"]] = {x for x in members(ch["class"]) if str(typed[x]["front"].get(ch["attribute"])) in ch["values"]}
        ok(f"вывод по {rid}: {ch['name']} — {len(derived[ch['name']])}")
        continue
    elif k == "disjoint_properties":
        p1, p2 = ch["properties"]
        bad = [s for (s, r), ts in list(out.items()) if r == p1 and ts & out[(s, p2)]]
    elif k == "some_inverse_any":
        bad = [x for x in members(ch["class"]) if not any(inc[(x, p)] for p in ch["properties"])]
    elif k == "all_inverse":
        src = members(ch["source"])
        bad = [x for x in members(ch["class"]) if not inc[(x, ch["property"])] <= src]
    elif k == "section":
        bad = [x for x in members(ch["class"]) if f"## {ch['section']}" not in typed[x]["text"]]
    if bad:
        rule_viol.append(f"{rid}: {rule['text']} Не выполнено для: {', '.join(sorted(set(bad)))}")
    else:
        ok(f"правило {rid} выполнено")

for t in tips:
    print(f"[СОВЕТ] {t}")
for r in rule_viol:
    print(f"[ПРАВИЛО] {r}")
for e in errors:
    print(f"[НЕТ]   {e}")
fail = errors or (STRICT and rule_viol)
print("Есть что исправить." if fail else "Все обязательные пункты выполнены.")
sys.exit(1 if fail else 0)
