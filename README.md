
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
- R2C701="flake8_requests.no_auth_over_http:NoAuthOverHttp"
- R2C702="flake8_requests.use_timeout:UseTimeout"
- R2C703="flake8_requests.use_scheme:UseScheme"
