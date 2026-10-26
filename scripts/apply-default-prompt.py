#!/usr/bin/env python3
"""Reaplica (idempotente) os system prompts padrao da MingHat.

Chamado no boot pelo start.sh como rede de seguranca, para o prompt padrao
ficar FIXO mesmo em banco/volume novo. Diferente do configure-minghat-models.py,
este script NUNCA apaga modelos nem mexe em configuracao de arena: so garante o
campo params.system dos modelos do KEEP. Best-effort e seguro para rodar sempre.

Retorna 0 quando conseguiu aplicar, 1 quando o banco/tabela ainda nao existe
(o start.sh reexecuta em loop ate o servidor criar as tabelas).
"""
import json
import sqlite3
import sys
import time
from importlib import util as _util
from pathlib import Path

DATABASE = Path(__file__).resolve().parents[1] / "backend" / "data" / "webui.db"
PENTEST_ID = "dolphin-llama3:latest"

# Fonte unica dos textos de prompt: reaproveita o script de configuracao.
_cfg_path = Path(__file__).resolve().parent / "configure-minghat-models.py"
_spec = _util.spec_from_file_location("_mh_cfg", _cfg_path)
_cfg = _util.module_from_spec(_spec)
_spec.loader.exec_module(_cfg)


def system_for(model_id: str) -> str:
    if model_id == PENTEST_ID:
        return _cfg.DEFAULT_SYSTEM_PROMPT + "\n\n" + _cfg.PENTESTING_SYSTEM_PROMPT
    return _cfg.DEFAULT_SYSTEM_PROMPT


def main() -> int:
    if not DATABASE.is_file():
        print("apply-default-prompt: banco ainda nao existe", file=sys.stderr)
        return 1
    con = sqlite3.connect(str(DATABASE))
    try:
        con.execute("SELECT 1 FROM model LIMIT 1")
    except sqlite3.OperationalError:
        print("apply-default-prompt: tabela 'model' ainda nao existe", file=sys.stderr)
        return 1

    now = int(time.time())
    owner = con.execute("SELECT id FROM user ORDER BY created_at LIMIT 1").fetchone()
    changed = 0
    # Fonte unica do prompt = middleware. Aqui so garantimos que os modelos
    # existem, com o nome certo, ativos e SEM system no params (sem duplicar).
    for model_id, name in _cfg.KEEP.items():
        row = con.execute("SELECT params, name FROM model WHERE id = ?", (model_id,)).fetchone()
        if row is not None:
            params = json.loads(row[0] or "{}")
            params.pop("system", None)  # remove qualquer prompt duplicado do banco
            if row[1] == name and json.loads(row[0] or "{}").get("system") in (None, ""):
                continue
            con.execute(
                "UPDATE model SET name = ?, params = ?, is_active = 1, updated_at = ? WHERE id = ?",
                (name, json.dumps(params), now, model_id),
            )
            changed += 1
        elif owner:
            con.execute(
                """INSERT INTO model
                   (id, user_id, base_model_id, name, params, meta, is_active, updated_at, created_at)
                   VALUES (?, ?, NULL, ?, '{}', ?, 1, ?, ?)""",
                (
                    model_id,
                    owner[0],
                    name,
                    json.dumps({"capabilities": {"memory": True}}),
                    now,
                    now,
                ),
            )
            changed += 1
    con.commit()
    con.close()
    print(f"apply-default-prompt: prompts reaplicados (alteracoes: {changed})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
