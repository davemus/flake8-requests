
# flake8-requests

flake8-requests is a plugin for flake8 with checks specifically for the [request](https://pypi.org/project/requests/) framework.

## Installation

```
pip install flake8-requests
```

Validate the install using `--version`. flake8-requests adds two plugins, but this will be consolidated in a very near-future version. :)

```
> flake8 --version
3.7.9 (mccabe: 0.6.1, pycodestyle: 2.5.0, pyflakes: 2.1.1, flake8-requests)
```

## List of warnings
- `r2c-requests-no-auth-over-http`: Alerts when `auth` param is possibly used over http://, which could expose credentials. See more documentation at https://checks.bento.dev/en/latest/flake8-requests/r2c-requests-no-auth-over-http/
- `r2c-requests-use-scheme`: Alerts when URLs passed to  `requests` API methods dont have a URL scheme (e.g., https://), otherwise an exception will be thrown. See more documentation at
https://checks.bento.dev/en/latest/flake8-requests/r2c-requests-use-scheme/
