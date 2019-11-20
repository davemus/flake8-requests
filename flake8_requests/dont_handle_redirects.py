import ast
import logging
import sys

from flake8_requests.requests_base_visitor import RequestsBaseVisitor

logger = logging.getLogger(__file__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(stream=sys.stderr)
handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)

class DontHandleRedirects(object):
    name = "DontHandleRedirects"
    version = "0.0.1"
    code = "R2C704"
    reasoning = "https://cve.mitre.org/cgi-bin/cvename.cgi?name=2018-18074"

    def __init__(self, tree):
        self.tree = tree

    def run(self):
        visitor = DontHandleRedirectsVisitor()
        visitor.visit(self.tree)

        for report in visitor.report_nodes:
            node = report['node']
            yield (
                node.lineno,
                node.col_offset,
                self._message_for(),
                self.name,
            )

    def _message_for(self):
        return f"{self.code} let requests handle redirects for you to avoid inadvertently exposing sensitive data to other servers. See {self.reasoning}"

class DontHandleRedirectsVisitor(RequestsBaseVisitor):

    def __init__(self):
        super(DontHandleRedirectsVisitor, self).__init__()
        self.dont_handle_scopes = []

    def visit_Call(self, call_node):
        logger.debug("Visiting Call node")
        fxn_name = self._get_function_name(call_node)
        if not self.is_method(call_node, fxn_name):
            logger.debug("Call node is not a requests API call")
            return

        logger.debug(f"Setting scope to not handle redirects: {self.scope}")
        self.dont_handle_scopes.append(self.scope)

    def visit_Compare(self, compare_node):
        logger.debug("Visiting Compare node")
        if compare_node.left.attr != "status_code":
            logger.debug("Not checking result of status_code")
            return

        if not isinstance(compare_node.ops[0], ast.Eq):
            logger.debug("Op is not ==")
            return

        if not any( [(num.n == 301 or num.n == 302) for num in compare_node.comparators] ):
            logger.debug("Not checking a redirect, don't care")
            return

        logger.debug(f"Found this node: {ast.dump(compare_node)}")
        self.report_nodes.append({
            "node": compare_node,
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

    visitor = DontHandleRedirectsVisitor()
    visitor.visit(tree)
