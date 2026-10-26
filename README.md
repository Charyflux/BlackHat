<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=12,20,24&height=210&section=header&text=BlackHat&fontSize=72&fontColor=c29aff&animation=fadeIn&fontAlignY=36&desc=IA%20de%20Pentest%2C%20Hacking%20e%20Programacao%20SEM%20FILTRO&descAlignY=56&descSize=18" alt="BlackHat" />

<img src="https://readme-typing-svg.demolab.com?font=Fira+Code&weight=600&size=22&duration=3000&pause=800&color=C29AFF&center=true&vCenter=true&width=640&lines=IA+sem+censura%2C+em+portugu%C3%AAs+do+Brasil;Pentest+%2B+Recon+automatizado;Programa%C3%A7%C3%A3o+n%C3%ADvel+s%C3%AAnior;Roda+no+SEU+servidor%2C+sem+API+externa" alt="typing" />

<br/>

![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Ollama](https://img.shields.io/badge/Ollama-000000?style=for-the-badge&logo=ollama&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)
![SvelteKit](https://img.shields.io/badge/SvelteKit-FF3E00?style=for-the-badge&logo=svelte&logoColor=white)
![Linux](https://img.shields.io/badge/Linux-FCC624?style=for-the-badge&logo=linux&logoColor=black)

![Status](https://img.shields.io/badge/status-produção-brightgreen?style=flat-square)
![Licença](https://img.shields.io/badge/base-Open%20WebUI%20(BSD--3)-blue?style=flat-square)
![PT-BR](https://img.shields.io/badge/idioma-PT--BR-9b59b6?style=flat-square)

</div>

---

> ### ⚠️ Aviso de uso responsável
> A **BlackHat** é voltada a testes de segurança em ambientes **autorizados**: seus próprios sistemas, laboratórios, CTFs e programas de **bug bounty com permissão**. Você é o único responsável pelo uso. **Não use contra alvos sem autorização.**

---

## 📑 Índice

- [🎯 O que é](#-o-que-é)
- [🧩 Como funciona (arquitetura)](#-como-funciona-arquitetura)
- [💻 Requisitos de hardware (potência)](#-requisitos-de-hardware-potência)
- [🖥️ Sistemas operacionais suportados](#️-sistemas-operacionais-suportados)
- [📦 O que você precisa instalar (pré-requisitos)](#-o-que-você-precisa-instalar-pré-requisitos)
- [🚀 Instalação passo a passo](#-instalação-passo-a-passo)
  - [Passo 1 — Preparar o servidor](#passo-1--preparar-o-servidor)
  - [Passo 2 — Instalar o Docker](#passo-2--instalar-o-docker)
  - [Passo 3 — Instalar o Ollama + baixar os modelos](#passo-3--instalar-o-ollama--baixar-os-modelos)
  - [Passo 4 — Baixar o código da BlackHat](#passo-4--baixar-o-código-da-blackhat)
  - [Passo 5 — Instalar as ferramentas de recon](#passo-5--instalar-as-ferramentas-de-recon)
  - [Passo 6 — Buildar a imagem Docker](#passo-6--buildar-a-imagem-docker)
  - [Passo 7 — Criar o arquivo de segredos](#passo-7--criar-o-arquivo-de-segredos)
  - [Passo 8 — Subir e testar](#passo-8--subir-e-testar)
  - [Passo 9 — Rodar 24h (systemd)](#passo-9--rodar-24h-systemd)
  - [Passo 10 — Criar o admin e usar](#passo-10--criar-o-admin-e-usar)
- [🌐 Deixar online com domínio e HTTPS](#-deixar-online-com-domínio-e-https)
- [📧 E-mail transacional (opcional)](#-e-mail-transacional-opcional)
- [💳 Webhooks de pagamento (opcional)](#-webhooks-de-pagamento-opcional)
- [🛠️ Manutenção do dia a dia](#️-manutenção-do-dia-a-dia)
- [🩺 Solução de problemas](#-solução-de-problemas)
- [🔐 Segurança](#-segurança)
- [📂 Estrutura do projeto](#-estrutura-do-projeto)
- [❓ FAQ](#-faq)

---

## 🎯 O que é

A **BlackHat** é uma IA de **cibersegurança, pentest e programação sem censura**, em português do Brasil, que roda **no seu próprio servidor** — sem depender de ChatGPT, Gemini ou qualquer API externa. É um fork do [Open WebUI](https://github.com/open-webui/open-webui) com personalizações próprias.

| Recurso | Descrição |
|---|---|
| 🔓 **Sem filtro** | Responde direto, sem recusas nem sermão. Entrega código, comandos e payloads completos. |
| 🕵️ **Modo Recon** | Pipeline próprio de reconhecimento (subdomínios, DNS, serviços web, crawl de URLs). |
| 🧠 **Pensamento ao vivo** | Mostra o raciocínio sendo construído antes da resposta (painel `<think>`). |
| 💻 **Código nível sênior** | Programação, debugging e arquitetura em qualquer linguagem. |
| 🇧🇷 **Português impecável** | Treinada para gramática e clareza. |
| 🏠 **100% no seu servidor** | Modelos locais via Ollama. Seus dados não saem da sua máquina. |

---

## 🧩 Como funciona (arquitetura)

```
                    ┌─────────────────────────────┐
  Internet ──HTTPS──►  Cloudflare Tunnel (opcional) │
                    └──────────────┬──────────────┘
                                   │ 127.0.0.1:8080
                    ┌──────────────▼──────────────┐
                    │   Container Docker  (blackhat)│
                    │   Open WebUI (Svelte + API)   │
                    └───┬───────────────┬──────────┘
                        │               │
            host:11434  │               │  /app/recon-tools
                    ┌───▼────┐     ┌─────▼─────────────────┐
                    │ Ollama │     │ subfinder / dnsx /     │
                    │ modelos│     │ httpx / katana / gau   │
                    └────────┘     └────────────────────────┘
                        │
                 volume "blackhat-data"  (DB, chave, assinantes)
```

- **Frontend + Backend:** empacotados em **uma única imagem Docker** (`blackhat:latest`).
- **Modelos de IA:** rodam no **Ollama no host** (CPU ou GPU).
- **Recon:** binários externos montados em `/app/recon-tools`.
- **Dados:** ficam num **volume Docker** (`blackhat-data`), nunca dentro do código.

---

## 💻 Requisitos de hardware (potência)

Os modelos de IA rodam **localmente** — então a RAM/CPU definem a velocidade. Abaixo o que você precisa:

| Componente | 🟡 Mínimo (funciona, mais lento) | 🟢 Recomendado | 🔵 Ideal (rápido) |
|---|---|---|---|
| **CPU** | 4 vCPUs | 8 vCPUs | 8+ vCPUs ou GPU NVIDIA |
| **RAM** | 8 GB | **16 GB** | 32 GB |
| **Disco (SSD)** | 30 GB livres | 50 GB | 80 GB+ |
| **GPU** | não precisa (roda em CPU) | opcional | NVIDIA 8 GB+ VRAM (CUDA) |
| **Internet** | 10 Mbps (só pra baixar) | 100 Mbps | — |

### Quanto cada coisa ocupa
| Item | Tamanho aproximado |
|---|---|
| Imagem Docker `blackhat` | ~7 GB |
| Modelo `dolphin-llama3` (8B, Q4) | ~4,7 GB |
| Modelo `llama3.2-abliterate` (3B, Q4) | ~2 GB |
| Ferramentas de recon | ~200 MB |

> 💡 **Importante sobre RAM:** o modelo 8B consome ~6 GB de RAM carregado. Em servidores de 8 GB, **pare o Ollama antes de buildar a imagem** (o build do frontend também come RAM) para não dar *Out Of Memory*. Com 16 GB você roda tudo tranquilo.
>
> ⚡ **GPU acelera muito:** se tiver uma NVIDIA, as respostas ficam vários segundos mais rápidas. Sem GPU funciona bem em CPU, só mais devagar.

---

## 🖥️ Sistemas operacionais suportados

| SO | Suporte | Observação |
|---|---|---|
| 🐧 **Ubuntu 22.04 / 24.04 LTS** | ✅ **Recomendado** | Melhor compatibilidade, é o usado em produção. |
| 🐧 **Debian 12** | ✅ Total | Funciona igual ao Ubuntu. |
| 🐧 Outras distros Linux (com Docker + systemd) | ✅ | Fedora, Rocky, Alma, etc. |
| 🪟 **Windows 10/11** | ⚠️ Via WSL2 + Docker Desktop | Bom para testar; produção use Linux. |
| 🍎 **macOS** (Intel/Apple Silicon) | ⚠️ Docker Desktop + Ollama nativo | Para desenvolvimento/testes. |

> Para **produção** (vender/disponibilizar 24h), use um **VPS Linux** (Ubuntu). Provedores comuns: Contabo, Hetzner, DigitalOcean, Vultr, AWS.

---

## 📦 O que você precisa instalar (pré-requisitos)

Antes de começar, estes são os programas que o passo a passo vai instalar:

| Programa | Para quê | Instalado no passo |
|---|---|---|
| **Git** | Baixar o código do GitHub | Passo 1 |
| **Docker** | Rodar a aplicação em container | Passo 2 |
| **Ollama** | Rodar os modelos de IA localmente | Passo 3 |
| **Modelos** (dolphin-llama3, llama3.2-abliterate) | O "cérebro" da IA | Passo 3 |
| **Ferramentas de recon** (subfinder, dnsx, httpx, katana, gau) | Reconhecimento de alvos | Passo 5 |

Tudo é gratuito e open-source. Não precisa de chave de API de ninguém.

---

## 🚀 Instalação passo a passo

> 📋 Os comandos abaixo são para **Ubuntu/Debian**. Rode como `root` ou com `sudo`.

### Passo 1 — Preparar o servidor

Atualize o sistema e instale utilitários básicos (incluindo o Git):

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y git curl wget unzip
```

Confirme que o Git foi instalado:

```bash
git --version
# deve aparecer algo como: git version 2.43.0
```

---

### Passo 2 — Instalar o Docker

O Docker roda a aplicação em um "container" isolado. Instalação oficial:

```bash
curl -fsSL https://get.docker.com | sh
sudo systemctl enable --now docker
```

Teste:

```bash
sudo docker run --rm hello-world
# se aparecer "Hello from Docker!" está funcionando
```

<details>
<summary>🔧 (Opcional) Rodar docker sem sudo</summary>

```bash
sudo usermod -aG docker $USER
# saia e entre de novo na sessão (logout/login) para valer
```
</details>

---

### Passo 3 — Instalar o Ollama + baixar os modelos

O **Ollama** é quem roda os modelos de IA. Instalação oficial:

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

Baixe os **dois modelos** da BlackHat (vão ~7 GB no total):

```bash
# Modelo principal — "BlackHat" (8B, sem censura)
ollama pull dolphin-llama3:latest

# Modelo rápido — "BlackHat Rápido" (3B)
ollama pull huihui_ai/llama3.2-abliterate:3b
```

Confira que baixaram:

```bash
ollama list
# devem aparecer os dois modelos na lista
```

<details>
<summary>⚙️ (Recomendado) Ajustar o Ollama para RAM limitada</summary>

Crie `/etc/systemd/system/ollama.service.d/override.conf`:

```ini
[Service]
Environment="OLLAMA_MAX_LOADED_MODELS=1"
Environment="OLLAMA_NUM_PARALLEL=1"
Environment="OLLAMA_KEEP_ALIVE=30m"
```

Aplique:

```bash
sudo systemctl daemon-reload && sudo systemctl restart ollama
```

Isso mantém só 1 modelo na RAM por vez, evitando estouro de memória.
</details>

---

### Passo 4 — Baixar o código da BlackHat

```bash
cd /root
git clone https://github.com/Charyflux/minghat.git
cd minghat
```

> Se o repositório estiver **privado**, o `git clone` vai pedir login no GitHub.

---

### Passo 5 — Instalar as ferramentas de recon

O modo Recon usa 5 ferramentas. Baixe os binários e coloque numa pasta no host:

```bash
sudo mkdir -p /opt/blackhat-recon-tools
cd /opt/blackhat-recon-tools
```

Baixe cada uma (ajuste a versão/arquitetura conforme o site de releases):

- **subfinder**, **dnsx**, **httpx**, **katana** → [github.com/projectdiscovery](https://github.com/projectdiscovery) (cada um tem releases)
- **gau** → [github.com/lc/gau/releases](https://github.com/lc/gau/releases)

Exemplo para `subfinder` (repita para os outros, trocando o nome/URL):

```bash
wget https://github.com/projectdiscovery/subfinder/releases/latest/download/subfinder_linux_amd64.zip
unzip subfinder_linux_amd64.zip && rm subfinder_linux_amd64.zip
```

No fim, dê permissão de execução a todos:

```bash
sudo chmod +x /opt/blackhat-recon-tools/*
ls -la /opt/blackhat-recon-tools
# devem aparecer: subfinder  dnsx  httpx  katana  gau
```

---

### Passo 6 — Buildar a imagem Docker

Isso compila o frontend e monta a imagem (`blackhat:latest`). **Pode demorar alguns minutos.**

```bash
cd /root/minghat

# Em servidores com pouca RAM, libere memória antes:
ollama stop dolphin-llama3:latest 2>/dev/null
ollama stop huihui_ai/llama3.2-abliterate:3b 2>/dev/null

# Buildar
docker build -t blackhat:latest .
```

Ao terminar, confira:

```bash
docker images blackhat:latest
# deve listar a imagem (~7 GB)
```

---

### Passo 7 — Criar o arquivo de segredos

Os segredos **nunca** ficam no código. Crie `/etc/blackhat-smtp.env` (permissão restrita):

```bash
sudo sh -c 'umask 077; cat > /etc/blackhat-smtp.env' <<'EOF'
# Preencha só o que for usar. Pode deixar em branco para começar.
MINGHAT_SMTP_PASSWORD=
CAKTO_WEBHOOK_SECRET=
STRIPE_WEBHOOK_SECRET=
EOF
```

> Para só **testar a IA**, pode deixar tudo em branco. E-mail e pagamentos são opcionais (passos mais abaixo).

---

### Passo 8 — Subir e testar

Rode o container (teste rápido, em primeiro plano):

```bash
docker run --rm --name blackhat \
  --add-host=host.docker.internal:host-gateway \
  -p 127.0.0.1:8080:8080 \
  --env-file /etc/blackhat-smtp.env \
  -e OLLAMA_BASE_URL=http://host.docker.internal:11434 \
  -e WEBUI_NAME=BlackHat \
  -e DEFAULT_MODELS=dolphin-llama3:latest \
  -e DEFAULT_LOCALE=pt-BR \
  -e WEBUI_AUTH=True \
  -e ENABLE_SIGNUP=True \
  -e BYPASS_MODEL_ACCESS_CONTROL=true \
  -e MINGHAT_RECON_TOOLS_DIR=/app/recon-tools \
  -e SUBFINDER_PATH=/app/recon-tools/subfinder \
  -e DNSX_PATH=/app/recon-tools/dnsx \
  -e HTTPX_PATH=/app/recon-tools/httpx \
  -e KATANA_PATH=/app/recon-tools/katana \
  -e GAU_PATH=/app/recon-tools/gau \
  -v blackhat-data:/app/backend/data \
  -v /opt/blackhat-recon-tools:/app/recon-tools:ro \
  blackhat:latest
```

Abra no navegador: **http://127.0.0.1:8080**
(se for VPS remoto, use túnel SSH: `ssh -L 8080:127.0.0.1:8080 root@SEU_IP` e abra `http://localhost:8080`)

Funcionou? Pressione **Ctrl+C** para parar e vá para o Passo 9 (rodar 24h).

---

### Passo 9 — Rodar 24h (systemd)

Para a BlackHat ficar sempre no ar (e reiniciar sozinha), crie o serviço.

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
  -e MINGHAT_RECON_TOOLS_DIR=/app/recon-tools \
  -e SUBFINDER_PATH=/app/recon-tools/subfinder \
  -e DNSX_PATH=/app/recon-tools/dnsx \
  -e HTTPX_PATH=/app/recon-tools/httpx \
  -e KATANA_PATH=/app/recon-tools/katana \
  -e GAU_PATH=/app/recon-tools/gau \
  -e MINGHAT_SMTP_PASSWORD \
  -e CAKTO_WEBHOOK_SECRET \
  -e STRIPE_WEBHOOK_SECRET \
  -v blackhat-data:/app/backend/data \
  -v /opt/blackhat-recon-tools:/app/recon-tools:ro \
  blackhat:latest

[Install]
WantedBy=multi-user.target
```

Ative:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now blackhat
sudo systemctl status blackhat     # deve aparecer "active (running)"
```

---

### Passo 10 — Criar o admin e usar

1. Abra a BlackHat no navegador.
2. Clique em **Inscrever-se** e crie sua conta.
3. **O primeiro usuário vira ADMIN automaticamente.** 🎉
4. Escolha o modelo **BlackHat** (ou **BlackHat Rápido**) e comece a usar.

Pronto — a IA está rodando no seu servidor!

---

## 🌐 Deixar online com domínio e HTTPS

Para acessar por um domínio (ex.: `seudominio.com`) com HTTPS, sem abrir portas no firewall, use o **Cloudflare Tunnel**:

```bash
# Instalar cloudflared
curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 \
  -o /usr/local/bin/cloudflared && chmod +x /usr/local/bin/cloudflared

# Autenticar e criar o túnel
cloudflared tunnel login
cloudflared tunnel create blackhat
cloudflared tunnel route dns blackhat seudominio.com
```

Crie `/etc/cloudflared/config.yml`:

```yaml
tunnel: <ID-DO-TUNEL>
credentials-file: /root/.cloudflared/<ID-DO-TUNEL>.json
ingress:
  - hostname: seudominio.com
    service: http://127.0.0.1:8080
  - service: http_status:404
```

Instale como serviço:

```bash
cloudflared service install
sudo systemctl enable --now cloudflared
```

Acesse `https://seudominio.com` 🎉

---

## 📧 E-mail transacional (opcional)

Para enviar e-mail de boas-vindas (ex.: após uma venda), configure um SMTP (ex.: [Brevo](https://www.brevo.com), grátis até 300 e-mails/dia):

1. Crie a conta no Brevo → **SMTP & API** → pegue usuário e senha SMTP.
2. **Autorize o IP do seu servidor** no Brevo (senão dá erro `525`).
3. Adicione ao serviço (passo 9) as variáveis `MINGHAT_SMTP_HOST`, `MINGHAT_SMTP_PORT`, `MINGHAT_SMTP_USER`, `MINGHAT_SMTP_FROM` e coloque a senha em `/etc/blackhat-smtp.env`.

---

## 💳 Webhooks de pagamento (opcional)

Se for **vender assinaturas**, a BlackHat libera automaticamente o acesso do comprador via webhook (Cakto e Stripe suportados).

<details>
<summary>Ver configuração de Cakto e Stripe</summary>

**Cakto** → endpoint `https://seudominio/api/minghat/cakto/webhook`, secret em `CAKTO_WEBHOOK_SECRET`.

**Stripe** → crie um Payment Link, webhook `https://seudominio/api/minghat/stripe/webhook`, eventos `checkout.session.completed`, `invoice.paid`, `invoice.payment_failed`, `customer.subscription.deleted`. Copie o `whsec_...` para `STRIPE_WEBHOOK_SECRET`.

Os dois compartilham a mesma allowlist, que gate o cadastro do comprador. **Não renomeie** as rotas `/api/minghat/...` para não quebrar os webhooks.
</details>

---

## 🛠️ Manutenção do dia a dia

```bash
# Ver logs em tempo real
docker logs -f blackhat

# Ver se está saudável
docker inspect -f '{{.State.Health.Status}}' blackhat

# Reiniciar
sudo systemctl restart blackhat

# Atualizar após mudar o código
cd /root/minghat && git pull
docker build -t blackhat:latest .
sudo systemctl restart blackhat

# Liberar RAM do Ollama
ollama stop dolphin-llama3:latest
```

---

## 🩺 Solução de problemas

<details>
<summary>❌ O build falha / trava (Out Of Memory)</summary>

Falta de RAM durante o `docker build`. Pare os modelos antes:
```bash
ollama stop dolphin-llama3:latest
ollama stop huihui_ai/llama3.2-abliterate:3b
docker build -t blackhat:latest .
```
Se persistir, aumente a RAM do servidor ou crie swap.
</details>

<details>
<summary>❌ A IA não responde / fica "pensando"</summary>

- Confira se o Ollama está rodando: `ollama ps`
- Confira se os modelos foram baixados: `ollama list`
- Veja os logs: `docker logs -f blackhat`
- O primeiro carregamento do modelo demora (ele é carregado na RAM).
</details>

<details>
<summary>❌ Não aparece nenhum modelo para o usuário</summary>

Certifique-se de que `BYPASS_MODEL_ACCESS_CONTROL=true` está no serviço (passo 9) e reinicie.
</details>

<details>
<summary>❌ Recon não retorna nada</summary>

Verifique se os binários existem e têm permissão em `/opt/blackhat-recon-tools` e se os caminhos (`SUBFINDER_PATH`, etc.) estão corretos no serviço.
</details>

---

## 🔐 Segurança

- **Nunca** coloque segredos no Git. Eles ficam em `/etc/blackhat-smtp.env` e no volume `blackhat-data` (ambos fora do repositório — veja o `.gitignore`).
- O container é exposto só em `127.0.0.1`; o acesso externo passa pelo Cloudflare Tunnel.
- Use **SSH com chave** (desative login por senha) e mantenha o firewall fechado.
- Instale **fail2ban** para barrar ataques de força bruta.
- Dados de clientes (e-mails/telefones) vivem só no volume `blackhat-data`, **nunca no Git**.

---

## 📂 Estrutura do projeto

```
minghat/
├── backend/open_webui/        # Backend FastAPI
│   ├── utils/middleware.py     # Prompt do sistema + injeções da BlackHat
│   ├── utils/minghat_recon.py  # Pipeline de recon
│   ├── utils/minghat_mail.py   # E-mail de boas-vindas
│   └── routers/                # Webhooks Cakto / Stripe
├── src/                        # Frontend SvelteKit
│   └── lib/components/          # UI (paywall, vitrine, sidebar...)
├── scripts/                    # Scripts de configuração/boot
├── Dockerfile                  # Build da imagem
└── README.md                   # Este arquivo
```

---

## ❓ FAQ

<details>
<summary>Preciso de GPU?</summary>
Não. Roda em CPU. GPU (NVIDIA) só deixa as respostas mais rápidas.
</details>

<details>
<summary>Preciso pagar API da OpenAI/Google?</summary>
Não. Os modelos rodam localmente via Ollama. Zero custo de API.
</details>

<details>
<summary>Funciona no Windows?</summary>
Para testar, sim (WSL2 + Docker Desktop). Para produção 24h, use um VPS Linux.
</details>

<details>
<summary>Quanto de RAM eu realmente preciso?</summary>
8 GB funciona (mais lento). 16 GB é o recomendado para rodar confortável.
</details>

---

<div align="center">

**Construído sobre o [Open WebUI](https://github.com/open-webui/open-webui) (BSD-3)** · Recon por [ProjectDiscovery](https://github.com/projectdiscovery) e [gau](https://github.com/lc/gau)

<img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=12,20,24&height=100&section=footer" alt="footer" />

</div>
