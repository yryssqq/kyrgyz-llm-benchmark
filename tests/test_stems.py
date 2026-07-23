import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from kyrgyz_eval.stems import read_stems


def test_strips_inline_comments(tmp_path):
    f = tmp_path / "stems.txt"
    f.write_text("гүл  # flower\nбоор\n", encoding="utf-8")
    assert read_stems(f) == [("гүл", None), ("боор", None)]


def test_skips_full_line_comments_and_blanks(tmp_path):
    f = tmp_path / "stems.txt"
    f.write_text("# header\n\nат\n   \nкөз\n", encoding="utf-8")
    assert read_stems(f) == [("ат", None), ("көз", None)]


def test_irregular_plural_override(tmp_path):
    f = tmp_path / "stems.txt"
    f.write_text("бала|балдар\nкыз\n", encoding="utf-8")
    assert read_stems(f) == [("бала", "балдар"), ("кыз", None)]


def test_irregular_with_trailing_comment(tmp_path):
    f = tmp_path / "stems.txt"
    f.write_text("бала|балдар  # child\n", encoding="utf-8")
    assert read_stems(f) == [("бала", "балдар")]
