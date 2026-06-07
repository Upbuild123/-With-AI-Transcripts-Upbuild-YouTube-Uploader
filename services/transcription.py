import os
import subprocess
import tempfile

import openai


def extract_audio(video_path: str) -> str:
    """Extract mono mp3 audio from video file. Returns path to temp mp3 file."""
    tmp = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
    tmp.close()
    audio_path = tmp.name

    result = subprocess.run(
        [
            "ffmpeg", "-y", "-i", video_path,
            "-ac", "1",       # mono
            "-ar", "16000",   # 16kHz
            "-q:a", "5",      # lossy compression
            audio_path,
        ],
        capture_output=True,
    )

    if result.returncode != 0:
        os.unlink(audio_path)
        raise RuntimeError(
            f"ffmpeg failed. Make sure ffmpeg is installed (brew install ffmpeg).\n"
            f"Error: {result.stderr.decode(errors='replace')}"
        )

    return audio_path


def transcribe(audio_path: str) -> str:
    """Send audio file to OpenAI Whisper API. Returns transcript text."""
    client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    with open(audio_path, "rb") as f:
        response = client.audio.transcriptions.create(
            model="whisper-1",
            file=f,
        )
    return response.text
