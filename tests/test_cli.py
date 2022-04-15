import datetime
import io

import pytest
from sugarjazy import cli

sampleline = """{"level":"info","ts":"2022-03-24T13:44:02.851Z","logger":"tekton-pipelines-webhook", "msg":"bar FOO hello", "event": "firstev"}"""


def test_good():
    argp = cli.parse_args(sysargs=[])
    f = cli.jline(sampleline, argp)
    assert "hello" in f
    assert f"{cli.bcolors.GREEN}INFO   {cli.bcolors.ENDC}" in f
    assert "13:44:02" in f
    assert cli.CURRENT_EVENT_CHAR in f

    f = cli.jline(sampleline.replace("info", "warn"), argp)
    assert f"{cli.bcolors.YELLOW}WARN   {cli.bcolors.ENDC}" in f

    f = cli.jline(sampleline.replace("info", "error"), argp)
    assert f"{cli.bcolors.RED}ERROR  {cli.bcolors.ENDC}" in f

    f = cli.jline(sampleline.replace("info", "other"), argp)
    assert f"{cli.bcolors.CYAN}OTHER  {cli.bcolors.ENDC}" in f


def test_float():
    ts = 1648151733.950114
    # pylint: disable=C0209
    tsfloat = (
        """{"level":"info","ts":%f,"logger":"tekton-pipelines-webhook", "msg":"bar FOO hello", "event": "firstev"}"""
        % ts
    )
    argp = cli.parse_args(sysargs=[])
    f = cli.jline(tsfloat, argp)
    assert str(datetime.datetime.fromtimestamp(ts).strftime(argp.timeformat)) in f


def test_not_json():
    argp = cli.parse_args(sysargs=[])
    f = cli.jline("NOT JSON", argp)
    assert f == "NOT JSON"


def test_skip_when_filtered():
    argp = cli.parse_args(sysargs=["-F=donotfilter"])
    f = cli.jline(sampleline, argp)
    assert f == ""

    argp = cli.parse_args(sysargs=["-F=info"])
    samplelinenolvel = """{"foo":"info","ts":"2022-03-24T13:44:02.851Z","logger":"tekton-pipelines-webhook", "msg":"bar FOO hello"}"""
    f = cli.jline(samplelinenolvel, argp)
    assert f == ""

    argp = cli.parse_args(sysargs=["-F=info"])
    f = cli.jline("FOOBAR", argp)
    assert f == ""


def test_no_keys_no_parsing():
    argp = cli.parse_args(sysargs=[])
    sample = """{"foo":"info","ts":"2022-03-24T13:44:02.851Z","logger":"tekton-pipelines-webhook", "msg":"bar FOO hello"}"""
    f = cli.jline(sample, argp)
    assert f == sample


def test_kail():
    argp = cli.parse_args(sysargs=["--kail", "--kail-prefix-format=<<{container}>>"])
    argp.stream = False
    line = """ns/pod[HELLOMOTO]: {"level":"info","ts":"2022-03-24T13:44:02.851Z","logger":"tekton-pipelines-webhook", "msg":"hello"}"""
    assert "<<HELLOMOTO>>" in cli.jline(line, argp)


def test_kail_only_on_stream(capsys):
    with pytest.raises(SystemExit):
        cli.main(["--kail", "/tmp/foo"])
    captured = capsys.readouterr()
    assert "kail mode only work on stream" in captured.out


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


def test_parse(capsys):
    fp = io.StringIO(sampleline + "\r\n" + sampleline + "\n")
    argp = cli.parse_args(sysargs=["-H"])
    cli.parse(fp, argp)
    captured = capsys.readouterr()
    assert "bar FOO hello" in captured.out


def test_parse_files(capsys, tmp_path):
    log_file = tmp_path / "log"
    log_file.write_text(sampleline + "\n" + sampleline)
    with pytest.raises(SystemExit):
        cli.main([str(log_file)])
    captured = capsys.readouterr()
    assert "bar FOO hello" in captured.out
