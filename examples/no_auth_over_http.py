import requests

def example_one():
    requests.get('http://api.github.com/user', auth=('user', 'pass'))

def example_two(url):
    from requests.auth import HTTPBasicAuth
    requests.post(url, auth=HTTPBasicAuth('user', 'pass'))

example_two('http://api.github.com/user')

def example_three():
    from requests.auth import HTTPDigestAuth
    url = 'http://httpbin.org/digest-auth/auth/user/pass'
    requests.get(url, auth=HTTPDigestAuth('user', 'pass'))

def example_four():
    class MyAuth(requests.auth.AuthBase):
        def __call__(self, r):
            return r

    url = 'http://httpbin.org/get'
    requests.get(url, auth=MyAuth())