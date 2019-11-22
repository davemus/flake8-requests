def example_one():
    params = {
        "hello", "world"
    }
    # Bad
    requests.get("api.github.com/users", params=params, timeout=60)

def example_two():
    url = "api.github.com/users"
    requests.get(url, timeout=60)


def example_three(b=True):
    if b:
        url = "api.github.com/users"
    else:
        url = "https://api.github.com/users"
    requests.get(url, timeout=50)

def example_four():
    params = {
        "hello", "world"
    }
    # Good
    requests.get("https://api.github.com/users", params=params, timeout=60)

def example_five():
    requests.get("HTTPS://api.github.com/users", params=params, timeout=60)

class Example(object):
    def example_six(self, message, chat_id):
        url = self.base_url + "sendMessage?text={}&chat_id={}".format(message, chat_id)
        response = requests.get(url)
        content = response.content.decode("utf8")
        return content


import requests
requests.get("http://github.com")
requests.get("http://localhost:8000")
requests.get("http://www.github.com/user?name=foo&repo=bar")
requests.get("https://github.com")
requests.get("https://www.github.com/user?name=foo&repo=bar")
requests.get("ftp://192.168.1.101")
requests.get("ws://192.168.1.101")
requests.get("file:///Users/user/secrets.txt")


r = requests.request("GET", "github.com")
r = requests.request("POST", "notavalidscheme://www.github.com/user?name=foo&repo=bar")

