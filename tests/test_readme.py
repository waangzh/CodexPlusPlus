from pathlib import Path


def test_readme_limits_discussion_group_qr_size():
    text = Path("README.md").read_text(encoding="utf-8")

    assert '<img src="docs/images/discussion-group-qr.jpg"' in text
    assert 'width="260"' in text
    assert '![Codex++ 交流群二维码](docs/images/discussion-group-qr.jpg)' not in text
