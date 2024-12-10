import ast
import re
import astunparse
from .tranformation import Transformation

class ArithmeticOperatorChecker(ast.NodeVisitor):
    """Check for presence of arithmetic operators in code"""
    def __init__(self):
        self.has_operators = False
        self.operators = {'+', '-', '*', '/'}

    def visit_BinOp(self, node):
        if isinstance(node.op, (ast.Add, ast.Sub, ast.Mult, ast.Div)):
            self.has_operators = True
        self.generic_visit(node)

class WhiteSpaceNormalizer(ast.NodeTransformer):
    """AST Transformer to normalize whitespace around operators"""
    def transform_code(self, code: str) -> str:
        patterns = [
            (r'([a-zA-Z0-9_\)])\s*([+\-*/])\s*([a-zA-Z0-9_\(])', r'\1 \2 \3'),
            (r'\s+([+\-*/])\s+', r' \1 ')
        ]
        
        transformed_code = code
        for pattern, replacement in patterns:
            transformed_code = re.sub(pattern, replacement, transformed_code)
        
        return transformed_code

class FixingMissingWhiteSpacesTransformation(Transformation):
    def __init__(self):
        self.transformation_name = "Fixing Missing White Spaces"
        
    def is_applicable(self, code: str) -> bool:
        """Check if code contains arithmetic operators"""
        try:
            tree = ast.parse(code)
            checker = ArithmeticOperatorChecker()
            checker.visit(tree)
            return checker.has_operators
        except Exception as e:
            print(f"Error during applicability check: {e}")
            return False

    def transform(self, code: str) -> str:
        """Transform code to have consistent whitespace around operators"""
        try:
            normalizer = WhiteSpaceNormalizer()
            return normalizer.transform_code(code)
        except Exception as e:
            print(f"Error during transformation: {e}")
            return code