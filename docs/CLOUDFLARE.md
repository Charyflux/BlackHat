# Publicar a MingHat com Cloudflare Tunnel

A MingHat continua executando nesta máquina, junto do Ollama e das ferramentas de recon. O Cloudflare Tunnel publica apenas o backend local `http://127.0.0.1:8080`, sem abrir portas no roteador.

## Pré-requisitos

- Um domínio ativo na conta Cloudflare.
- Build de produção em `build/`.
- Ollama em execução em `127.0.0.1:11434`.
- `cloudflared` instalado.

## Aplicação

Inicie a versão de produção, informando a URL pública escolhida:

```powershell
.\scripts\start-production.ps1 -PublicUrl 'https://chat.seudominio.com'
```

Esta versão serve interface e API na porta local 8080 e habilita autenticação. A primeira conta criada no banco novo recebe privilégios administrativos; depois disso, desative novos cadastros no painel administrativo se o acesso for fechado.

## Tunnel

No painel Cloudflare, crie um Cloudflare Tunnel, adicione um hostname público como `chat.seudominio.com` e aponte o serviço para:

```text
http://127.0.0.1:8080
```

Instale o conector usando o comando/token exibido pelo próprio painel. Nunca salve o token no repositório.

Não use Quick Tunnel para produção: ele não oferece hostname estável e tem limitações incompatíveis com um chat comercial.

## Operação comercial

O computador precisa permanecer ligado, com Ollama, MingHat e cloudflared ativos. Para vender com disponibilidade real, mova os três processos para um servidor Windows/Linux com GPU, supervisão de processos, backups e monitoramento.
