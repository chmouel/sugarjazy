# sugarjazy - parse json logs nicely

sugarjazy is a simple tool to parse json logs and output them in a nice format with nice colors.

Usually play nicely with <https://github.com/uber-go/zap> when using the ["Sugar"](https://pkg.go.dev/go.uber.org/zap#Logger.Sugar) logger output.

## Screenshot

### Default

![screenshot](./.github/screenshot.png)

### Stream from kail with sugarjazy

https://user-images.githubusercontent.com/98980/159916310-fabaa48e-b92a-4a41-a935-a1cb2a31e8fe.mp4


## Installation

There is not many dependencies on this package but [`python-dateutil`](https://dateutil.readthedocs.io/en/stable/) is an optional dependency, if the package is not installed you will not be be able to show the log timestamps.

### Arch

You can install it [from aur](https://aur.archlinux.org/packages/sugarjazy) with your aurhelper, like yay :

```
yay -S sugarjazy
```

### pip

With pip from pypi - <https://pypi.org/project/sugarjazy/>

```
pip install --user sugarjazy
```

(make sure $HOME/.local/bin is in your PATH)

### git clone

you will need [poetry](https://python-poetry.org/) :

```
git clone https://github.com/chmouel/sugarjazy
cd sugarjazy
poetry run sugarjazy
```

## Usage

You can use `sugarjazy` in multiple ways :

- By piping your logs: `kubectl logs podname|sugarjazy`
- By streamining your logs: `kubectl logs -f podname|sugarjazy -s`
- Or with the file (or multiples files) directly: `sugarjazy /tmp/file1.log /tmp/file2.log`
- Using kail from https://github.com/boz/kail piping the output to `sugarjazy` with the `--kail` flag.
  - By default the prefix of the pod/container will be printed unless you specify
    the option `--kail-no-prefix`.
  - The prefix can be customized with `--kail-prefix-format` flag, the default template is :
        `{namespace}/{pod}[{container}]`
        If you want to see only the pod name you can simply do :

        `--kail-prefix-format="[{pod}]"`

  - The `--kail` flags always assume `--stream` implicitely.

### Options

```shell
usage: sugarjazy [-h] [--timeformat TIMEFORMAT]
                 [--regexp-highlight REGEXP_HIGHLIGHT]
                 [--disable-event-colouring] [--filter-level FILTER_LEVEL]
                 [--stream] [--kail] [--kail-no-prefix]
                 [--kail-prefix-format KAIL_PREFIX_FORMAT]
                 [--regexp-color REGEXP_COLOR] [--hide-timestamp]
                 [files ...]

positional arguments:
  files

options:
  -h, --help            show this help message and exit
  --timeformat TIMEFORMAT
                        timeformat default only to the hour:minute:second. Use
                        "%Y-%m-%d %H:%M:%S" if you want to add the year
  --regexp-highlight REGEXP_HIGHLIGHT, -r REGEXP_HIGHLIGHT
                        Highlight a regexp in message, eg: "Failed:\s*\d+,
                        Cancelled\s*\d+"
  --disable-event-colouring
                        By default sugarjazy will try to add a ˃ char with a
                        color to the eventid to easily identify which event
                        belongs to which. Use this option to disable it.
  --filter-level FILTER_LEVEL, -F FILTER_LEVEL
                        filter levels separated by commas, eg: info,debug
  --stream, -s          wait for input stream
  --kail, -k            assume streaming logs from kail
                        (https://github.com/boz/kail)
  --kail-no-prefix      by default kail will print the prefix unless you
                        specify this flag
  --kail-prefix-format KAIL_PREFIX_FORMAT
                        the template of the kail prefix.
  --regexp-color REGEXP_COLOR
                        Regexp highlight color
  --hide-timestamp, -H  don't show timestamp
```

## *`NOTE`*

- Sugarjazy tries hard to identify the same event and add all events on the same colors to the chevron character ().
- The json fields are not standardize. It works well with `knative` based
  controllers like `tekton` or others but that may be buggy for other ones.

## Copyright

[Apache-2.0](./LICENSE)

## Authors

Chmouel Boudjnah <[@chmouel](https://twitter.com/chmouel)>
