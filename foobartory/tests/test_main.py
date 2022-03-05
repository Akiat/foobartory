from types import SimpleNamespace

from foobartory.main import start


def test_main(capsys):
    args = SimpleNamespace(quick=5000)
    start(args=args)
    res = capsys.readouterr()
    assert "Your Foobartory has now" in res.out
