import io

import pytest
from sugarjazy import cli

sampleline = """{"level":"info","ts":"2022-03-24T13:44:02.851Z","logger":"tekton-pipelines-webhook", "msg":"bar FOO hello"}"""


def test_good():
    argp = cli.parse_args(sysargs=[])
    f = cli.jline(sampleline, argp)
    assert "hello" in f
    assert f"{cli.bcolors.GREEN}INFO   {cli.bcolors.ENDC}" in f
    assert "13:44:02" in f


def test_kail():
    argp = cli.parse_args(sysargs=["--kail", "--kail-prefix-format=<<{container}>>"])
    argp.stream = False
    line = """ns/pod[HELLOMOTO]: {"level":"info","ts":"2022-03-24T13:44:02.851Z","logger":"tekton-pipelines-webhook", "msg":"hello"}"""
    assert "<<HELLOMOTO>>" in cli.jline(line, argp)


def test_regexp_hl():
    argp = cli.parse_args(sysargs=["-r", "FOO"])
    argp.stream = False
    assert f"{cli.bcolors.CYAN}FOO{cli.bcolors.ENDC}" in cli.jline(sampleline, argp)


def test_hide_ts():
    argp = cli.parse_args(sysargs=["-H"])
    f = cli.jline(sampleline, argp)
    assert "13:44:02" not in f


def test_stream(monkeypatch, capsys):
    def f():
        return io.StringIO(sampleline + "\r\n" + sampleline + "\nEOF")

    with pytest.raises(SystemExit):
        monkeypatch.setattr("sys.stdin", f())
        cli.main(["-s"])
    captured = capsys.readouterr()
    assert "bar FOO hello" in captured.out
