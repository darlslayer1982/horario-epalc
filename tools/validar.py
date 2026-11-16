#!/usr/bin/env python3
"""Valida horario.json antes de publicar. Uso: python3 tools/validar.py horario.json"""
import json, sys, datetime as dt

HORAS = {("09:00","10:00"),("10:15","11:15"),("11:15","12:15"),("13:10","14:10"),("14:10","15:10"),("15:10","16:10")}
erros = []
d = json.load(open(sys.argv[1] if len(sys.argv) > 1 else "horario.json", encoding="utf-8"))
disc = d.get("disciplinas", {})
for k, v in disc.items():
    if not v.get("nome") or not v.get("abrev"): erros.append(f"disciplina {k}: falta nome/abrev")
    if not isinstance(v.get("cor"), int) or not 1 <= v["cor"] <= 8: erros.append(f"disciplina {k}: cor tem de ser 1..8")
try: dt.datetime.fromisoformat(d["atualizado"])
except Exception: erros.append("campo 'atualizado' inválido")
if not d.get("turmas"): erros.append("sem turmas")
for t, td in d.get("turmas", {}).items():
    seg = dt.date.fromisoformat(td["semana"])
    if seg.weekday() != 0: erros.append(f"{t}: 'semana' tem de ser uma segunda-feira")
    dias_validos = {(seg + dt.timedelta(i)).isoformat() for i in range(5)}
    vistos = set(); por_dia = {}
    for a in td["aulas"]:
        tag = f"{t} {a.get('dia')} {a.get('inicio')}"
        if a.get("dia") not in dias_validos: erros.append(f"{tag}: dia fora da semana")
        if (a.get("inicio"), a.get("fim")) not in HORAS: erros.append(f"{tag}: horas fora da grelha ({a.get('inicio')}-{a.get('fim')})")
        if a.get("disciplina") not in disc: erros.append(f"{tag}: disciplina '{a.get('disciplina')}' não definida")
        if (a.get("dia"), a.get("inicio")) in vistos: erros.append(f"{tag}: aula repetida")
        vistos.add((a.get("dia"), a.get("inicio")))
        por_dia[a.get("dia")] = por_dia.get(a.get("dia"), 0) + 1
    if len(td["aulas"]) < 15: erros.append(f"{t}: só {len(td['aulas'])} aulas na semana (esperado 20-35)")
    for dia in sorted(dias_validos):
        if por_dia.get(dia, 0) == 0: erros.append(f"{t}: {dia} sem aulas (feriado? confirmar)")
if erros:
    print("ERROS:"); [print(" -", e) for e in erros]; sys.exit(1)
for t, td in d["turmas"].items():
    print(f"OK {t}: semana {td['semana']}, {len(td['aulas'])} aulas")
