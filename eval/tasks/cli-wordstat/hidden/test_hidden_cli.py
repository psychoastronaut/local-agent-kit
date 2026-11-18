import json
import subprocess
import sys

import pytest

from wordstat.cli import main

TEXT = "the cat and the dog and the bird a a a"


@pytest.fixture
def f(tmp_path):
    p = tmp_path / "t.txt"
    p.write_text(TEXT)
    return str(p)


def test_top(f, capsys):
    assert main([f, "--top", "2"]) == 0
    assert capsys.readouterr().out == "a 3\nthe 3\n"


def test_min_length_then_top(f, capsys):
    main([f, "--min-length", "3", "--top", "2"])
    assert capsys.readouterr().out == "the 3\nand 2\n"


def test_json_order_and_content(f, capsys):
    main([f, "--json", "--top", "3"])
    out = capsys.readouterr().out
    data = json.loads(out)
    assert list(data.items()) == [("a", 3), ("the", 3), ("and", 2)]


@pytest.mark.parametrize("bad", [["--top", "0"], ["--top", "-1"], ["--min-length", "-2"]])
def test_invalid_values_exit_2(f, bad):
    with pytest.raises(SystemExit) as e:
        main([f] + bad)
    assert e.value.code == 2


def test_module_entrypoint(f):
    r = subprocess.run([sys.executable, "-m", "wordstat", f, "--json"],
                       capture_output=True, text=True)
    assert r.returncode == 0 and json.loads(r.stdout)["the"] == 3
