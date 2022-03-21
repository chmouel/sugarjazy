# sugarjazy - parse json logs nicely

sugarjazy is a simple tool to parse json logs and output them in a nice format with nice colors.

Usually play nicely with <https://github.com/uber-go/zap> when using the ["Sugar"](https://pkg.go.dev/go.uber.org/zap#Logger.Sugar) log.

## Installation

There is not many dependencies on this package but [`python-dateutil`](https://dateutil.readthedocs.io/en/stable/) is an optional dependency, if the package is not installed you will not be be able to show the log timestamps.

### Arch

You can install it [from aur](https://aur.archlinux.org/packages/sugarjazy) with your aurhelper, like yay :

```
yay -S sugarjazy
```

### pip

With pip from pypi - <https://pypi.org/project/sugarjaz/>

```
pip install --user sugarjazy
```

(make sure $HOME/.local/bin is in your PATH)

## Screenshot

![screenshot](./.github/screenshot.png)

## Usage

You can simply pipe your logs vai `kubectl logs podname|sugarjazy` or specify a log file.

```shell
% poetry run sugarjazy --help
usage: sugarjazy [-h] [--timeformat TIMEFORMAT] [--regexp-highlight REGEXP_HIGHLIGHT] [--disable-event-colouring] [--regexp-color REGEXP_COLOR] [--hide-timestamp] [files ...]

positional arguments:
  files

options:
  -h, --help            show this help message and exit
  --timeformat TIMEFORMAT
                        timeformat default only to the hour minute. Use "%Y-%m-%d %H:%M:%S" if you want to add the year
  --regexp-highlight REGEXP_HIGHLIGHT, -r REGEXP_HIGHLIGHT
                        Highlight a regexp in message, for example: \"Failed:\s*\d+, Cancelled\s*\d+\"
  --disable-event-colouring
                        Add a  with a color to the eventid to easily identify which event belongs to which
  --regexp-color REGEXP_COLOR
                        Regexp highlight color
  --hide-timestamp, -H  don't show timestamp
  ```

Sugarjazy try to identify the same event and add all events on the same colors to the chevron character ().

## Copyright

[Apache-2.0](./LICENSE)

## Authors

Chmouel Boudjnah <[@chmouel](https://twitter.com/chmouel)>
