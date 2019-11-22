import pytest
import ast
from urllib.parse import urlparse

from flake8_requests.use_timeout import UseTimeoutVisitor

## True positive
@pytest.mark.true_positive
def test_basic_visit_call():
    url = "https://github.com"
    code = f"""
import requests
requests.get('{url}')
"""

    tree = ast.parse(code)
    visitor = UseTimeoutVisitor()
    visitor.visit(tree)
    assert len(visitor.report_nodes) == 1

@pytest.mark.true_positive
def test_import_function_visit_call():
    url = "https://github.com"
    code = f"""
from requests import get, post
get('{url}', timeout=3)
post('{url}')
"""

    tree = ast.parse(code)
    visitor = UseTimeoutVisitor()
    visitor.visit(tree)
    assert len(visitor.report_nodes) == 1
    assert visitor.report_nodes[0]['node'].lineno == 4

## True negative
@pytest.mark.true_negative
def test_with_timeout_visit_call():
    url = "https://github.com"
    code = f"""
import requests
requests.get('{url}', timeout=50)
"""

    tree = ast.parse(code)
    visitor = UseTimeoutVisitor()
    visitor.visit(tree)
    assert len(visitor.report_nodes) == 0