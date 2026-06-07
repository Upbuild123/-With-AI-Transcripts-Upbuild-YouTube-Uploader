import os
import tempfile
from unittest.mock import patch, MagicMock, mock_open
import pytest

from services.transcription import extract_audio, transcribe


def test_extract_audio_calls_ffmpeg():
    mock_tmp = MagicMock()
    mock_tmp.name = "/tmp/audio_abc.mp3"

    with patch("services.transcription.tempfile.NamedTemporaryFile", return_value=mock_tmp):
        with patch("services.transcription.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            result = extract_audio("/path/to/video.mp4")

    assert result == "/tmp/audio_abc.mp3"
    mock_run.assert_called_once()
    args = mock_run.call_args[0][0]
    assert "ffmpeg" in args
    assert "-ac" in args
    assert "1" in args          # mono
    assert "-ar" in args
    assert "16000" in args      # 16kHz
    assert "-q:a" in args
    assert "5" in args


def test_extract_audio_raises_on_ffmpeg_failure():
    mock_tmp = MagicMock()
    mock_tmp.name = "/tmp/audio_abc.mp3"

    with patch("services.transcription.tempfile.NamedTemporaryFile", return_value=mock_tmp):
        with patch("services.transcription.subprocess.run") as mock_run:
            with patch("services.transcription.os.unlink"):
                mock_run.return_value = MagicMock(returncode=1, stderr=b"error")
                with pytest.raises(RuntimeError, match="ffmpeg"):
                    extract_audio("/path/to/video.mp4")


def test_transcribe_returns_text():
    mock_client = MagicMock()
    mock_client.audio.transcriptions.create.return_value = MagicMock(text="Hello world")

    with patch("services.transcription.openai.OpenAI", return_value=mock_client):
        with patch("builtins.open", mock_open()):
            with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}):
                result = transcribe("/tmp/audio.mp3")

    assert result == "Hello world"


def test_transcribe_raises_on_missing_api_key():
    env_without_key = {k: v for k, v in os.environ.items() if k != "OPENAI_API_KEY"}
    with patch.dict("os.environ", env_without_key, clear=True):
        with pytest.raises(ValueError, match="OPENAI_API_KEY"):
            transcribe("/tmp/audio.mp3")
