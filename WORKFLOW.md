# Fluxo de ambientes da MingHat (dev -> staging -> produção)

Três cópias independentes do projeto, cada uma em seu próprio diretório
(git worktree) e branch, rodando ao mesmo tempo em portas diferentes.
Elas compartilham o mesmo Ollama (`127.0.0.1:11434`) e o mesmo interpretador
Python (`.venv`), mas cada uma tem seu **próprio banco de dados** (`DATA_DIR`)
e seu **próprio processo** de frontend/backend — mudar uma não afeta as outras.

| Ambiente   | Branch    | Diretório        | Frontend | Backend | Acesso público                                  |
|------------|-----------|-------------------|----------|---------|--------------------------------------------------|
| Dev        | `dev`     | `D:\IA-dev`       | 8801     | 8070    | nenhum (só `localhost:8801`)                     |
| Staging    | `staging` | `D:\IA-staging`   | 8821     | 8090    | `https://teste.minghat.com.br` (Basic Auth)      |
| Produção   | `main`    | `D:\IA`           | 8811     | 8080    | `https://minghat.com.br`                         |

Os branches são **locais** (não existe remote próprio configurado — `origin`
aqui é o repositório público do open-webui/open-webui, não seu fork; nada é
enviado (`git push`) para lá).

## O ciclo de trabalho

1. **Desenvolvimento** — toda mudança pedida no chat é feita em `D:\IA-dev`
   (branch `dev`). Suba com:
   ```
   powershell -File D:\IA-dev\scripts\start-dev.ps1
   ```
   Acesse `http://localhost:8801` para conferir antes de qualquer coisa ir
   pro ar. Nada aqui é visível publicamente.

2. **Promover para staging** — quando a mudança parecer pronta, mescla
   `dev` dentro de `staging`:
   ```
   powershell -File D:\IA\scripts\promote.ps1 -From dev -To staging
   powershell -File D:\IA-staging\scripts\start-staging.ps1
   ```
   Teste em `https://teste.minghat.com.br` (usuário/senha do Basic Auth
   ficam em `D:\IA-staging\.runtime\staging-auth-password.txt`). É o mesmo
   comportamento de produção, com um banco de dados totalmente separado
   (assinantes de teste não aparecem na lista real da Kiwify).

3. **Promover para produção** — só depois de validar no staging:
   ```
   powershell -File D:\IA\scripts\promote.ps1 -From staging -To main
   powershell -File D:\IA\scripts\start-local.ps1
   ```
   Isso atualiza o `D:\IA` (o que está de fato publicado em
   `minghat.com.br`). Se o backend/frontend de produção já estiverem
   rodando, pare os processos antigos (porta 8080/8811) antes de rodar de
   novo, para carregar o código novo.

`promote.ps1` só faz `git merge` local (sem `--force`, sem push) e recusa
promover se o ambiente de destino tiver mudanças não commitadas.

## O que fica isolado por ambiente

- **Banco de dados** (`DATA_DIR`): usuários, senhas, config, tudo em
  `.runtime\data\webui.db` de cada worktree.
- **Allowlist de assinantes da Kiwify** (`minghat_subscribers.json`): segue
  o `DATA_DIR`, então testar o webhook em staging nunca autoriza nem
  desativa e-mail nenhum de cliente real.
- **E-mail de boas-vindas**: as variáveis `MINGHAT_SMTP_*` só devem ser
  configuradas em produção (`D:\IA\scripts\start-local.ps1`). Dev e staging
  não têm SMTP configurado de propósito — o webhook funciona, mas o envio
  real de e-mail fica pulado (só loga aviso).

## O que é compartilhado (de propósito, pra economizar recursos)

- Ollama (mesmo modelo, mesma porta, para os três).
- Interpretador Python / dependências (`.venv`) — o código de cada branch
  ainda roda isolado, só as bibliotecas de terceiros são as mesmas.
- Ferramentas de recon (`subfinder`, `httpx`, etc.) do modo Pentesting.

`node_modules` **não** é compartilhado (o disco `D:` é exFAT, que não
suporta link/junction de diretório) — cada worktree tem sua própria cópia
instalada via `npm install --engine-strict=false`.
