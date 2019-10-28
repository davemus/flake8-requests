import pytest
import ast
from urllib.parse import urlparse

from r2c_flake8_requests.use_scheme import UseSchemeVisitor

def test_is_valid_scheme():
    true_urls = (
        "http://github.com",
        "http://localhost:8000",
        "http://www.github.com/user?name=foo&repo=bar",
        "https://github.com",
        "https://www.github.com/user?name=foo&repo=bar",
        "ftp://192.168.1.101",
        "ws://192.168.1.101",
        "file:///Users/user/secrets.txt"
    )
    false_urls = (
        "github.com",
        "notavalidscheme://www.github.com/user?name=foo&repo=bar",
        None
    )

    visitor = UseSchemeVisitor()
    assert all([visitor._is_valid_scheme(urlparse(url)) for url in true_urls])
    assert all([not visitor._is_valid_scheme(urlparse(url)) for url in false_urls])

def test_basic_visit_call():
    bad_url = "github.com"
    code = f"""
import requests
requests.get('{bad_url}', auth=('user', 'pass'))
"""

    tree = ast.parse(code)
    visitor = UseSchemeVisitor()
    visitor.visit(tree)
    assert len(visitor.report_nodes) == 1
    assert len(visitor.report_nodes[0]['urls']) == 1
    assert bad_url in visitor.report_nodes[0]['urls']

def test_valid_scheme_visit_call():
    bad_url = "http://github.com"
    code = f"""
import requests
requests.get('{bad_url}')
"""

    tree = ast.parse(code)
    visitor = UseSchemeVisitor()
    visitor.visit(tree)
    assert len(visitor.report_nodes) == 0

def test_unresolvable_variable():
    code = """
def send_message(self, message, chat_id):
    url = self.base_url + "sendMessage?text={}&chat_id={}".format(message, chat_id)
    response = requests.get(url)
    content = response.content.decode("utf8")
    return content
"""

    tree = ast.parse(code)
    visitor = UseSchemeVisitor()
    visitor.visit(tree)
    assert len(visitor.report_nodes) == 0

def test_none_case():
    code = """
url = None
response = requests.get(url, timeout=20)
content = response.content.decode("utf8")
"""

    tree = ast.parse(code)
    visitor = UseSchemeVisitor()
    visitor.visit(tree)
    assert len(visitor.report_nodes) == 0

def test_request_case():
    bad_url = "api.github.com/user"
    code = f"""
url = "{bad_url}"
r = requests.request("GET", url, timeout=10)
data = r.json()
"""

    tree = ast.parse(code)
    visitor = UseSchemeVisitor()
    visitor.visit(tree)
    assert len(visitor.report_nodes) == 1
    assert len(visitor.report_nodes[0]['urls']) == 1
    assert bad_url in visitor.report_nodes[0]['urls']

# TODO: failure case
def test_dot_format_case():
    code = """
def check_image_evaluation(self, image, show_history=False, detail=False, tag=None, policy=None):
    itype, _, image_digest = self._discover_inputimage(image)
    if not image_digest:
        return [False, "could not get image record from anchore"]
    if not tag and itype != 'tag':
        return [False, "input image name is not a tag, and no --tag is specified"]

    thetag = tag if tag else image

    url = "{base_url}/api/scanning/v1/anchore/images/{image_digest}/check?history={history}&detail={detail}&tag={tag}{policy_id}"
    url = url.format(
        base_url=self.url,
        image_digest=image_digest,
        history=str(show_history).lower(),
        detail=str(detail).lower(),
        tag=thetag,
        policy_id=("&policyId=%s" % policy) if policy else "")

    res = requests.get(url, headers=self.hdrs, verify=self.ssl_verify)
    if not self._checkResponse(res):
        return [False, self.lasterr]

    return [True, res.json()]
"""
    tree = ast.parse(code)
    visitor = UseSchemeVisitor()
    visitor.visit(tree)
    assert len(visitor.report_nodes) == 0