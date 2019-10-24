import ast
from urllib.parse import urlparse

import logging
import sys

logger = logging.getLogger(__file__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(stream=sys.stderr)
handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)

http_verbs = (
    "get",
    "post",
    "option",
    "head",
    "put",
    "delete",
    "request"
)

class NoAuthOverHttp(object):
    name = "NoAuthOverHttp"
    version = "0.0.1"
    code = "R2C701"

    def __init__(self, tree):
        self.tree = tree

    def run(self):
        visitor = NoAuthOverHttpVisitor()
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
        return f"{self.code} auth used over http: {url}"

class NoAuthOverHttpVisitor(ast.NodeVisitor):
    def __init__(self):
        self.report_nodes = []
        self.symbol_table = {}
        self._set_scope("global")

    def _symbol_lookup(self, symbol):
        logger.debug(f"Symbol table: {self.symbol_table}")

        try:
            val = self.symbol_table[self.scope][symbol]
        except KeyError:
            logger.debug(f"{symbol} not in scope[{self.scope}] symbol table. Case not handled yet")
            return None

        if isinstance(val, ast.Name):
            val = self._symbol_lookup(val.id)
        return val

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


    def _is_http(self, parsed_url):
        if parsed_url and parsed_url.scheme == "http":
            return True
        return False

    def _set_scope(self, scope):
        self.scope = scope
        self.symbol_table[self.scope] = {}

    def _set_symbol(self, symbol, value):
        self.symbol_table[self.scope][symbol] = value

    def visit_FunctionDef(self, def_node):
        self._set_scope(def_node.name)
        for node in def_node.body:
            self.visit(node)

    def visit_AsyncFunctionDef(self, def_node):
        self.visit_FunctionDef(def_node)

    def visit_ClassDef(self, class_node):
        self._set_scope(class_node.name)
        for node in class_node.body:
            self.visit(node)

    def visit_Assign(self, assign_node):
        target = assign_node.targets[0]
        logger.debug(f"Visiting Assign node: {ast.dump(assign_node)}")
        if isinstance(target, ast.Name):
            if isinstance(target.ctx, ast.Store):
                self._set_symbol(target.id, assign_node.value)
        elif isinstance(target, ast.Tuple):
            if isinstance(target.ctx, ast.Store):
                for i, elem in enumerate(target.elts):
                    self._set_symbol(elem.id, assign_node.value.elts[i])

    def visit_Call(self, call_node):
        logger.debug(f"Visiting Call node: {ast.dump(call_node)}")
        if not call_node.func:
            logger.debug("Call node func does not exist")
            return

        if not isinstance(call_node.func, ast.Attribute):
            logger.debug("Call node func is not an ast.Attribute")
            return

        attribute = call_node.func

        if not attribute.value.id == "requests" and not attribute.attr in http_verbs:
            logger.debug("Call node is not a requests API call")
            return

        if not call_node.keywords:
            logger.debug("No keywords on Call node")
            return

        keywords = call_node.keywords
        if not any([kw.arg == "auth" for kw in keywords]):
            logger.debug("requests call does not contain the 'auth' keyword")
            return

        if not call_node.args:
            logger.debug("No args on Call node")
            return

        args = call_node.args
        url = self._parse_url(call_node.args)
        if not self._is_http(url):
            logger.debug("url is not http, so it's fine")
            return

        logger.debug(f"Found this node: {ast.dump(call_node)}")
        self.report_nodes.append({
            "node": call_node,
            "url": url.geturl()
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

    visitor = NoAuthOverHttpVisitor()
    visitor.visit(tree)