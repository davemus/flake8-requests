import requests

def fxn():
    return

fxn()

r = requests.get("http://localhost:8000", allow_redirects=False)
if r.status_code == 301:
    r2 = requests.get("http://localhost:8888")