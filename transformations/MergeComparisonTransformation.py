import ast
from .tranformation import Transformation

class MergeComparisonChecker(ast.NodeVisitor):
    def __init__(self):
        self.is_applicable = False

    def visit_If(self, node):
        # Check for OR conditions with equality comparisons
        if isinstance(node.test, ast.BoolOp) and isinstance(node.test.op, ast.Or):
            operands = node.test.values
            if all(isinstance(op, ast.Compare) and 
                  len(op.ops) == 1 and 
                  isinstance(op.ops[0], ast.Eq) 
                  for op in operands):
                variables = {op.left.id for op in operands 
                           if isinstance(op.left, ast.Name)}
                if len(variables) == 1:
                    self.is_applicable = True
                    return

        # Check for existing in operator with tuple
        if (isinstance(node.test, ast.Compare) and 
            len(node.test.ops) == 1 and 
            isinstance(node.test.ops[0], ast.In) and
            isinstance(node.test.left, ast.Name) and
            isinstance(node.test.comparators[0], ast.Tuple)):
            self.is_applicable = True
            return

        self.generic_visit(node)

class MergeComparisonTransformer(ast.NodeTransformer):
    def visit_If(self, node):
        # Only transform OR conditions, skip existing 'in' statements
        if isinstance(node.test, ast.Compare) and isinstance(node.test.ops[0], ast.In):
            return node

        if not (isinstance(node.test, ast.BoolOp) and isinstance(node.test.op, ast.Or)):
            return node

        operands = node.test.values
        if not all(isinstance(op, ast.Compare) and 
                  len(op.ops) == 1 and 
                  isinstance(op.ops[0], ast.Eq) 
                  for op in operands):
            return node

        first_compare = operands[0]
        if not isinstance(first_compare.left, ast.Name):
            return node

        variable = first_compare.left
        values = []
        
        for op in operands:
            if not (isinstance(op.left, ast.Name) and op.left.id == variable.id):
                return node
            values.append(op.comparators[0])

        new_test = ast.Compare(
            left=variable,
            ops=[ast.In()],
            comparators=[ast.Tuple(elts=values, ctx=ast.Load())]
        )

        return ast.If(
            test=new_test,
            body=node.body,
            orelse=node.orelse
        )

class MergeComparisonTransformation(Transformation):
    def __init__(self):
        self.checker = MergeComparisonChecker()
        self.transformation_name = "Merge Multiple Equality Comparisons"

    def is_applicable(self, code: str) -> bool:
        try:
            tree = ast.parse(code)
            self.checker.visit(tree)
            return self.checker.is_applicable
        except SyntaxError:
            return False

    def transform(self, code: str) -> str:
        try:
            tree = ast.parse(code)
            transformer = MergeComparisonTransformer()
            modified_tree = transformer.visit(tree)
            ast.fix_missing_locations(modified_tree)
            return ast.unparse(modified_tree)
        except Exception as e:
            print(f"Transform error: {e}")
            return code

    def __str__(self):
        return "Merge Multiple Equality Comparisons"