# MingHat hardening checklist

## Segredos e tokens

- Coloque chaves reais apenas em `.env`, variáveis do provedor, cofre de segredos ou painel de deploy.
- Nunca coloque tokens reais em `src/`, `static/`, `docs/` ou arquivos enviados ao navegador.
- Rode `powershell -ExecutionPolicy Bypass -File scripts/security-preflight.ps1` antes de publicar.
- Os valores de `.env.decoy.example` são falsos. Para honeytokens reais, use um serviço de canary tokens com alerta.

## DNS contra email spoofing

Se o domínio `minghat.com.br` ainda não envia e-mail, publique estes TXT no Cloudflare:

```txt
Nome: @
Tipo: TXT
Valor: v=spf1 -all
```

```txt
Nome: _dmarc
Tipo: TXT
Valor: v=DMARC1; p=reject; sp=reject; adkim=s; aspf=s; rua=mailto:security@minghat.com.br
```

Quando contratar um provedor de e-mail, troque o SPF pelo valor do provedor e adicione os DKIMs que ele fornecer.

## Produção

- `ENABLE_SIGNUP=False` até você decidir como vender/criar contas.
- `CORS_ALLOW_ORIGIN` deve conter só `https://minghat.com.br` e subdomínios oficiais.
- `FORWARDED_ALLOW_IPS=127.0.0.1` quando usar Cloudflare Tunnel local.
- Source maps públicos ficam desligados por padrão. Só ative `SOURCEMAP=true` em ambiente privado.
- O recon usa timeouts curtos por padrão: `MINGHAT_SUBFINDER_TIMEOUT_SECONDS=45`, `MINGHAT_DNSX_TIMEOUT_SECONDS=25`, `MINGHAT_HTTPX_TIMEOUT_SECONDS=60`, `MINGHAT_KATANA_TIMEOUT_SECONDS=30` e `MINGHAT_GAU_TIMEOUT_SECONDS=20`.
- DevTools guard dificulta clique direito/atalhos no navegador em produção, mas não substitui segurança de servidor.
