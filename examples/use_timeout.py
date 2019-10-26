import requests
from requests import post

def example_one():
    r = requests.get('https://api.github.com/user', timeout=50)

def example_two(url):
    from requests.auth import HTTPBasicAuth
    r = requests.post(url, auth=HTTPBasicAuth('user', 'pass'))

def example_three():
    to = 60
    r = requests.get('https://api.github.com/user', timeout=to)

def example_four(url):
    r = post(url)