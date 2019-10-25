import requests

def example_one():
    requests.get('http://api.github.com/user', auth=('user', 'pass'), timeout=10)

def example_two(url):
    from requests.auth import HTTPBasicAuth
    requests.post(url, auth=HTTPBasicAuth('user', 'pass'), timeout=60)

example_two('http://api.github.com/user')

def example_three():
    from requests.auth import HTTPDigestAuth
    url = 'http://httpbin.org/digest-auth/auth/user/pass'
    requests.get(url, auth=HTTPDigestAuth('user', 'pass'), timeout=60)

def example_four():
    class MyAuth(requests.auth.AuthBase):
        def __call__(self, r):
            return r

    url = 'http://httpbin.org/get'
    requests.get(url, auth=MyAuth(), timeout=50)

def example_five(a=True):
    if a:
        url = "https://github.com"
    else:
        url = "http://github.com"
    requests.get(url, auth=('user', 'pass'), timeout=50)

def example_six(a=True):
    if a:
        url = "http://pastebin.com"
        requests.get(url, auth=('user', 'pass'), timeout=50)

def example_seven():
    urls = [
        "http://bing.com",
        "http://google.com"
    ]

    for url in urls:
        requests.get(url, auth=('user', 'pass'), timeout=10)