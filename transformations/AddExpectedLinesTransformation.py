import ast
from .tranformation import Transformation

class FunctionNotLastChecker(ast.NodeVisitor):
    """
    AST Visitor to check if any function definition is not the last node in the module.
    """
    def __init__(self):
        self.found = False  # Flag to indicate if such a function exists

    def visit_Module(self, node):
        # Check if the last node is a function definition
        if node.body:
            last_index = len(node.body) - 1
            for index, stmt in enumerate(node.body):
                if isinstance(stmt, ast.FunctionDef) and index != last_index:
                    self.found = True
                    break  # No need to continue after finding one
        self.generic_visit(node)

class AddBlankLineAfterFunctionTransformer(ast.NodeTransformer):
    """
    AST Transformer to add a blank line after function definitions if none exists.
    """
    def __init__(self, source_lines):
        self.source_lines = source_lines

    def visit_Module(self, node):
        # Collect line numbers where blank lines need to be inserted
        insertion_lines = []

        for index, stmt in enumerate(node.body):
            if isinstance(stmt, ast.FunctionDef) and index != len(node.body) - 1:
                # Use stmt.end_lineno to get the last line of the function definition
                end_line = stmt.end_lineno  # AST line numbers are 1-based

                # Ensure we don't go out of bounds
                if end_line < len(self.source_lines):
                    next_line = self.source_lines[end_line].strip()
                    if next_line:  # If the next line is not blank
                        insertion_lines.append(end_line)

        # Insert blank lines in reverse order to prevent index shifting
        for line_no in reversed(insertion_lines):
            self.source_lines.insert(line_no, "")

        return node

class AddExpectedLinesTransformation(Transformation):
    def __init__(self):
        self.transformation_name = "AddExpectedLinesTransformation"
    def is_applicable(self, code: str) -> bool:
        """
        Checks if any function definition is not the last node in the module.
        """
        try:
            tree = ast.parse(code)
            checker = FunctionNotLastChecker()
            checker.visit(tree)
            return checker.found
        except Exception:
            return False

    def transform(self, code: str) -> str:
        """
        Transforms the code by adding a blank line after function bodies if none exists.
        """
        try:
            source_lines = code.splitlines()
            tree = ast.parse(code)

            transformer = AddBlankLineAfterFunctionTransformer(source_lines)
            transformer.visit(tree)

            return "\n".join(source_lines)
        except Exception:
            return code  # Return the original code if an error occurs