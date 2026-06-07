from services.drive import drive_link_to_file_id

def test_extract_file_id_slash_d_format():
    url = "https://drive.google.com/file/d/1ABC123xyz/view?usp=sharing"
    assert drive_link_to_file_id(url) == "1ABC123xyz"

def test_extract_file_id_open_format():
    url = "https://drive.google.com/open?id=1ABC123xyz"
    assert drive_link_to_file_id(url) == "1ABC123xyz"

def test_extract_file_id_invalid_raises():
    import pytest
    with pytest.raises(ValueError, match="Could not extract"):
        drive_link_to_file_id("https://example.com/not-a-drive-link")
