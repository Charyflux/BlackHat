import asyncio
import os
import re
import shutil
import time
from collections.abc import Awaitable, Callable
from pathlib import Path
from urllib.parse import urlparse


PENTESTING_MODEL_ID = os.getenv("MINGHAT_PENTEST_MODEL_ID", "dolphin-llama3:latest")
RECON_TERMS = re.compile(
    r"\b(?:recon|reconhecimento|subfinder|enumer(?:ar|e|aÃ§Ã£o)\s+(?:de\s+)?subdom[iÃ­]nios?|"
    r"buscar\s+subdom[iÃ­]nios?|descobrir\s+subdom[iÃ­]nios?)\b",
    re.IGNORECASE,
)
DOMAIN_CANDIDATE = re.compile(
    r"(?<![\w@])(?:https?://)?(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+"
    r"[a-z]{2,63}(?::\d+)?(?:/[^\s]*)?",
    re.IGNORECASE,
)
MAX_OUTPUT_CHARS = int(os.getenv("MINGHAT_RECON_MAX_OUTPUT_CHARS", "60000"))
MAX_CONTEXT_SUBDOMAINS = int(os.getenv("MINGHAT_RECON_MAX_CONTEXT_SUBDOMAINS", "1000"))
MAX_STAGE_OUTPUT_CHARS = int(os.getenv("MINGHAT_RECON_MAX_STAGE_OUTPUT_CHARS", "20000"))
SUBFINDER_TIMEOUT_SECONDS = int(os.getenv("MINGHAT_SUBFINDER_TIMEOUT_SECONDS", "45"))
RECON_STAGE_TIMEOUT_SECONDS = int(os.getenv("MINGHAT_RECON_STAGE_TIMEOUT_SECONDS", "25"))
DNSX_TIMEOUT_SECONDS = int(os.getenv("MINGHAT_DNSX_TIMEOUT_SECONDS", str(RECON_STAGE_TIMEOUT_SECONDS)))
HTTPX_TIMEOUT_SECONDS = int(os.getenv("MINGHAT_HTTPX_TIMEOUT_SECONDS", "60"))
KATANA_TIMEOUT_SECONDS = int(os.getenv("MINGHAT_KATANA_TIMEOUT_SECONDS", "30"))
GAU_TIMEOUT_SECONDS = int(os.getenv("MINGHAT_GAU_TIMEOUT_SECONDS", "20"))
# Quando ligado (padrao), o painel ao vivo nao expoe o nome da ferramenta nem os
# comandos/flags — mostra apenas rotulos genericos por etapa e os resultados.
HIDE_RECON_TOOLS = os.getenv("MINGHAT_RECON_HIDE_TOOLS", "1").strip().lower() not in ("0", "false", "no", "off", "")
# Rotulo generico por ferramenta usado quando HIDE_RECON_TOOLS esta ativo.
RECON_TOOL_LABELS = {
    "subfinder": "subdominio",
    "dnsx": "dns",
    "httpx": "web",
    "gau": "url",
    "katana": "url",
}


def recon_stage_label(tool: str) -> str:
    """Rotulo exibido no lugar do nome da ferramenta no painel ao vivo."""
    if HIDE_RECON_TOOLS:
        return RECON_TOOL_LABELS.get(tool, tool)
    return tool


# Extensoes de arquivos estaticos ("lixo") descartadas das URLs coletadas.
# Sobrescreva com MINGHAT_RECON_JUNK_EXTENSIONS="png,jpg,css,..." (lista separada por virgulas).
_DEFAULT_JUNK_EXTENSIONS = (
    "png,jpg,jpeg,gif,svg,webp,ico,bmp,tiff,tif,avif,heic,"  # imagens
    "css,scss,sass,less,map,"                                  # estilos / sourcemaps
    "woff,woff2,ttf,otf,eot,"                                  # fontes
    "mp4,webm,mp3,wav,ogg,oga,avi,mov,mkv,m4a,m4v,flv,"        # midia
    "xml,rss,atom,"                                            # feeds / xml
    "pdf,doc,docx,xls,xlsx,ppt,pptx,zip,rar,7z,gz,tar"        # binarios/documentos
)
JUNK_URL_EXTENSIONS = {
    ext.strip().lstrip(".").lower()
    for ext in os.getenv("MINGHAT_RECON_JUNK_EXTENSIONS", _DEFAULT_JUNK_EXTENSIONS).split(",")
    if ext.strip()
}


def url_extension(url: str) -> str:
    """Extensao (sem ponto, minuscula) do ultimo segmento do caminho, ignorando query/fragmento."""
    candidate = (url or "").strip()
    try:
        path = urlparse(candidate).path
    except ValueError:
        path = candidate
    last_segment = path.rsplit("/", 1)[-1]
    if "." not in last_segment:
        return ""
    return last_segment.rsplit(".", 1)[-1].lower()


def is_junk_url(url: str) -> bool:
    """True se a URL aponta para um arquivo estatico de extensao ignorada."""
    return url_extension(url) in JUNK_URL_EXTENSIONS


def _dedupe_key(url: str) -> str:
    """Chave de deduplicacao: ignora barra final e diferencas de caixa em esquema/host."""
    stripped = url.strip()
    try:
        parts = urlparse(stripped)
        if parts.scheme and parts.netloc:
            rebuilt = f"{parts.scheme.lower()}://{parts.netloc.lower()}{parts.path}"
            if parts.query:
                rebuilt += f"?{parts.query}"
            return rebuilt.rstrip("/")
    except ValueError:
        pass
    return stripped.rstrip("/")


def clean_urls(lines, seen: set | None = None) -> list[str]:
    """Remove URLs de arquivos-lixo e duplicadas, preservando a ordem de descoberta.

    Passe o mesmo `seen` entre etapas para deduplicar tambem entre ferramentas.
    """
    if seen is None:
        seen = set()
    result: list[str] = []
    for raw in lines:
        url = (raw or "").strip()
        if not url or is_junk_url(url):
            continue
        key = _dedupe_key(url)
        if key in seen:
            continue
        seen.add(key)
        result.append(url)
    return result
BLOCKED_RECON_SUFFIXES = {
    "localhost",
    "local",
    "lan",
    "home",
    "internal",
    "corp",
    "test",
    "example",
    "invalid",
    "onion",
    "nip.io",
    "sslip.io",
    "xip.io",
    "localtest.me",
}
HOSTNAME_LINE = re.compile(
    r"(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,63}", re.IGNORECASE
)
NETWORK_DENIED_MARKERS = (
    "connectex:",
    "permission denied",
    "permissions",
    "acesso a uma socket",
    "acesso proibida",
)


INTERESTING_RECON_TERMS = (
    "admin",
    "api",
    "login",
    "auth",
    "token",
    "swagger",
    "openapi",
    "graphql",
    "internal",
    "interno",
    "vpn",
    "citrix",
    "webmail",
    "cpanel",
    "dev",
    "stg",
    "stage",
    "homolog",
    "qas",
    "s3",
    "bucket",
    "cloudfront",
    "azure",
)
INTERESTING_STATUS_CODES = {"401", "403", "404", "500", "502", "503"}


def recon_alert_prefix(value: str, status: str = "") -> str:
    text = (value or "").lower()
    if status in INTERESTING_STATUS_CODES or any(term in text for term in INTERESTING_RECON_TERMS):
        return "🚨 "
    return ""

def normalize_domain(candidate: str) -> str | None:
    value = candidate.strip().rstrip(".,;:!?)\"]}")
    try:
        parsed = urlparse(value if "://" in value else f"//{value}")
    except ValueError:
        return None
    hostname = parsed.hostname
    if not hostname:
        return None
    try:
        hostname = hostname.encode("idna").decode("ascii").lower().rstrip(".")
    except UnicodeError:
        return None
    if len(hostname) > 253 or "." not in hostname:
        return None
    labels = hostname.split(".")
    if any(not label or len(label) > 63 for label in labels):
        return None
    if any(not re.fullmatch(r"[a-z0-9](?:[a-z0-9-]*[a-z0-9])?", label) for label in labels):
        return None
    return hostname


def normalize_recon_domain(candidate: str) -> str | None:
    domain = normalize_domain(candidate)
    if not domain:
        return None
    if domain.startswith("www."):
        return domain[4:]
    return domain


def recon_domain_allowed(domain: str) -> bool:
    labels = domain.split(".")
    suffixes = {".".join(labels[index:]) for index in range(len(labels))}
    if suffixes & BLOCKED_RECON_SUFFIXES:
        return False

    allowed_domains = {
        item.strip().lower().rstrip(".")
        for item in os.getenv("MINGHAT_RECON_ALLOWED_DOMAINS", "").split(",")
        if item.strip()
    }
    if not allowed_domains:
        return True
    return any(domain == allowed or domain.endswith(f".{allowed}") for allowed in allowed_domains)


def extract_target_hostnames(text: str, domain: str) -> list[str]:
    found: set[str] = set()
    for line in text.splitlines():
        for match in HOSTNAME_LINE.finditer(line):
            hostname = match.group(0).lower().rstrip(".")
            if hostname == domain or hostname.endswith(f".{domain}"):
                found.add(hostname)
    return sorted(found)


def requested_recon_domain(model_id: str, messages: list[dict]) -> str | None:
    if model_id != PENTESTING_MODEL_ID:
        return None
    last_user = next((m for m in reversed(messages) if m.get("role") == "user"), None)
    content = last_user.get("content", "") if last_user else ""
    if isinstance(content, list):
        content = " ".join(
            part.get("text", "") for part in content if isinstance(part, dict) and part.get("type") == "text"
        )
    if not isinstance(content, str) or not RECON_TERMS.search(content):
        return None
    match = DOMAIN_CANDIDATE.search(content)
    domain = normalize_recon_domain(match.group(0)) if match else None
    if not domain or not recon_domain_allowed(domain):
        return None
    return domain


def find_subfinder() -> str | None:
    configured = os.getenv("SUBFINDER_PATH")
    candidates = [
        configured,
        shutil.which("subfinder"),
        str(Path(__file__).resolve().parents[3] / ".runtime" / "tools" / "subfinder.exe"),
        str(Path(__file__).resolve().parents[3] / ".runtime" / "tools" / "subfinder"),
    ]
    return next((path for path in candidates if path and Path(path).is_file()), None)


def find_recon_tool(name: str) -> str | None:
    tools_dir = Path(os.getenv("MINGHAT_RECON_TOOLS_DIR", Path(__file__).resolve().parents[3] / ".runtime" / "tools"))
    configured = os.getenv(f"{name.upper()}_PATH")
    candidates = [configured, shutil.which(name), str(tools_dir / f"{name}.exe"), str(tools_dir / name)]
    return next((path for path in candidates if path and Path(path).is_file()), None)


async def run_recon_command(name: str, args: list[str], stdin: str = "", *, timeout_seconds: int = RECON_STAGE_TIMEOUT_SECONDS) -> dict:
    executable = find_recon_tool(name)
    if not executable:
        return {"ok": False, "output": "", "error": f"{name} nÃ£o estÃ¡ instalado."}
    process = await asyncio.create_subprocess_exec(
        executable,
        *args,
        stdin=asyncio.subprocess.PIPE if stdin else None,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    try:
        stdout, stderr = await asyncio.wait_for(
            process.communicate(stdin.encode() if stdin else None), timeout=timeout_seconds
        )
    except asyncio.TimeoutError:
        process.kill()
        stdout, stderr = await process.communicate()
        output = stdout.decode("utf-8", errors="replace").strip()
        diagnostic = stderr.decode("utf-8", errors="replace").strip()
        return {
            "ok": bool(output),
            "output": output[:MAX_STAGE_OUTPUT_CHARS],
            "diagnostic": diagnostic[-10_000:],
            "error": "" if output else f"{name} excedeu {timeout_seconds} segundos.",
            "timed_out": True,
        }
    output = stdout.decode("utf-8", errors="replace").strip()
    diagnostic = stderr.decode("utf-8", errors="replace").strip()
    return {
        "ok": process.returncode == 0,
        "output": output[:MAX_STAGE_OUTPUT_CHARS],
        "diagnostic": diagnostic[-10_000:],
        "error": "" if process.returncode == 0 else diagnostic[-1_000:],
    }


S3_PATTERNS = (
    re.compile(r"https?://([a-z0-9][a-z0-9.-]{1,62})\.s3(?:[.-][a-z0-9-]+)?\.amazonaws\.com", re.I),
    re.compile(r"https?://s3(?:[.-][a-z0-9-]+)?\.amazonaws\.com/([a-z0-9][a-z0-9.-]{1,62})", re.I),
    re.compile(r"s3://([a-z0-9][a-z0-9.-]{1,62})", re.I),
)


def extract_s3_references(text: str) -> list[str]:
    return sorted({match.group(1).lower() for pattern in S3_PATTERNS for match in pattern.finditer(text)})


def extract_s3_technology_hosts(httpx_output: str) -> list[str]:
    hosts: set[str] = set()
    for line in httpx_output.splitlines():
        if "amazon s3" not in line.lower():
            continue
        match = re.match(r"https?://([^\s/\]]+)", line.strip(), re.IGNORECASE)
        if match:
            hosts.add(match.group(1).lower().rstrip("."))
    return sorted(hosts)



def parse_httpx_endpoint(line: str) -> dict:
    stripped = line.strip()
    match = re.match(r"(https?://[^\s]+)", stripped)
    url = match.group(1) if match else stripped
    status_match = re.search(r"\[(\d{3})\]", stripped)
    status = status_match.group(1) if status_match else ""
    title = ""
    bracket_values = re.findall(r"\[([^\]]+)\]", stripped)
    for value in bracket_values:
        if value != status and not value.lower().startswith("http"):
            title = value
            break
    return {"url": url, "status": status, "title": title, "raw": stripped}


def parse_dns_line(line: str) -> dict:
    stripped = line.strip()
    host_match = re.match(r"([^\s]+)", stripped)
    values = re.findall(r"\[([^\]]+)\]", stripped)
    return {
        "host": host_match.group(1) if host_match else stripped,
        "type": values[0] if values else "",
        "value": values[1] if len(values) > 1 else "",
        "raw": stripped,
    }

async def run_subfinder(domain: str, timeout_seconds: int = SUBFINDER_TIMEOUT_SECONDS) -> dict:
    if not recon_domain_allowed(domain):
        return {
            "ok": False,
            "domain": domain,
            "error": "DomÃ­nio fora da polÃ­tica de recon do MingHat.",
        }

    executable = find_subfinder()
    if not executable:
        return {
            "ok": False,
            "domain": domain,
            "error": "Subfinder nÃ£o estÃ¡ instalado no ambiente MingHat.",
        }

    process = await asyncio.create_subprocess_exec(
        executable,
        "-d",
        domain,
        "-all",
        "-t",
        "100",
        "-v",
        "-nc",
        "-duc",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    try:
        stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=timeout_seconds)
    except asyncio.TimeoutError:
        process.kill()
        await process.communicate()
        return {"ok": False, "domain": domain, "error": f"O recon excedeu o limite de {timeout_seconds} segundos."}

    output = stdout.decode("utf-8", errors="replace").strip()
    diagnostic = stderr.decode("utf-8", errors="replace").strip()
    all_subdomains = extract_target_hostnames(output, domain)
    network_denied = any(marker in diagnostic.lower() for marker in NETWORK_DENIED_MARKERS)
    ok = process.returncode == 0 and (bool(all_subdomains) or not network_denied)
    subdomains = all_subdomains[:MAX_CONTEXT_SUBDOMAINS]
    return {
        "ok": ok,
        "domain": domain,
        "command": f"subfinder -d {domain} -all -t 100 -v",
        "subdomains": subdomains,
        "total": len(all_subdomains),
        "truncated": len(all_subdomains) > len(subdomains),
        "output": "\n".join(subdomains)[:MAX_OUTPUT_CHARS],
        "diagnostic": diagnostic[-20_000:],
        "error": "Subfinder executou, mas as fontes externas foram bloqueadas pela rede/permissÃ£o do processo." if network_denied and not all_subdomains else "",
        "returncode": process.returncode,
    }


async def run_basic_recon(domain: str, progress: Callable[[object], Awaitable[None]] | None = None) -> dict:
    started_at = time.time()

    async def emit(line: str) -> None:
        if progress:
            await progress(line)

    def stamp() -> str:
        return f"{int(time.time() - started_at):02d}s"

    await emit(f"[{stamp()}] > alvo: {domain}")
    await emit(f"[{stamp()}] > Analisando o alvo por completo. Dependendo do porte da infraestrutura, isso pode levar alguns minutos — pode aguardar, a analise segue em andamento.")
    await emit(f"[{stamp()}] > Mapeando a infraestrutura completa de {domain}...")
    if HIDE_RECON_TOOLS:
        await emit(f"[{stamp()}] > enumerando subdominios")
    else:
        await emit(f"[{stamp()}] > subfinder -d {domain} -all -t 100 -v")
    subfinder = await run_subfinder(domain)
    if not subfinder.get("ok"):
        await emit(f"[{stamp()}] x {recon_stage_label('subfinder')}: {subfinder.get('error') or 'falhou'}")
        return subfinder

    await emit(
        f"[{stamp()}] ok {recon_stage_label('subfinder')}: {subfinder.get('total', len(subfinder.get('subdomains', [])))} subdominios"
    )
    for host in subfinder.get("subdomains", []):
        await emit(f"[{stamp()}] {recon_alert_prefix(host)}{recon_stage_label('subfinder')} -> {host}")
    await emit({"subdomains": subfinder.get("subdomains", [])})
    hosts = [domain, *subfinder.get("subdomains", [])]
    host_input = "\n".join(dict.fromkeys(hosts[:MAX_CONTEXT_SUBDOMAINS])) + "\n"

    # ------------------------------------------------------------------
    # Ordem de recon (metodologia): subfinder -> dnsx -> httpx, com o gau
    # passivo rodando em paralelo desde o inicio.
    #   1) dnsx resolve os subdominios e separa apenas os hosts VIVOS;
    #   2) httpx so prova os hosts que resolveram (sinal limpo, menos ruido);
    #   3) gau (passivo, so depende do dominio) roda em paralelo, sem atrasar;
    #   4) katana faz o crawl apenas dos servicos web confirmados (mais abaixo).
    # ------------------------------------------------------------------

    # gau e passivo e depende apenas do dominio: dispara ja em paralelo com dnsx/httpx.
    gau_task = asyncio.create_task(
        run_recon_command(
            "gau",
            ["--providers", "wayback", "--threads", "10", "--timeout", "10", "--subs", domain],
            timeout_seconds=GAU_TIMEOUT_SECONDS,
        )
    )
    seen_urls: set[str] = set()

    # Etapa 1 - resolucao DNS de todos os subdominios encontrados.
    if HIDE_RECON_TOOLS:
        await emit(f"[{stamp()}] > resolvendo DNS de {len(hosts)} hosts")
    else:
        await emit(f"[{stamp()}] > dnsx: resolvendo {len(hosts)} hosts")
    dnsx = await run_recon_command(
        "dnsx", ["-silent", "-a", "-resp", "-nc", "-duc"], host_input, timeout_seconds=DNSX_TIMEOUT_SECONDS
    )
    dns_lines = [line for line in dnsx.get("output", "").splitlines() if line.strip()]
    dns_count = len(dns_lines)
    await emit(f"[{stamp()}] ok {recon_stage_label('dnsx')}: {dns_count} registros")
    for line in dns_lines:
        await emit(f"[{stamp()}] {recon_alert_prefix(line)}{recon_stage_label('dnsx')} -> {line}")
    await emit({"dns": [parse_dns_line(line) for line in dns_lines]})

    # Hosts que realmente resolveram -> alvos do httpx (so o que esta vivo).
    resolved_hosts = list(dict.fromkeys(parse_dns_line(line)["host"] for line in dns_lines))
    httpx_targets = resolved_hosts or list(dict.fromkeys(hosts[:MAX_CONTEXT_SUBDOMAINS]))
    httpx_input = "\n".join(httpx_targets) + "\n"

    # Etapa 2 - httpx apenas nos hosts resolvidos.
    if HIDE_RECON_TOOLS:
        await emit(f"[{stamp()}] > verificando servicos web em {len(httpx_targets)} hosts vivos")
    else:
        await emit(f"[{stamp()}] > httpx: verificando servicos web em {len(httpx_targets)} hosts vivos")
    httpx = await run_recon_command(
        "httpx",
        [
            "-silent",
            "-status-code",
            "-title",
            "-tech-detect",
            "-follow-redirects",
            "-nc",
            "-duc",
            "-threads",
            "50",
            "-timeout",
            "8",
        ],
        httpx_input,
        timeout_seconds=HTTPX_TIMEOUT_SECONDS,
    )
    http_lines = [line for line in httpx.get("output", "").splitlines() if line.strip()]
    http_count = len(http_lines)
    await emit(f"[{stamp()}] ok {recon_stage_label('httpx')}: {http_count} servicos/URLs")
    for line in http_lines:
        await emit(f"[{stamp()}] {recon_alert_prefix(line, parse_httpx_endpoint(line).get('status', ''))}{recon_stage_label('httpx')} -> {line}")
    httpx_endpoints = [parse_httpx_endpoint(line) for line in http_lines]
    await emit({"endpoints": httpx_endpoints})

    # Etapa 3 - coleta passiva (gau), que rodou em paralelo; agora consolidamos.
    if HIDE_RECON_TOOLS:
        await emit(f"[{stamp()}] > coletando URLs historicas")
    else:
        await emit(f"[{stamp()}] > gau: coletando URLs historicas")
    gau = await gau_task
    # Descarta arquivos-lixo (imagens, css, fontes, xml, midia...) e URLs duplicadas.
    gau_raw_count = len([line for line in gau.get("output", "").splitlines() if line.strip()])
    gau_urls = clean_urls(gau.get("output", "").splitlines(), seen=seen_urls)
    gau["output"] = "\n".join(gau_urls)
    gau_hidden = gau_raw_count - len(gau_urls)
    gau_count = len(gau_urls)
    gau_suffix = f" ({gau_hidden} arquivos estaticos ocultados)" if gau_hidden > 0 else ""
    await emit(f"[{stamp()}] {'ok' if gau.get('ok') else 'aviso'} {recon_stage_label('gau')}: {gau_count} URLs{gau_suffix}")
    for line in gau_urls:
        await emit(f"[{stamp()}] {recon_alert_prefix(line)}{recon_stage_label('gau')} -> {line}")
    if gau_count:
        await emit({"endpoints": [*httpx_endpoints, *[{"url": u, "status": "", "title": "GAU", "raw": u} for u in gau_urls]]})

    live_urls = []
    for line in httpx.get("output", "").splitlines():
        match = re.match(r"(https?://[^\s]+)", line.strip())
        if match:
            live_urls.append(match.group(1))

    katana_input = "\n".join(dict.fromkeys(live_urls[:10])) + ("\n" if live_urls else "")
    if HIDE_RECON_TOOLS:
        await emit(f"[{stamp()}] > crawl basico em {len(dict.fromkeys(live_urls[:10]))} URLs")
    else:
        await emit(f"[{stamp()}] > katana: crawl basico em {len(dict.fromkeys(live_urls[:10]))} URLs")
    katana = (
        await run_recon_command(
            "katana",
            ["-silent", "-d", "1", "-c", "5", "-p", "5", "-nc", "-duc", "-timeout", "8"],
            katana_input,
            timeout_seconds=KATANA_TIMEOUT_SECONDS,
        )
        if katana_input
        else {"ok": True, "output": "", "diagnostic": "Nenhum servico HTTP para rastrear."}
    )
    # Mesmo filtro de lixo/duplicadas, deduplicando tambem contra as URLs do gau.
    katana_raw_count = len([line for line in katana.get("output", "").splitlines() if line.strip()])
    katana_urls = clean_urls(katana.get("output", "").splitlines(), seen=seen_urls)
    katana["output"] = "\n".join(katana_urls)
    katana_hidden = katana_raw_count - len(katana_urls)
    katana_count = len(katana_urls)
    katana_suffix = f" ({katana_hidden} arquivos estaticos ocultados)" if katana_hidden > 0 else ""
    await emit(f"[{stamp()}] ok {recon_stage_label('katana')}: {katana_count} URLs coletadas{katana_suffix}")
    for line in [line for line in katana.get("output", "").splitlines() if line.strip()]:
        await emit(f"[{stamp()}] {recon_alert_prefix(line)}{recon_stage_label('katana')} -> {line}")
    katana_endpoints = [{"url": line.strip(), "status": "", "title": "Katana", "raw": line.strip()} for line in katana.get("output", "").splitlines() if line.strip()]
    await emit({"endpoints": [*httpx_endpoints, *katana_endpoints]})

    await emit(f"[{stamp()}] > S3: extraindo referencias")
    s3 = sorted(
        set(extract_s3_references("\n".join([httpx.get("output", ""), katana.get("output", ""), gau.get("output", "")])) )
        | set(extract_s3_technology_hosts(httpx.get("output", "")))
    )
    await emit(f"[{stamp()}] ok S3: {len(s3[:1000])} referencia(s)")
    for item in s3:
        await emit(f"[{stamp()}] 🚨 s3 -> {item}")
    await emit({"s3": s3[:1000]})
    await emit(f"[{stamp()}] ok pipeline concluido")

    return {
        **subfinder,
        "dnsx": dnsx,
        "httpx": httpx,
        "katana": katana,
        "gau": gau,
        "s3": s3[:1000],
        "live_urls": live_urls[:1000],
    }

def recon_context(result: dict) -> str:
    if not result.get("ok"):
        return (
            "[MINGHAT RECON]\n"
            f"O recon automÃ¡tico de {result['domain']} falhou: {result.get('error') or result.get('diagnostic')}. "
            "Explique a falha de forma objetiva e nÃ£o invente resultados."
        )
    subdomains = result.get("subdomains", [])
    subdomain_header = (
        "[MINGHAT RECON - RESULTADO REAL]" if HIDE_RECON_TOOLS else "[MINGHAT RECON - RESULTADO REAL DO SUBFINDER]"
    )
    command_line = "" if HIDE_RECON_TOOLS else f"Comando: {result['command']}\n"
    sections = [
        f"{subdomain_header}\n"
        f"Alvo: {result['domain']}\n{command_line}"
        f"Total encontrado: {result.get('total', len(subdomains))}\n"
        f"Resultados enviados para anÃ¡lise: {len(subdomains)}"
        f"{' (lista limitada para caber no contexto)' if result.get('truncated') else ''}\n"
        f"SubdomÃ­nios:\n{result.get('output') or '(nenhum encontrado)'}"
    ]
    if HIDE_RECON_TOOLS:
        stage_labels = (("DNS resolvido", "dnsx"), ("ServiÃ§os web", "httpx"), ("Crawl bÃ¡sico", "katana"), ("URLs histÃ³ricas", "gau"))
    else:
        stage_labels = (("DNS resolvido (DNSx)", "dnsx"), ("ServiÃ§os web (HTTPx)", "httpx"), ("Crawl bÃ¡sico (Katana)", "katana"), ("URLs histÃ³ricas (GAU)", "gau"))
    for label, key in stage_labels:
        stage = result.get(key, {})
        sections.append(f"\n[{label}]\n{stage.get('output') or stage.get('error') or '(sem resultados)'}")
    sections.append(f"\n[ReferÃªncias S3]\n" + ("\n".join(result.get("s3", [])) or "(nenhuma encontrada)"))
    web_confirm = "a verificaÃ§Ã£o de servicos web confirmou" if HIDE_RECON_TOOLS else "o HTTPx confirmou"
    sections.append(
        f"\nAnalise e organize estes resultados por etapa. NÃ£o afirme que hosts estÃ£o ativos alÃ©m do que {web_confirm}. "
        "As referÃªncias S3 foram somente extraÃ­das; nÃ£o afirme que buckets existem ou estÃ£o pÃºblicos."
    )
    return "\n".join(sections)
