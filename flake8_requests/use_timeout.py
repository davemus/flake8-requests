import ast
import logging
import sys

from flake8_requests.requests_base_visitor import RequestsBaseVisitor
from flake8_requests import __version__
logger = logging.getLogger(__file__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(stream=sys.stderr)
handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)

class UseTimeoutVisitor(RequestsBaseVisitor):
    name = "r2c-requests-use-timeout"

    def visit_Call(self, call_node):
        logger.debug(f"Visiting Call node: {ast.dump(call_node)}")
        if not call_node.func:
            logger.debug("Call node func does not exist")
            return

        fxn_name = self._get_function_name(call_node)
        logger.debug(f"Found function name: {fxn_name}")
        if not self.is_method(call_node, fxn_name):
            logger.debug("Call node is not a requests API call")
            return

        keywords = call_node.keywords
        if any([kw.arg == "timeout" for kw in keywords]):
            logger.debug("requests call has the 'timeout' keyword, so we're good")
            return

        logger.debug(f"Found this node: {ast.dump(call_node)}")
        self.report_nodes.append({
            "node": call_node,
            "message": f"{self.name} requests will hang forever without a timeout. Consider adding a timeout (recommended 10 sec)."
        })