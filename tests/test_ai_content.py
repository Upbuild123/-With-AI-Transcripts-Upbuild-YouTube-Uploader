import pytest
from unittest.mock import patch, MagicMock

from services.ai_content import generate_titles_and_summary


SAMPLE_TRANSCRIPT = "Today we discussed the nature of the self and how to quiet the mind."

SAMPLE_RESPONSE = """TITLES:
1. The Quiet Mind: Exploring the Inner Self
2. Who Are We Really? A Conversation on Consciousness
3. Stilling the Mind, Knowing the Self
4. Beyond the Ego: Remembering Who We Are
5. The Inner Life: Presence, Stillness, and Identity

SUMMARY:
In this session, we explored the nature of the self and the practice of quieting the mind. The conversation touched on how our busy lives often pull us away from a deeper awareness of who we are. Participants reflected on how stillness creates space to reconnect with something more essential. The group considered practical ways to bring this awareness into daily life."""


def test_generate_returns_five_titles():
    mock_client = MagicMock()
    mock_message = MagicMock()
    mock_message.content = [MagicMock(text=SAMPLE_RESPONSE)]
    mock_client.messages.create.return_value = mock_message

    with patch("services.ai_content.anthropic.Anthropic", return_value=mock_client), \
         patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test-key"}):
        result = generate_titles_and_summary(SAMPLE_TRANSCRIPT)

    assert len(result["titles"]) == 5
    assert result["titles"][0] == "The Quiet Mind: Exploring the Inner Self"


def test_generate_returns_summary():
    mock_client = MagicMock()
    mock_message = MagicMock()
    mock_message.content = [MagicMock(text=SAMPLE_RESPONSE)]
    mock_client.messages.create.return_value = mock_message

    with patch("services.ai_content.anthropic.Anthropic", return_value=mock_client), \
         patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test-key"}):
        result = generate_titles_and_summary(SAMPLE_TRANSCRIPT)

    assert "summary" in result
    assert len(result["summary"]) > 20


def test_generate_sends_transcript_in_prompt():
    mock_client = MagicMock()
    mock_message = MagicMock()
    mock_message.content = [MagicMock(text=SAMPLE_RESPONSE)]
    mock_client.messages.create.return_value = mock_message

    with patch("services.ai_content.anthropic.Anthropic", return_value=mock_client), \
         patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test-key"}):
        generate_titles_and_summary(SAMPLE_TRANSCRIPT)

    call_kwargs = mock_client.messages.create.call_args[1]
    prompt_text = call_kwargs["messages"][0]["content"]
    assert SAMPLE_TRANSCRIPT in prompt_text


def test_generate_raises_if_no_api_key():
    with patch.dict("os.environ", {"ANTHROPIC_API_KEY": ""}, clear=False):
        with pytest.raises(ValueError, match="ANTHROPIC_API_KEY"):
            generate_titles_and_summary(SAMPLE_TRANSCRIPT)
