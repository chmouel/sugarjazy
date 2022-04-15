import datetime
import io

import pytest

from sugarjazy import cli

sampleline = """{"level":"info","ts":"2022-03-24T13:44:02.851Z","logger":"tekton-pipelines-webhook", "msg":"bar FOO hello", "event": "firstev"}"""


def test_good():
    sj = cli.Sugarjazy(sysargs=[])
    f = sj.parse(sampleline)
    assert "hello" in f
    assert f"{cli.bcolors.GREEN}INFO   {cli.bcolors.ENDC}" in f
    assert "13:44:02" in f
    assert cli.CURRENT_EVENT_CHAR in f

    f = sj.parse(sampleline.replace("info", "warn"))
    assert f"{cli.bcolors.YELLOW}WARN   {cli.bcolors.ENDC}" in f

    f = sj.parse(sampleline.replace("info", "error"))
    assert f"{cli.bcolors.RED}ERROR  {cli.bcolors.ENDC}" in f

    f = sj.parse(sampleline.replace("info", "other"))
    assert f"{cli.bcolors.CYAN}OTHER  {cli.bcolors.ENDC}" in f


def test_float():
    ts = 1648151733.950114
    # pylint: disable=C0209
    tsfloat = (
        """{"level":"info","ts":%f,"logger":"tekton-pipelines-webhook", "msg":"bar FOO hello", "event": "firstev"}"""
        % ts
    )
    sj = cli.Sugarjazy(sysargs=[])
    f = sj.parse(tsfloat)
    assert str(datetime.datetime.fromtimestamp(ts).strftime(sj.argp.timeformat)) in f


def test_not_json():
    sj = cli.Sugarjazy(sysargs=[])
    f = sj.parse("NOT JSON")
    assert f == "NOT JSON"


def test_skip_when_filtered():
    sj = cli.Sugarjazy(sysargs=["-F=donotfilter"])
    f = sj.parse(sampleline)
    assert f == ""

    sj = cli.Sugarjazy(sysargs=["-F=info"])
    samplelinenolvel = """{"foo":"info","ts":"2022-03-24T13:44:02.851Z","logger":"tekton-pipelines-webhook", "msg":"bar FOO hello"}"""
    f = sj.parse(samplelinenolvel)
    assert f == ""

    sj = cli.Sugarjazy(sysargs=["-F=info"])
    f = sj.parse("FOOBAR")
    assert f == ""


def test_no_keys_no_parsing():
    sample = """{"foo":"info","ts":"2022-03-24T13:44:02.851Z","logger":"tekton-pipelines-webhook", "msg":"bar FOO hello"}"""
    sj = cli.Sugarjazy(sysargs=[])
    f = sj.parse(sample)
    assert f == sample


def test_kail():
    sj = cli.Sugarjazy(sysargs=["--kail", "--kail-prefix-format=<<{container}>>"])
    line = """ns/pod[HELLOMOTO]: {"level":"info","ts":"2022-03-24T13:44:02.851Z","logger":"tekton-pipelines-webhook", "msg":"hello"}"""
    assert "<<HELLOMOTO>>" in sj.parse(line)


def test_kail_only_on_stream():
    with pytest.raises(cli.SugarJazyBadArgumentExc):
        cli.Sugarjazy(sysargs=["--kail", "/tmp/foo"])


def test_regexp_hl():
    sj = cli.Sugarjazy(sysargs=["-r", "FOO"])
    assert f"{cli.bcolors.CYAN}FOO{cli.bcolors.ENDC}" in sj.parse(sampleline)


def test_hide_ts():
    sj = cli.Sugarjazy(sysargs=["-H"])
    f = sj.parse(sampleline)
    assert "13:44:02" not in f


def test_stream(monkeypatch, capsys):
    def f():
        return io.StringIO(sampleline + "\r\n" + sampleline + "\nEOF")

    monkeypatch.setattr("sys.stdin", f())
    cli.main(["-s"])
    captured = capsys.readouterr()
    assert "bar FOO hello" in captured.out


def test_parse(capsys):
    fp = io.StringIO(sampleline + "\r\n" + sampleline + "\n")
    sj = cli.Sugarjazy(sysargs=["-H"])
    sj.do_fp(fp)
    captured = capsys.readouterr()
    assert "bar FOO hello" in captured.out


def test_parse_files(capsys, tmp_path):
    log_file = tmp_path / "log"
    log_file.write_text(sampleline + "\n" + sampleline)
    cli.main([str(log_file)])
    captured = capsys.readouterr()
    assert "bar FOO hello" in captured.out
