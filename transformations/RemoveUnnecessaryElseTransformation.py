import ast
import libcst as cst
from .tranformation import Transformation

class IfEndsWithReturnChecker(ast.NodeVisitor):
    """
    AST Visitor to detect `if` statements ending with a `return`.
    """
    def __init__(self):
        self.found = False  # Flag to indicate if the pattern is present

    def visit_If(self, node):
        # Check if the `if` block ends with a `return`
        if node.body and isinstance(node.body[-1], ast.Return):
            self.found = True
        # Continue traversing the AST
        self.generic_visit(node)


class RemoveUnnecessaryElseCSTTransformer(cst.CSTTransformer):
    """
    CST Transformer to remove unnecessary `else` blocks while preserving formatting.
    """
    def leave_If(self, original_node: cst.If, updated_node: cst.If) -> cst.BaseStatement:
        """
        This method is called when the transformer has finished processing an `if` node.
        It checks if the `if` block ends with a `return` statement and has an `else` block.
        If so, it removes the `else` block and appends its body after the `if` statement.
        """
        # Ensure the `if` body is a block
        if isinstance(updated_node.body, cst.IndentedBlock):
            body_statements = updated_node.body.body
            if body_statements:
                last_stmt = body_statements[-1]
                # Check if the last statement in the `if` body is a `return` statement
                if isinstance(last_stmt, cst.SimpleStatementLine) and isinstance(last_stmt.body[0], cst.Return):
                    # Check if there is an `else` block
                    if updated_node.orelse:
                        else_block = updated_node.orelse
                        else_body = else_block.body
                        # Create a new `if` node without the `else` block
                        new_if_node = updated_node.with_changes(orelse=None)
                        # Prepare the list of statements: modified `if` and the `else` body
                        # Convert else_body.body to a list to match types
                        return cst.FlattenSentinel([new_if_node] + list(else_body.body))
        # If conditions are not met, return the node unchanged
        return updated_node


class RemoveUnnecessaryElseTransformation(Transformation):
    """
    Transformation class that removes unnecessary `else` blocks after `if` statements
    that end with a `return`, while preserving the original code's formatting and whitespaces.
    """
    def __init__(self):
        self.transformation_name = "Remove Unnecessary Else Blocks"
        
    def is_applicable(self, code: str) -> bool:
        """
        Checks if any `if` statement ends with a `return` using AST for robust pattern detection.
        """
        try:
            tree = ast.parse(code)
            checker = IfEndsWithReturnChecker()
            checker.visit(tree)
            return checker.found
        except Exception as e:
            print(f"Error during applicability check: {e}")
            return False

    def transform(self, code: str) -> str:
        """
        Transforms the code by removing unnecessary `else` blocks using libcst
        to maintain formatting and whitespaces.
        """
        try:
            # Parse the code into a CST (Concrete Syntax Tree)
            module = cst.parse_module(code)
            # Initialize the CST transformer
            transformer = RemoveUnnecessaryElseCSTTransformer()
            # Apply the transformation
            transformed_module = module.visit(transformer)
            # Return the transformed code as a string
            return transformed_module.code
        except Exception as e:
            print(f"Error during transformation: {e}")
            return code  # Return the original code if an error occurs