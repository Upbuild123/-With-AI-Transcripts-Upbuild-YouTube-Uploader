from unittest.mock import patch, MagicMock
from services.email import send_error_alert

def test_send_error_alert_calls_resend(monkeypatch):
    monkeypatch.setenv("RESEND_API_KEY", "re_test_key")
    monkeypatch.setenv("EMAIL_FROM", "Upbuild <noreply@upbuild.com>")
    monkeypatch.setenv("ERROR_ALERT_EMAIL", "michael@upbuild.com")

    mock_send = MagicMock()
    with patch("resend.Emails.send", mock_send):
        send_error_alert(
            program="RWWA",
            attempted_title="RWWA - Test - Part 1 - Jun. 9, 2026",
            error=ValueError("something broke"),
        )

    mock_send.assert_called_once()
    call_kwargs = mock_send.call_args[0][0]
    assert call_kwargs["to"] == "michael@upbuild.com"
    assert "RWWA" in call_kwargs["subject"]
    assert "something broke" in call_kwargs["html"]

def test_send_error_alert_no_api_key_does_not_raise(monkeypatch, capsys):
    monkeypatch.delenv("RESEND_API_KEY", raising=False)
    monkeypatch.setenv("ERROR_ALERT_EMAIL", "michael@upbuild.com")
    send_error_alert("RWWA", "RWWA - Test - Part 1 - Jun. 9, 2026", ValueError("test"))
    captured = capsys.readouterr()
    assert "[email]" in captured.out
