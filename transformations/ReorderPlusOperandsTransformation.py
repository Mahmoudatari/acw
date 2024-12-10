import ast
import libcst as cst
import hashlib
from .tranformation import Transformation

class PlusOperationChecker(ast.NodeVisitor):
    def __init__(self):
        self.found = False

    def visit_BinOp(self, node):
        if isinstance(node.op, ast.Add):
            if node.left is not None and node.right is not None:
                self.found = True
        self.generic_visit(node)

class ReorderPlusOperandsTransformer(cst.CSTTransformer):
    def leave_BinaryOperation(
        self, 
        original_node: cst.BinaryOperation, 
        updated_node: cst.BinaryOperation
    ) -> cst.BinaryOperation:
        if isinstance(original_node.operator, cst.Add):
            left_code = cst.Module([cst.Expr(original_node.left)]).code
            right_code = cst.Module([cst.Expr(original_node.right)]).code
            
            left_hash = hashlib.sha256(left_code.encode('utf-8')).hexdigest()
            right_hash = hashlib.sha256(right_code.encode('utf-8')).hexdigest()
            
            if left_hash < right_hash:
                return updated_node.with_changes(
                    left=original_node.right,
                    right=original_node.left
                )
        return updated_node

class ReorderPlusOperandsTransformation(Transformation):
    def __init__(self):
        self.transformation_name = "Reorder Plus Operands"
    def is_applicable(self, code: str) -> bool:
        try:
            tree = ast.parse(code)
            checker = PlusOperationChecker()
            checker.visit(tree)
            return checker.found
        except Exception as e:
            print(f"Error during applicability check: {e}")
            return False

    def transform(self, code: str) -> str:
        try:
            source_tree = cst.parse_module(code)
            transformer = ReorderPlusOperandsTransformer()
            transformed_tree = source_tree.visit(transformer)
            return transformed_tree.code
        except Exception as e:
            print(f"Error during transformation: {e}")
            return code