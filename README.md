# 1pass2pass

Utility for transfer items from the 1password (*.1pif files) to the pass ([the standard unix password manager](https://www.passwordstore.org)).

## Usage

```python
python 1pass2pass [-h] [-v] [-p] [-f] [-fl] <1pif filename> <folder>
```

Positional arguments:

```console
<1pif filename>     - path to *.1pif file for processing
<folder>            - path to folder for store passwords
```

Optional arguments:

```console
-h,  --help         - show help message
-v,  --verbose      - increase output verbosity
-p,  --print-only   - print data into console, without saving into password store
-f,  --force        - force overwrite existing passwords (default=False)
-fl, --first-line   - Put password in first line (default=False)
```

> WARN: If you whant to use the `Pass` aplication on iOS, you need to use the `--first-line` option.
> Because the `Pass` app on iOS find the password in the first line.

## Example

```console
python 1pass2pass.py -v -f -fl ~/Downloads/1password.1pif /Personal
```

Where we import passwords from `~/Downloads/1password.1pif` to the folder `/Personal` with verbose output, force overwrite existing passwords and put password in first line.

## Requirements

- python 3.6+
- loguru
