import ast
import logging
import sys
from urllib.parse import urlparse
from functools import reduce

from r2c_flake8_requests.requests_base_visitor import RequestsBaseVisitor
from r2c_flake8_requests.constants import VALID_SCHEMES

logger = logging.getLogger(__file__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(stream=sys.stderr)
handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)

class UseScheme(object):
    name = "UseScheme"
    version = "0.0.1"
    code = "R2C703"
    reasoning = "https://stackoverflow.com/questions/15115328/python-requests-no-connection-adapters"

    def __init__(self, tree):
        self.tree = tree

    def run(self):
        visitor = UseSchemeVisitor()
        visitor.visit(self.tree)

        for report in visitor.report_nodes:
            node = report['node']
            urls = report['urls']
            yield (
                node.lineno,
                node.col_offset,
                self._message_for(urls),
                self.name,
            )

    def _message_for(self, urls):
        return f"{self.code} need a scheme (e.g., https://) for one of these possible urls {urls} otherwise requests will throw an exception.  See {self.reasoning}"

class UseSchemeVisitor(RequestsBaseVisitor):

    def __init__(self):
        super(UseSchemeVisitor, self).__init__()

    def _try_parse_url(self, url):
        try:
            parsed = urlparse(url)
            logger.debug(f"Parsed url is: {parsed}")
        except Exception:
            parsed = ""
            logger.debug("Not a parseable URL")
        return parsed

    def _is_valid_scheme(self, parsed_url):
        if parsed_url and parsed_url.scheme in VALID_SCHEMES:
            return True
        return False

    def _see_if_possible_urls_fails_this_check(self, urls):
        return any( [self._is_valid_scheme(url) for url in urls] )

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

    def visit_Call(self, call_node):
        logger.debug(f"Visiting Call node: {ast.dump(call_node)}")
        if not call_node.func:
            logger.debug("Call node func does not exist")
            return

        fxn_name = self._get_function_name(call_node)
        if not self.is_method(call_node, fxn_name):
            logger.debug("Call node is not a requests API call")
            return

        args = call_node.args
        possible_urls = self._get_possible_urls_from_args(args)
        if not possible_urls:
            logger.debug("No possible urls; can't figure out what this is. Calling it good")
            return

        if any( [self._is_valid_scheme(url) for url in possible_urls] ):
            logger.debug("url has a valid scheme, so we're good")
            return

        logger.debug(f"Found this node: {ast.dump(call_node)}")
        self.report_nodes.append({
            "node": call_node,
            "urls": [url.geturl() for url in possible_urls]
        })

if __name__ == "__main__":
    import argparse

    logger.setLevel(logging.DEBUG)

    parser = argparse.ArgumentParser()
    # Add arguments here
    parser.add_argument("inputfile")

    args = parser.parse_args()

    logger.info(f"Parsing {args.inputfile}")
    with open(args.inputfile, 'r') as fin:
        tree = ast.parse(fin.read())

    visitor = UseSchemeVisitor()
    visitor.visit(tree)