import pytest
from unittest.mock import patch, MagicMock

from services.ai_content import generate_titles_and_summary, generate_topic_suggestions


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


def test_generate_topic_suggestions_with_previous_topic(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")

    captured_prompt = {}

    class FakeResponse:
        content = [type("C", (), {"text": (
            "1. Prema Vivarta - Part 10\n"
            "2. The Nature of Surrender\n"
            "3. Cultivating Humility\n"
            "4. Service Without Attachment\n"
            "5. Faith in Difficult Times\n"
        )})()]

    class FakeMessages:
        def create(self, **kwargs):
            captured_prompt["text"] = kwargs["messages"][0]["content"]
            return FakeResponse()

    class FakeClient:
        def __init__(self, api_key):
            self.messages = FakeMessages()

    import services.ai_content as ai_content
    monkeypatch.setattr(ai_content.anthropic, "Anthropic", FakeClient)

    topics = generate_topic_suggestions("some transcript text", previous_topic="Prema Vivarta - Part 9")

    assert len(topics) == 5
    assert topics[0] == "Prema Vivarta - Part 10"
    assert "Prema Vivarta - Part 9" in captured_prompt["text"]
    assert "continu" in captured_prompt["text"].lower()


def test_generate_topic_suggestions_without_previous_topic(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")

    captured_prompt = {}

    class FakeResponse:
        content = [type("C", (), {"text": (
            "1. The Nature of Surrender\n"
            "2. Cultivating Humility\n"
            "3. Service Without Attachment\n"
            "4. Faith in Difficult Times\n"
            "5. The Power of Association\n"
        )})()]

    class FakeMessages:
        def create(self, **kwargs):
            captured_prompt["text"] = kwargs["messages"][0]["content"]
            return FakeResponse()

    class FakeClient:
        def __init__(self, api_key):
            self.messages = FakeMessages()

    import services.ai_content as ai_content
    monkeypatch.setattr(ai_content.anthropic, "Anthropic", FakeClient)

    topics = generate_topic_suggestions("some transcript text")

    assert len(topics) == 5
    assert "Part" not in captured_prompt["text"].split("Transcript:")[0] or "previous" not in captured_prompt["text"].lower()
    assert "continu" not in captured_prompt["text"].lower()


def test_generate_topic_suggestions_raises_on_too_few(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")

    class FakeResponse:
        content = [type("C", (), {"text": (
            "1. The Nature of Surrender\n"
            "2. Cultivating Humility\n"
        )})()]

    class FakeMessages:
        def create(self, **kwargs):
            return FakeResponse()

    class FakeClient:
        def __init__(self, api_key):
            self.messages = FakeMessages()

    import services.ai_content as ai_content
    monkeypatch.setattr(ai_content.anthropic, "Anthropic", FakeClient)

    import pytest
    with pytest.raises(ValueError):
        generate_topic_suggestions("some transcript text")
