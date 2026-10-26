# MingHat na porta 8811

Execute no PowerShell, dentro de `D:\IA`:

```powershell
.\scripts\start-local.ps1
```

Abra <http://localhost:8811> depois que os servicos iniciarem.

- Frontend MingHat, baseado no Open WebUI: `127.0.0.1:8811`.
- Backend: `127.0.0.1:8080`.
- Ollama: `127.0.0.1:11434`.
- Modelo inicial: `uncensored-br:latest`, exibido como MingHat na interface. O nome do modelo no Ollama permanece inalterado.
- O perfil local de `uncensored-br:latest` usa conversa sem ferramentas nativas, compativel com as capacidades informadas pelo Ollama. Essa configuracao fica no banco do Open WebUI.
- Ao selecionar `PENTESTING`, pedidos explicitos de recon ou enumeracao com um dominio valido executam um fluxo basico: Subfinder (`-all -t 100 -v`), DNSx, HTTPx, Katana com profundidade 1, GAU e extracao de referencias a buckets S3. A saida real e anexada ao contexto para o modelo organizar. O modo `MINGHAT` nunca dispara esse fluxo.
- Subfinder 2.14.0, DNSx 1.3.1, HTTPx 1.12.0, Katana 1.7.0 e GAU 2.2.4 sao instalados em `.runtime/tools` no primeiro inicio. O instalador baixa releases oficiais e valida os checksums SHA-256 publicados antes de extrair cada executavel.
- A etapa S3 somente identifica nomes e URLs encontrados nas saidas anteriores; ela nao testa acesso, lista objetos nem grava em buckets.
- Idioma inicial: portugues brasileiro.
- Modo pessoal local, sem tela de login. Ambos os servidores escutam somente em loopback.
- Logs de inicializacao: `.runtime/frontend.log`, `.runtime/frontend-error.log`, `.runtime/backend.log` e `.runtime/backend-error.log`.
- O ambiente Python desta instalacao fica em `%TEMP%\ia-8811-backend`, devido a erros de acesso no cache em D:. O script tambem aceita um ambiente completo em `.venv`.

O tema preto com degrade e neon roxo esta em `static/static/custom.css` e e aplicado ao modo escuro. Em navegadores com uma preferencia anterior, selecione o tema escuro nas configuracoes de aparencia.

As conversas do Open WebUI ficam em `backend/data`. O script reutiliza os servicos quando as portas ja estao ocupadas; nao encerra outros programas.
