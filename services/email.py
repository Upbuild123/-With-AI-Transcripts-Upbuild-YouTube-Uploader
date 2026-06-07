import os
import traceback
import resend as resend_lib


def send_error_alert(program: str, attempted_title: str, error: Exception) -> None:
    api_key = os.environ.get("RESEND_API_KEY", "")
    email_from = os.environ.get("EMAIL_FROM", "Upbuild <noreply@upbuild.com>")
    to_email = os.environ.get("ERROR_ALERT_EMAIL", "michael@upbuild.com")

    subject = f"[Upbuild Uploader Error] {program}"
    tb = traceback.format_exc()
    html = f"""
<p><strong>Program:</strong> {program}</p>
<p><strong>Attempted title:</strong> {attempted_title}</p>
<p><strong>Error:</strong> {error}</p>
<pre>{tb}</pre>
"""

    if not api_key:
        print(f"[email] Would send error alert to {to_email}: {subject}")
        print(f"[email] Error: {error}")
        return

    resend_lib.api_key = api_key
    try:
        resend_lib.Emails.send({"from": email_from, "to": to_email, "subject": subject, "html": html})
    except Exception as e:
        print(f"[email] Failed to send error alert: {e}")
