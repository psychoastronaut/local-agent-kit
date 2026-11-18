from wordstat.cli import main
from wordstat.counter import count_words, ranked


def test_ranked_order():
    assert ranked(count_words("b a b c c")) == [("b", 2), ("c", 2), ("a", 1)]


def test_main_prints(tmp_path, capsys):
    f = tmp_path / "t.txt"
    f.write_text("the cat the dog")
    assert main([str(f)]) == 0
    assert capsys.readouterr().out == "the 2\ncat 1\ndog 1\n"
