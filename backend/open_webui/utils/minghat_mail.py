"""Envio de e-mail transacional da BlackHat (ex.: boas-vindas pós-compra).

Usa SMTP puro (smtplib da stdlib, sem dependência nova). As credenciais vêm de
variáveis de ambiente — sem elas configuradas, o envio é pulado (log de aviso)
em vez de quebrar o webhook que chamou a função.
"""

import logging
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

log = logging.getLogger(__name__)

SMTP_HOST = os.getenv("MINGHAT_SMTP_HOST", "")
SMTP_PORT = int(os.getenv("MINGHAT_SMTP_PORT", "587"))
SMTP_USER = os.getenv("MINGHAT_SMTP_USER", "")
SMTP_PASSWORD = os.getenv("MINGHAT_SMTP_PASSWORD", "")
SMTP_FROM = os.getenv("MINGHAT_SMTP_FROM", SMTP_USER)
SMTP_USE_TLS = os.getenv("MINGHAT_SMTP_USE_TLS", "true").lower() != "false"
SIGNUP_URL = os.getenv("MINGHAT_SIGNUP_URL", "https://minghat.com.br/auth?mode=signup")


def is_configured() -> bool:
    return bool(SMTP_HOST and SMTP_USER and SMTP_PASSWORD and SMTP_FROM)


def _build_welcome_message(email: str) -> MIMEMultipart:
    msg = MIMEMultipart("alternative")
    msg["Subject"] = "\U0001f3a9 Sua assinatura BlackHat foi liberada — crie seu acesso"
    msg["From"] = SMTP_FROM
    msg["To"] = email

    text = f"""Sua assinatura da BlackHat foi confirmada!

Para começar a usar a IA, crie sua conta agora em:
{SIGNUP_URL}

IMPORTANTE: use o MESMO e-mail que você usou na compra ({email}) e escolha
a senha que quiser. Essa é a senha de acesso à BlackHat, ela não tem
relação com a senha usada no pagamento.

Depois de criar a conta, é só entrar e usar a BlackHat sem filtro,
com o modo Pentesting liberado, disponível 24 horas por dia.

Qualquer dúvida, responda este e-mail.

— Equipe BlackHat
"""

    html = f"""\
<html>
  <body style="margin:0;padding:0;background:#0b0b10;font-family:'Segoe UI',Arial,sans-serif;">
    <table width="100%" cellpadding="0" cellspacing="0" style="background:#0b0b10;padding:32px 0;">
      <tr>
        <td align="center">
          <table width="480" cellpadding="0" cellspacing="0"
                 style="background:linear-gradient(180deg,#1a1622,#100d18);border:1px solid rgba(194,154,255,0.3);
                        border-radius:20px;padding:32px 28px;color:#f4f1fa;">
            <tr>
              <td align="center" style="font-size:34px;padding-bottom:8px;">&#x1F3A9;</td>
            </tr>
            <tr>
              <td align="center" style="font-size:22px;font-weight:800;padding-bottom:12px;">
                Sua assinatura BlackHat está liberada!
              </td>
            </tr>
            <tr>
              <td style="font-size:14.5px;line-height:1.6;color:#c9c5d6;padding-bottom:22px;">
                Recebemos a confirmação do seu pagamento. Agora falta só um passo para você
                começar a usar a <strong style="color:#c29aff;">IA sem filtro</strong> da BlackHat,
                com o modo <strong style="color:#c29aff;">Pentesting</strong> liberado.
              </td>
            </tr>
            <tr>
              <td style="font-size:14.5px;line-height:1.6;color:#c9c5d6;padding-bottom:6px;">
                1&#41; Clique no botão abaixo<br />
                2&#41; Use o <strong>mesmo e-mail da compra</strong>: <strong>{email}</strong><br />
                3&#41; Escolha a senha que quiser para acessar a BlackHat
              </td>
            </tr>
            <tr>
              <td align="center" style="padding:22px 0;">
                <a href="{SIGNUP_URL}"
                   style="display:inline-block;padding:14px 28px;border-radius:999px;font-weight:700;
                          font-size:15px;text-decoration:none;color:#150c22;
                          background:linear-gradient(180deg,#d9bcff,#c29aff);">
                  Criar minha conta agora
                </a>
              </td>
            </tr>
            <tr>
              <td style="font-size:12px;color:#726e80;text-align:center;padding-top:10px;">
                Dúvidas? É só responder este e-mail.<br />
                &#128274; Sua compra foi processada com seguran&ccedil;a pela Cakto.
              </td>
            </tr>
          </table>
        </td>
      </tr>
    </table>
  </body>
</html>
"""

    msg.attach(MIMEText(text, "plain", "utf-8"))
    msg.attach(MIMEText(html, "html", "utf-8"))
    return msg


def send_welcome_email(email: str) -> bool:
    """Envia o e-mail de boas-vindas pedindo para o comprador criar a conta.

    Retorna True se enviou, False se pulou (sem config) ou falhou (logado).
    Nunca lança exceção — quem chama não deve ter o fluxo quebrado por isso.
    """
    if not email:
        return False

    if not is_configured():
        log.warning(
            "BlackHat mail: SMTP nao configurado (MINGHAT_SMTP_HOST/USER/PASSWORD) "
            "- pulando envio de boas-vindas para %s",
            email,
        )
        return False

    try:
        msg = _build_welcome_message(email)
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=15) as server:
            if SMTP_USE_TLS:
                server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(SMTP_FROM, [email], msg.as_string())
        log.info("BlackHat mail: e-mail de boas-vindas enviado para %s", email)
        return True
    except Exception:
        log.exception("BlackHat mail: falha ao enviar e-mail de boas-vindas para %s", email)
        return False
