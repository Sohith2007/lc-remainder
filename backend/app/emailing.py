from __future__ import annotations

from email.message import EmailMessage
from html import escape
import smtplib

from .models import DailyProblem


DESCRIPTION_LIMIT = 2200


def _description_preview(description: str) -> str:
  lines = []
  previous_blank = True
  for raw_line in description.splitlines():
    line = " ".join(raw_line.split())
    if not line:
      if not previous_blank:
        lines.append("")
      previous_blank = True
      continue
    lines.append(line)
    previous_blank = False

  preview = "\n".join(lines).strip()
  if len(preview) <= DESCRIPTION_LIMIT:
    return preview
  return preview[: DESCRIPTION_LIMIT - 3].rstrip() + "..."


def build_email(problem: DailyProblem, sender: str, recipient: str) -> EmailMessage:
    message = EmailMessage()
    message["Subject"] = f"LeetCode Daily Problem: {problem.title}"
    message["From"] = sender
    message["To"] = recipient

    preview = _description_preview(problem.description)
    sent_time = problem.fetched_at.strftime("%Y-%m-%d %H:%M UTC")

    text_body = (
        f"LeetCode Daily Reminder\n"
        f"======================\n\n"
        f"Problem: {problem.title}\n"
        f"Difficulty: {problem.difficulty}\n"
        f"Fetched At: {sent_time}\n"
        f"Link: {problem.url}\n\n"
        f"Description Preview:\n{preview}\n\n"
        f"Open the link above to read the full problem statement and examples.\n"
    )

    escaped_title = escape(problem.title)
    escaped_difficulty = escape(problem.difficulty)
    escaped_url = escape(problem.url)
    escaped_preview = escape(preview).replace("\n", "<br />")
    html_body = f"""
    <html>
      <body style="margin:0; padding:24px; background:#f4f6f8; font-family:Segoe UI, Arial, sans-serif; color:#0f172a;">
        <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="max-width:680px; margin:0 auto; background:#ffffff; border:1px solid #e2e8f0; border-radius:12px; overflow:hidden;">
          <tr>
            <td style="padding:20px 24px; background:#0b1220; color:#f8fafc;">
              <h1 style="margin:0; font-size:22px;">LeetCode Daily Reminder</h1>
              <p style="margin:8px 0 0 0; font-size:14px; color:#cbd5e1;">{sent_time}</p>
            </td>
          </tr>
          <tr>
            <td style="padding:24px;">
              <h2 style="margin:0 0 10px 0; font-size:24px; line-height:1.3;">{escaped_title}</h2>
              <p style="margin:0 0 16px 0; font-size:14px; color:#334155;">Difficulty: <strong>{escaped_difficulty}</strong></p>
              <p style="margin:0 0 18px 0;">
                <a href="{escaped_url}" style="display:inline-block; padding:10px 14px; background:#0ea5e9; color:#ffffff; text-decoration:none; border-radius:8px; font-weight:600;">Open Problem on LeetCode</a>
              </p>
              <h3 style="margin:0 0 10px 0; font-size:17px; color:#1e293b;">Description Preview</h3>
              <p style="margin:0; line-height:1.6; color:#334155;">{escaped_preview}</p>
            </td>
          </tr>
        </table>
      </body>
    </html>
    """
    message.set_content(text_body)
    message.add_alternative(html_body, subtype="html")
    return message


def send_email(message: EmailMessage, host: str, port: int, username: str, password: str) -> None:
    with smtplib.SMTP(host, port) as smtp:
        smtp.starttls()
        smtp.login(username, password)
        smtp.send_message(message)