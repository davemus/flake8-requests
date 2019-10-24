import ast
import logging
import sys
from urllib.parse import urlparse

from .dumb_scope_visitor import DumbScopeVisitor
from .constants import HTTP_VERBS, VALID_SCHEMES

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
            url = report['url']
            yield (
                node.lineno,
                node.col_offset,
                self._message_for(url),
                self.name,
            )

    def _message_for(self, url):
        return f"{self.code} need a scheme (e.g., https://) for url [{url}] otherwise requests will throw an exception.  See {self.reasoning}"

class UseSchemeVisitor(DumbScopeVisitor):

    def _parse_url(self, args):
        for arg in args:
            if isinstance(arg, ast.Str):
                try:
                    parsed = urlparse(arg.s)
                    logger.debug(f"Parsed url is: {parsed}")
                except Exception:
                    parsed = None
                    logger.debug("Not a parseable URL")
                return parsed
            elif isinstance(arg, ast.Name):
                # Look up in symbol table
                val = self._symbol_lookup(arg.id)
                return self._parse_url([val])

    def _is_valid_scheme(self, parsed_url):
        if parsed_url and parsed_url.scheme in VALID_SCHEMES:
            return True
        return False

    def visit_Call(self, call_node):
        logger.debug(f"Visiting Call node: {ast.dump(call_node)}")
        if not call_node.func:
            logger.debug("Call node func does not exist")
            return

        if not isinstance(call_node.func, ast.Attribute):
            logger.debug("Call node func is not an ast.Attribute")
            return

        attribute = call_node.func

        if not attribute.value.id == "requests" and not attribute.attr in HTTP_VERBS:
            logger.debug("Call node is not a requests API call")
            return

        args = call_node.args
        url = self._parse_url(call_node.args)
        if self._is_valid_scheme(url):
            logger.debug("url has a valid scheme, so it's cool")
            return

        # This is bad, I know.  Please forgive me.......
        if url:
            url = url.geturl()

        logger.debug(f"Found this node: {ast.dump(call_node)}")
        self.report_nodes.append({
            "node": call_node,
            "url": url
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