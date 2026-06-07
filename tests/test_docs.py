from services.docs import _find_cell_range, _cell_text

def _make_cell(text, start, end):
    return {
        "startIndex": start,
        "endIndex": end,
        "content": [{
            "paragraph": {
                "elements": [{"textRun": {"content": text}}]
            }
        }]
    }

def _make_doc(rows):
    table_rows = []
    for row in rows:
        table_rows.append({"tableCells": [_make_cell(t, s, e) for t, s, e in row]})
    return {"body": {"content": [{"table": {"tableRows": table_rows}}]}}

def test_cell_text():
    cell = _make_cell("Jun. 9, 2026\n", 10, 25)
    assert "Jun. 9, 2026" in _cell_text(cell)

def test_find_cell_range_col4():
    doc = _make_doc([
        [("Jun. 2, 2026\n", 5, 20), ("Title\n", 21, 30), ("x\n", 31, 40), ("x\n", 41, 50), ("x\n", 51, 60)],
        [("Jun. 9, 2026\n", 61, 77), ("Title\n", 78, 87), ("x\n", 88, 97), ("x\n", 98, 107), ("x\n", 108, 118)],
    ])
    start, end = _find_cell_range(doc, "Jun. 9, 2026", col_index=3)
    assert start == 98
    assert end == 107

def test_find_cell_range_not_found():
    import pytest
    doc = _make_doc([
        [("Jun. 2, 2026\n", 5, 20), ("x\n", 21, 30), ("x\n", 31, 40), ("x\n", 41, 50), ("x\n", 51, 60)],
    ])
    with pytest.raises(ValueError, match="not found"):
        _find_cell_range(doc, "Sep. 22, 2026", col_index=3)
