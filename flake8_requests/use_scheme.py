import ast
import logging
import sys
from urllib.parse import urlparse
from functools import reduce

from flake8_requests.requests_base_visitor import RequestsBaseVisitor
from flake8_requests.constants import VALID_SCHEMES
from flake8_requests import __version__
logger = logging.getLogger(__file__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(stream=sys.stderr)
handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)

class UseSchemeVisitor(RequestsBaseVisitor):
    name = "r2c-requests-use-scheme"
    reasoning = "https://stackoverflow.com/questions/15115328/python-requests-no-connection-adapters"

    def __init__(self):
        super(UseSchemeVisitor, self).__init__()

    def _is_valid_scheme(self, parsed_url):
        if parsed_url and parsed_url.scheme in VALID_SCHEMES:
            return True
        return False

    def _see_if_possible_urls_fails_this_check(self, urls):
        return any( [self._is_valid_scheme(url) for url in urls] )

    def visit_Call(self, call_node):
        logger.debug(f"Visiting Call node: {ast.dump(call_node)}")
        if not call_node.func:
            logger.debug("Call node func does not exist")
            return

        fxn_name = self._get_function_name(call_node)
        if not self.is_method(call_node, fxn_name):
            logger.debug("Call node is not a requests API call")
            return

        url_arg = self._get_url_arg(call_node, fxn_name)
        possible_urls = self._get_possible_urls_from_arg(url_arg)
        logger.debug(f"possible_urls: {possible_urls}")
        if not possible_urls:
            logger.debug("No possible urls; can't figure out what this is. Calling it good")
            return

        if any( [self._is_valid_scheme(url) for url in possible_urls] ):
            logger.debug("url has a valid scheme, so we're good")
            return

        logger.debug(f"Found this node: {ast.dump(call_node)}")
        urls = [url.geturl() for url in possible_urls]
        self.report_nodes.append({
            "node": call_node,
            "urls": urls,
            "message": f"{self.name} need a scheme (e.g., https://) for one of these possible urls {urls}. Otherwise requests will throw an exception.  See {self.reasoning}"
        })