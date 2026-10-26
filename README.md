# BlackHat (MingHat)

IA de **cibersegurança, pentest e programação sem filtro**, em português do Brasil, construída sobre um fork do [Open WebUI](https://github.com/open-webui/open-webui) com modelos locais via [Ollama](https://ollama.com) e um pipeline próprio de **recon** (reconhecimento de alvos autorizados).

> ⚠️ **Uso autorizado.** A BlackHat é voltada para testes de segurança em ambientes próprios, laboratórios, CTF e programas de bug bounty **com permissão**. Use com responsabilidade e dentro da lei.

---

## Índice

1. [O que é / arquitetura](#1-o-que-é--arquitetura)
2. [Requisitos](#2-requisitos)
3. [Instalação passo a passo](#3-instalação-passo-a-passo)
4. [Variáveis de ambiente](#4-variáveis-de-ambiente)
5. [Serviço systemd (rodar 24h)](#5-serviço-systemd-rodar-24h)
6. [Domínio e HTTPS (Cloudflare Tunnel)](#6-domínio-e-https-cloudflare-tunnel)
7. [E-mail transacional (Brevo/SMTP)](#7-e-mail-transacional-brevosmtp)
8. [Webhooks de pagamento (Cakto / Stripe)](#8-webhooks-de-pagamento-cakto--stripe)
9. [Painel admin](#9-painel-admin)
10. [Primeiro usuário admin](#10-primeiro-usuário-admin)
11. [Manutenção (rebuild / logs / restart)](#11-manutenção-rebuild--logs--restart)
12. [Segurança](#12-segurança)

---

## 1. O que é / arquitetura

- **Frontend + Backend:** fork do Open WebUI (SvelteKit compilado + FastAPI), empacotado em **uma única imagem Docker** (`blackhat:latest`).
- **Modelos de IA:** rodam no **Ollama no host** (CPU ou GPU). Dois modelos padrão:
  - `dolphin-llama3:latest` → exibido como **BlackHat** (8B, sem censura)
  - `huihui_ai/llama3.2-abliterate:3b` → exibido como **BlackHat Rápido** (3B, mais rápido)
- **Prompt do sistema:** injetado no servidor (`backend/open_webui/utils/middleware.py`) para TODOS os usuários — estilo hacker, sem recusa, com painel de "pensamento" (`<think>`) ao vivo.
- **Recon:** pipeline próprio (`backend/open_webui/utils/minghat_recon.py`) usando ferramentas externas (subfinder, dnsx, httpx, katana, gau) montadas em `/app/recon-tools`.
- **Pagamentos:** webhooks de **Cakto** e **Stripe** liberam o e-mail do comprador numa allowlist e disparam e-mail de boas-vindas.
- **Acesso externo:** via **Cloudflare Tunnel** (sem abrir portas no firewall).

```
Internet ──► Cloudflare Tunnel ──► 127.0.0.1:8080 (container blackhat)
                                         │
                                         ├─► Ollama (host:11434)  ← modelos
                                         ├─► /app/recon-tools      ← subfinder/dnsx/httpx/gau
                                         └─► volume blackhat-data  ← DB, chave, assinantes
```

---

## 2. Requisitos

| Item | Mínimo recomendado |
|---|---|
| **SO** | Ubuntu 22.04/24.04 (ou similar) |
| **RAM** | **16 GB+** (8 GB roda apertado; o build do frontend consome bastante) |
| **CPU** | 4+ vCPUs (modelos rodam em CPU por padrão) |
| **Disco** | 30 GB+ livres (imagem ~7 GB + modelos Q4) |
| **Docker** | Engine 24+ |
| **Ollama** | instalado no host |
| **Node** | só para desenvolvimento local (o build acontece dentro do Docker) |

> 💡 Em VPS de 8–11 GB, pare o Ollama antes de buildar (`ollama stop <modelo>`) para liberar RAM e evitar OOM.

---

## 3. Instalação passo a passo

### 3.1. Clonar o repositório

```bash
git clone https://github.com/Charyflux/minghat.git
cd minghat
```

### 3.2. Instalar Docker

```bash
curl -fsSL https://get.docker.com | sh
sudo systemctl enable --now docker
```

### 3.3. Instalar Ollama e baixar os modelos

```bash
curl -fsSL https://ollama.com/install.sh | sh

# Modelos padrão da BlackHat:
ollama pull dolphin-llama3:latest
ollama pull huihui_ai/llama3.2-abliterate:3b
```

Ajuste do Ollama (opcional, recomendado em RAM limitada) — em `/etc/systemd/system/ollama.service.d/override.conf`:

```ini
[Service]
Environment="OLLAMA_MAX_LOADED_MODELS=1"
Environment="OLLAMA_NUM_PARALLEL=1"
Environment="OLLAMA_KEEP_ALIVE=30m"
```

```bash
sudo systemctl daemon-reload && sudo systemctl restart ollama
```

### 3.4. Instalar as ferramentas de recon

Baixe os binários do [ProjectDiscovery](https://github.com/projectdiscovery) e o [gau](https://github.com/lc/gau), e coloque-os numa pasta no host (ex.: `/opt/blackhat-recon-tools`):

```bash
sudo mkdir -p /opt/blackhat-recon-tools
# Exemplo (ajuste as versões/arquitetura):
#   subfinder, dnsx, httpx, katana  → github.com/projectdiscovery/*/releases
#   gau                             → github.com/lc/gau/releases
# Descompacte cada binário dentro de /opt/blackhat-recon-tools e dê permissão:
sudo chmod +x /opt/blackhat-recon-tools/*
```

Essa pasta é montada no container como `/app/recon-tools` (read-only).

### 3.5. Buildar a imagem

```bash
# (em RAM limitada, libere o Ollama antes)
ollama stop dolphin-llama3:latest 2>/dev/null
ollama stop huihui_ai/llama3.2-abliterate:3b 2>/dev/null

docker build -t blackhat:latest .
```

### 3.6. Criar o arquivo de segredos

Os segredos **nunca** ficam no repositório. Crie `/etc/blackhat-smtp.env` (permissão 600):

```bash
sudo sh -c 'umask 077; cat > /etc/blackhat-smtp.env' <<'EOF'
MINGHAT_SMTP_PASSWORD=coloque_a_senha_do_smtp_aqui
CAKTO_WEBHOOK_SECRET=coloque_o_secret_da_cakto
STRIPE_WEBHOOK_SECRET=coloque_o_whsec_da_stripe
EOF
```

### 3.7. Subir o container (teste rápido)

```bash
docker run --rm --name blackhat \
  --add-host=host.docker.internal:host-gateway \
  -p 127.0.0.1:8080:8080 \
  --env-file /etc/blackhat-smtp.env \
  -e OLLAMA_BASE_URL=http://host.docker.internal:11434 \
  -e WEBUI_NAME=BlackHat \
  -e DEFAULT_MODELS=dolphin-llama3:latest \
  -e BYPASS_MODEL_ACCESS_CONTROL=true \
  -v blackhat-data:/app/backend/data \
  -v /opt/blackhat-recon-tools:/app/recon-tools:ro \
  blackhat:latest
```

Acesse `http://127.0.0.1:8080`. Funcionou? Pare (Ctrl+C) e configure o serviço systemd (passo 5) para rodar 24h.

---

## 4. Variáveis de ambiente

| Variável | Valor | Para quê |
|---|---|---|
| `WEBUI_NAME` | `BlackHat` | Nome exibido na interface |
| `OLLAMA_BASE_URL` | `http://host.docker.internal:11434` | Onde o Ollama responde |
| `DEFAULT_MODELS` | `dolphin-llama3:latest` | Modelo padrão |
| `DEFAULT_LOCALE` | `pt-BR` | Idioma padrão |
| `WEBUI_AUTH` | `True` | Exige login |
| `ENABLE_SIGNUP` | `True` | Permite cadastro (gated pela allowlist de assinantes) |
| `BYPASS_MODEL_ACCESS_CONTROL` | `true` | Todos os usuários veem os modelos |
| `WEBUI_SECRET_KEY_FILE` | `/app/backend/data/.webui_secret_key` | Chave JWT (gerada no 1º boot) |
| `MINGHAT_RECON_TOOLS_DIR` | `/app/recon-tools` | Pasta das ferramentas de recon |
| `SUBFINDER_PATH` / `DNSX_PATH` / `HTTPX_PATH` / `KATANA_PATH` / `GAU_PATH` | `/app/recon-tools/<bin>` | Caminho de cada binário |
| `MINGHAT_SMTP_HOST` | `smtp-relay.brevo.com` | Servidor SMTP |
| `MINGHAT_SMTP_PORT` | `587` | Porta SMTP |
| `MINGHAT_SMTP_USER` | `<usuario-brevo>` | Usuário SMTP |
| `MINGHAT_SMTP_FROM` | `noreply@seudominio` | Remetente |
| `MINGHAT_SMTP_PASSWORD` | *(no arquivo de segredos)* | Senha SMTP |
| `MINGHAT_SIGNUP_URL` | `https://seudominio/auth?mode=signup` | Link do e-mail de boas-vindas |
| `CAKTO_WEBHOOK_SECRET` | *(no arquivo de segredos)* | Valida webhook da Cakto |
| `STRIPE_WEBHOOK_SECRET` | *(no arquivo de segredos)* | Valida webhook da Stripe (`whsec_...`) |

> Os caminhos internos e os IDs dos modelos são configuráveis; os nomes exibidos (BlackHat / BlackHat Rápido) ficam em `scripts/configure-minghat-models.py`.

---

## 5. Serviço systemd (rodar 24h)

Crie `/etc/systemd/system/blackhat.service`:

```ini
[Unit]
Description=BlackHat (Open WebUI container)
After=docker.service ollama.service network-online.target
Requires=docker.service
Wants=ollama.service

[Service]
Restart=always
RestartSec=5
EnvironmentFile=-/etc/blackhat-smtp.env
ExecStartPre=-/usr/bin/docker stop blackhat
ExecStartPre=-/usr/bin/docker rm blackhat
ExecStart=/usr/bin/docker run --rm --name blackhat \
  --add-host=host.docker.internal:host-gateway \
  -p 127.0.0.1:8080:8080 \
  -e OLLAMA_BASE_URL=http://host.docker.internal:11434 \
  -e WEBUI_NAME=BlackHat \
  -e DEFAULT_MODELS=dolphin-llama3:latest \
  -e DEFAULT_LOCALE=pt-BR \
  -e WEBUI_AUTH=True -e ENABLE_SIGNUP=True \
  -e BYPASS_MODEL_ACCESS_CONTROL=true \
  -e WEBUI_SECRET_KEY_FILE=/app/backend/data/.webui_secret_key \
  -e MINGHAT_RECON_TOOLS_DIR=/app/recon-tools \
  -e SUBFINDER_PATH=/app/recon-tools/subfinder \
  -e DNSX_PATH=/app/recon-tools/dnsx \
  -e HTTPX_PATH=/app/recon-tools/httpx \
  -e KATANA_PATH=/app/recon-tools/katana \
  -e GAU_PATH=/app/recon-tools/gau \
  -e MINGHAT_SIGNUP_URL=https://seudominio/auth?mode=signup \
  -e MINGHAT_SMTP_HOST=smtp-relay.brevo.com \
  -e MINGHAT_SMTP_PORT=587 \
  -e MINGHAT_SMTP_USER=seu_usuario_brevo \
  -e MINGHAT_SMTP_FROM=noreply@seudominio \
  -e MINGHAT_SMTP_USE_TLS=true \
  -e MINGHAT_SMTP_PASSWORD \
  -e CAKTO_WEBHOOK_SECRET \
  -e STRIPE_WEBHOOK_SECRET \
  -v blackhat-data:/app/backend/data \
  -v /opt/blackhat-recon-tools:/app/recon-tools:ro \
  blackhat:latest

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now blackhat
sudo systemctl status blackhat
```

---

## 6. Domínio e HTTPS (Cloudflare Tunnel)

```bash
# Instala o cloudflared
curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 \
  -o /usr/local/bin/cloudflared && chmod +x /usr/local/bin/cloudflared

cloudflared tunnel login
cloudflared tunnel create blackhat
cloudflared tunnel route dns blackhat seudominio.com
```

`/etc/cloudflared/config.yml`:

```yaml
tunnel: <ID-DO-TUNEL>
credentials-file: /root/.cloudflared/<ID-DO-TUNEL>.json
ingress:
  - hostname: seudominio.com
    service: http://127.0.0.1:8080
  - service: http_status:404
```

```bash
cloudflared service install
sudo systemctl enable --now cloudflared
```

---

## 7. E-mail transacional (Brevo/SMTP)

1. Crie conta no [Brevo](https://www.brevo.com) → **SMTP & API** → pegue o usuário e a senha SMTP.
2. **Autorize o IP do VPS** em Brevo (senão dá erro `525 Unauthorized IP`).
3. Preencha `MINGHAT_SMTP_*` (senha no `/etc/blackhat-smtp.env`).
4. Verifique o domínio remetente (SPF/DKIM) para não cair em spam.

O e-mail de boas-vindas é enviado em `backend/open_webui/utils/minghat_mail.py`.

---

## 8. Webhooks de pagamento (Cakto / Stripe)

Os dois compartilham a mesma allowlist (`backend/data/minghat_subscribers.json`), que libera o cadastro do comprador.

### Cakto
- Endpoint: `https://seudominio/api/minghat/cakto/webhook`
- Secret em `CAKTO_WEBHOOK_SECRET`.

### Stripe
- Crie um **Payment Link** do seu produto.
- Webhook: `https://seudominio/api/minghat/stripe/webhook`
- Eventos: `checkout.session.completed`, `invoice.paid`, `invoice.payment_failed`, `customer.subscription.deleted`.
- Copie o **Signing secret** (`whsec_...`) para `STRIPE_WEBHOOK_SECRET` e reinicie o serviço.
- A verificação da assinatura é feita na mão (HMAC-SHA256) em `backend/open_webui/routers/minghat_stripe.py` — sem dependência da lib `stripe`.

> As rotas internas usam o prefixo `/api/minghat/...` por compatibilidade. **Não renomeie** para não quebrar os webhooks já configurados.

---

## 9. Painel admin

Dashboard separado (lista de usuários, assinantes, reset de senha, bloqueio), disponível em `minghat-admin/`. Rode em `127.0.0.1` (privado), atrás de Basic Auth:

```bash
cd minghat-admin
docker build -t blackhat-admin:latest .
docker run -d --name blackhat-admin --restart always \
  -p 127.0.0.1:8890:8888 \
  -e ADMIN_DASH_USER=seu_usuario \
  -e ADMIN_DASH_PASSWORD=sua_senha_forte \
  -v blackhat-data:/data:ro \
  blackhat-admin:latest
```

Acesse via túnel SSH: `ssh -L 8890:127.0.0.1:8890 root@SEU_VPS` e abra `http://localhost:8890`.

---

## 10. Primeiro usuário admin

O **primeiro usuário que se cadastrar** vira admin automaticamente. Acesse `https://seudominio/auth?mode=signup` e crie sua conta.

Para redefinir a senha do admin depois, use o painel admin (passo 9) ou o script em `scripts/`.

---

## 11. Manutenção (rebuild / logs / restart)

```bash
# Rebuild após mudanças no código (libere RAM antes se necessário)
cd /caminho/para/minghat
docker build -t blackhat:latest .
sudo systemctl restart blackhat

# Logs
docker logs -f blackhat

# Status de saúde
docker inspect -f '{{.State.Health.Status}}' blackhat

# Liberar RAM do Ollama
ollama stop dolphin-llama3:latest
```

---

## 12. Segurança

- **Nunca** commite segredos. Eles ficam em `/etc/blackhat-smtp.env` e no volume `blackhat-data` (ambos fora do repo — veja o `.gitignore`).
- Container exposto só em `127.0.0.1`; o acesso externo passa pelo Cloudflare Tunnel.
- Painel admin **privado** (127.0.0.1 + Basic Auth + túnel SSH).
- Mantenha SSH com chave (desative senha), `fail2ban` ativo e o firewall fechado.
- Dados de clientes (e-mails/telefones) vivem só no volume `blackhat-data`, nunca no Git.

---

## Créditos

Construído sobre o [Open WebUI](https://github.com/open-webui/open-webui) (licença BSD-3). Ferramentas de recon: [ProjectDiscovery](https://github.com/projectdiscovery) e [gau](https://github.com/lc/gau).
