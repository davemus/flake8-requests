import requests
from requests import post

def example_one():
    requests.get('https://api.github.com/user', timeout=50)

def example_two(url):
    from requests.auth import HTTPBasicAuth
    requests.post(url, auth=HTTPBasicAuth('user', 'pass'))

def example_three():
    to = 60
    requests.get('https://api.github.com/user', timeout=to)

def example_four(url):
    post(url)