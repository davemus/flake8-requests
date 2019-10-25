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