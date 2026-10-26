import json
import re
import time
from pathlib import Path


LEARNING_FILE = Path(__file__).resolve().parents[1] / "data" / "minghat_learning.jsonl"
MAX_LEARNING_ROWS = 300


SECRET_PATTERNS = [
    re.compile(r"(?i)(api[_-]?key|token|secret|password|passwd|authorization|bearer)\s*[:=]\s*[^\s]+"),
    re.compile(r"(?i)AKIA[0-9A-Z]{16}"),
    re.compile(r"(?i)AIza[0-9A-Za-z\-_]{35}"),
    re.compile(r"(?i)gh[pousr]_[0-9A-Za-z_]{20,}"),
]


def _sanitize(value: object, max_len: int = 220) -> str:
    text = str(value or "").strip()
    for pattern in SECRET_PATTERNS:
        text = pattern.sub("[REDACTED]", text)
    return text[:max_len]


def _domain_from_text(text: str) -> str | None:
    match = re.search(r"\b(?:https?://)?(?:www\.)?([a-z0-9.-]+\.[a-z]{2,})\b", text.lower())
    if not match:
        return None
    return match.group(1).strip(".")


def remember_recon_result(result: dict) -> None:
    if not result or not result.get("domain"):
        return

    domain = _sanitize(result.get("domain"), 120)
    interesting = []
    for source in (
        result.get("subdomains", []),
        result.get("live_urls", []),
        result.get("s3", []),
    ):
        for item in source or []:
            value = _sanitize(item)
            low = value.lower()
            if any(term in low for term in ("admin", "api", "login", "auth", "token", "swagger", "graphql", "internal", "dev", "stg", "homolog", "s3", "bucket")):
                interesting.append(value)
            if len(interesting) >= 30:
                break
        if len(interesting) >= 30:
            break

    row = {
        "ts": int(time.time()),
        "kind": "recon_summary",
        "domain": domain,
        "subdomains": len(result.get("subdomains", []) or []),
        "live_urls": len(result.get("live_urls", []) or []),
        "s3": len(result.get("s3", []) or []),
        "interesting": sorted(set(interesting))[:30],
    }

    LEARNING_FILE.parent.mkdir(parents=True, exist_ok=True)
    rows = []
    if LEARNING_FILE.exists():
        rows = [line for line in LEARNING_FILE.read_text(encoding="utf-8", errors="ignore").splitlines() if line.strip()]
    rows.append(json.dumps(row, ensure_ascii=False))
    LEARNING_FILE.write_text("\n".join(rows[-MAX_LEARNING_ROWS:]) + "\n", encoding="utf-8")


def learning_context_for_messages(messages: list[dict], limit: int = 5) -> str:
    if not LEARNING_FILE.exists():
        return ""

    text = "\n".join(str(message.get("content", "")) for message in messages[-8:])
    requested_domain = _domain_from_text(text)
    rows = []
    for line in LEARNING_FILE.read_text(encoding="utf-8", errors="ignore").splitlines():
        try:
            row = json.loads(line)
        except Exception:
            continue
        if row.get("kind") != "recon_summary":
            continue
        if requested_domain and row.get("domain") != requested_domain:
            continue
        rows.append(row)

    if not rows:
        return ""

    parts = ["[MINGHAT APRENDIZADO LOCAL]"]
    for row in rows[-limit:]:
        parts.append(
            f"- {row.get('domain')}: recons anteriores encontraram "
            f"{row.get('subdomains', 0)} subdomínios, {row.get('live_urls', 0)} URLs/serviços web "
            f"e {row.get('s3', 0)} referência(s) S3."
        )
        interesting = row.get("interesting") or []
        if interesting:
            parts.append("  Pontos interessantes já vistos: " + "; ".join(interesting[:12]))

    parts.append("Use este contexto como memória técnica local. Não trate como vulnerabilidade confirmada sem nova validação.")
    return "\n".join(parts)


def clear_learning_store() -> bool:
    if LEARNING_FILE.exists():
        LEARNING_FILE.unlink()
    return True
