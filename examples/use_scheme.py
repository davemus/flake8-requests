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
