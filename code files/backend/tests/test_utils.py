from backend.utils import clean_json_block, truncate


def test_clean_json_block_handles_fences_and_leading_text():
    raw = 'Here is the JSON:\n```json\n{"ok": true, "items": [1,2]}\n```'
    assert clean_json_block(raw).startswith('{"ok": true')


def test_truncate_adds_marker():
    value = truncate("abcdef", 3)
    assert value.startswith("abc")
    assert "truncated" in value
