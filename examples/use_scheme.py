def example_one():
    params = {
        "hello", "world"
    }
    # Bad
    requests.get("api.github.com/users", params=params)

def example_two():
    url = "api.github.com/users"
    requests.get(url)


def example_three(b=True):
    if b:
        url = "api.github.com/users"
    else:
        url = "https://api.github.com/users"
    requests.get(url)

def example_four():
    params = {
        "hello", "world"
    }
    # Good
    requests.get("https://api.github.com/users", params=params)