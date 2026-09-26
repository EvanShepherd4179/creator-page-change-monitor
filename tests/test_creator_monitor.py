from src.creator_monitor import compare_text, normalize_html


def test_delivery_change_crosses_alert_threshold():
    old = normalize_html("<h1>New print</h1><p>Ships in five days.</p>")
    new = normalize_html("<h1>New print</h1><p>Ships in two days.</p>")
    result = compare_text(old, new, threshold=0.08)
    assert result.status == "changed"
    assert result.ratio >= 0.08


def test_whitespace_only_edit_is_unchanged():
    old = normalize_html("<p>Member update</p>")
    new = normalize_html("<p>  Member   update </p>")
    result = compare_text(old, new)
    assert result.status == "unchanged"
    assert result.ratio == 0
