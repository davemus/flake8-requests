import ast
import logging
import sys
from urllib.parse import urlparse
from functools import reduce

from r2c_flake8_requests.dumb_scope_visitor import DumbScopeVisitor
from r2c_flake8_requests.import_aliasing import MethodVisitor
from r2c_flake8_requests.constants import REQUESTS_API_HTTP_VERBS, REQUESTS_API_TOP_LEVEL

logger = logging.getLogger(__file__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(stream=sys.stderr)
handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)

class RequestsBaseVisitor(DumbScopeVisitor):

    def __init__(self):
        super(RequestsBaseVisitor, self).__init__()

    def _try_parse_url(self, url):
        try:
            parsed = urlparse(url)
            logger.debug(f"Parsed url is: {parsed}")
        except Exception:
            parsed = ""
            logger.debug("Not a parseable URL")
        return parsed

    def _get_possible_urls_from_arg(self, arg):
        if isinstance(arg, ast.Name):
            possible_values = self._get_possible_symbol_values(arg.id)
            urls = [self._try_parse_url(value) for value in possible_values]
        elif isinstance(arg, ast.Str):
            urls = [self._try_parse_url(arg.s)]
        urls = list(filter(lambda url: url, urls))
        return urls

    def _get_possible_urls_from_args(self, args):
        urls = [self._get_possible_urls_from_arg(arg) for arg in args]
        urls = list(reduce(lambda x, y: x + y, urls))
        return urls

    def _get_function_name(self, call_node):
        func = call_node.func
        if isinstance(func, ast.Attribute):
            return func.attr
        elif isinstance(func, ast.Name):
            return func.id

    def _get_url_arg(self, call_node, function_name):
        if function_name in REQUESTS_API_HTTP_VERBS:
            # From requests/api.py L64:  def get(url, params=None, **kwargs):
            return call_node.args[0]
        elif function_name in REQUESTS_API_TOP_LEVEL:
            # From requests/api.py L16:  def request(method, url, **kwargs):
            return call_node.args[1]
    