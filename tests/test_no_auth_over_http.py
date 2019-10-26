import pytest
import ast
from urllib.parse import urlparse

from r2c_flake8_requests.no_auth_over_http import NoAuthOverHttpVisitor

def test_is_http():
    true_urls = (
        "http://github.com",
        "http://localhost:8000",
        "http://www.github.com/user?name=foo&repo=bar"
    )
    false_urls = (
        "https://github.com",
        "https://www.github.com/user?name=foo&repo=bar",
        "ftp://192.168.1.101",
        None
    )

    visitor = NoAuthOverHttpVisitor()
    assert all([visitor._is_http(urlparse(url)) for url in true_urls])
    assert all([not visitor._is_http(urlparse(url)) for url in false_urls])

def test_basic_visit_call():
    bad_url = "http://github.com"
    code = f"""
import requests
r = requests.get('{bad_url}', auth=('user', 'pass'))
"""

    tree = ast.parse(code)
    visitor = NoAuthOverHttpVisitor()
    visitor.visit(tree)
    assert len(visitor.report_nodes) == 1
    assert len(visitor.report_nodes[0]['urls']) == 1
    assert bad_url in visitor.report_nodes[0]['urls']

def test_no_auth_visit_call():
    bad_url = "http://github.com"
    code = f"""
import requests
r = requests.get('{bad_url}')
"""

    tree = ast.parse(code)
    visitor = NoAuthOverHttpVisitor()
    visitor.visit(tree)
    assert len(visitor.report_nodes) == 0

def test_import_function_visit_call():
    bad_url = "http://github.com"
    code = f"""
from requests import get, post
r = get('{bad_url}', auth=('user', 'pass'))
post('{bad_url}', auth=('user', 'pass'))
"""

    tree = ast.parse(code)
    visitor = NoAuthOverHttpVisitor()
    visitor.visit(tree)
    assert len(visitor.report_nodes) == 2
    assert len(visitor.report_nodes[0]['urls']) == 1
    assert len(visitor.report_nodes[1]['urls']) == 1
    assert bad_url in visitor.report_nodes[0]['urls']
    assert bad_url in visitor.report_nodes[1]['urls']

def test_global_scope_variable_visit_call():
    bad_url = "http://github.com"
    code = f"""
import requests
url = '{bad_url}'
requests.get(url, auth=('user', 'pass'))
"""

    tree = ast.parse(code)
    visitor = NoAuthOverHttpVisitor()
    visitor.visit(tree)
    assert len(visitor.report_nodes) == 1
    assert len(visitor.report_nodes[0]['urls']) == 1
    assert bad_url in visitor.report_nodes[0]['urls']

def test_tuple_assign_visit_call():
    bad_url = "http://github.com"
    code = f"""
import requests
url, _ = '{bad_url}', 0
requests.get(url, auth=('user', 'pass'))
"""

    tree = ast.parse(code)
    visitor = NoAuthOverHttpVisitor()
    visitor.visit(tree)
    assert len(visitor.report_nodes) == 1
    assert len(visitor.report_nodes[0]['urls']) == 1
    assert bad_url in visitor.report_nodes[0]['urls']

# TODO: failing case
def test_list_accessor_visit_call():
    bad_url = "http://github.com"
    code = f"""
import requests
urls = ['{bad_url}']
requests.get(urls[0], auth=('user', 'pass'))
"""

    tree = ast.parse(code)
    visitor = NoAuthOverHttpVisitor()
    visitor.visit(tree)
    assert len(visitor.report_nodes) == 1
    assert len(visitor.report_nodes[0]['urls']) == 1
    assert bad_url in visitor.report_nodes[0]['urls']

# TODO: failing case
def test_dict_accessor_visit_call():
    bad_url = "http://github.com"
    code = f"""
import requests
urls = {{
    'url': '{bad_url}'
}}
requests.get(urls['url'], auth=('user', 'pass'))
"""

    tree = ast.parse(code)
    visitor = NoAuthOverHttpVisitor()
    visitor.visit(tree)
    assert len(visitor.report_nodes) == 1
    assert len(visitor.report_nodes[0]['urls']) == 1
    assert bad_url in visitor.report_nodes[0]['urls']

# TODO: failing case
def test_variable_redef_visit_call():
    good_url = "https://github.com"
    bad_url = "http://github.com"
    code = f"""
import requests
url = '{good_url}'
url = '{bad_url}'

requests.get(url, auth=('user', 'pass'))
"""

    tree = ast.parse(code)
    visitor = NoAuthOverHttpVisitor()
    visitor.visit(tree)
    assert len(visitor.report_nodes) == 1
    assert len(visitor.report_nodes[0]['urls']) == 1
    assert bad_url in visitor.report_nodes[0]['urls']

def test_functiondef_scope_variable_visit_call():
    bad_url = "http://github.com"
    code = f"""
import requests
def fxn():
    url = '{bad_url}'
    requests.get(url, auth=('user', 'pass'))
"""

    tree = ast.parse(code)
    visitor = NoAuthOverHttpVisitor()
    visitor.visit(tree)
    assert len(visitor.report_nodes) == 1
    assert len(visitor.report_nodes[0]['urls']) == 1
    assert bad_url in visitor.report_nodes[0]['urls']

def test_functiondef_scope_variable_multiple_visit_call():
    bad_url = "http://github.com"
    good_url = "https://github.com"
    code = f"""
import requests
def fxn(cond=True):
    if cond:
        endpoint = '{bad_url}'
    else:
        endpoint = '{good_url}'
    requests.get(endpoint, auth=('user', 'pass'))
"""

    tree = ast.parse(code)
    visitor = NoAuthOverHttpVisitor()
    visitor.visit(tree)
    assert len(visitor.report_nodes) == 1
    assert len(visitor.report_nodes[0]['urls']) == 2
    assert bad_url in visitor.report_nodes[0]['urls']
    assert good_url in visitor.report_nodes[0]['urls']

def test_functiondef_scope_variable_unknown_visit_call():
    code = f"""
import requests
def fxn(url):
    requests.get(url, auth=('user', 'pass'))
"""

    tree = ast.parse(code)
    visitor = NoAuthOverHttpVisitor()
    visitor.visit(tree)
    assert len(visitor.report_nodes) == 0

# TODO: failing case
def test_functiondef_scope_variable_loop_visit_call():
    bad_url = "http://github.com"
    good_url = "https://github.com"
    code = f"""
import requests
def fxn():
    urls = ('{bad_url}', '{good_url}')
    for url in urls:
        requests.get(url, auth=('user', 'pass'))
"""

    tree = ast.parse(code)
    visitor = NoAuthOverHttpVisitor()
    visitor.visit(tree)
    assert len(visitor.report_nodes) == 1
    assert len(visitor.report_nodes[0]['urls']) == 2
    assert bad_url in visitor.report_nodes[0]['urls']
    assert good_url in visitor.report_nodes[0]['urls']