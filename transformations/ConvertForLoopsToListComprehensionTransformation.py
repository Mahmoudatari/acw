import ast
import astunparse
from .tranformation import Transformation
import libcst as cst

class ForToListComprehensionChecker(ast.NodeVisitor):
    """
    AST Visitor to detect for-loops that can be converted to list comprehensions
    or list comprehensions matching the transformation pattern.
    """
    def __init__(self):
        self.is_applicable = False

    def visit_For(self, node):
        if len(node.body) == 1:
            stmt = node.body[0]
            
            # Case 1: Simple for loop with append
            if isinstance(stmt, ast.Expr) and self._is_append_call(stmt.value):
                self.is_applicable = True
                return
            
            # Case 2 & 3: For loop with if or if-else
            if isinstance(stmt, ast.If):
                if_body_valid = (len(stmt.body) == 1 and 
                               isinstance(stmt.body[0], ast.Expr) and 
                               self._is_append_call(stmt.body[0].value))
                
                # Case 2: If without else
                if not stmt.orelse and if_body_valid:
                    self.is_applicable = True
                    return
                
                # Case 3: If-else with both append
                if stmt.orelse:
                    else_body_valid = (len(stmt.orelse) == 1 and 
                                     isinstance(stmt.orelse[0], ast.Expr) and 
                                     self._is_append_call(stmt.orelse[0].value))
                    if if_body_valid and else_body_valid:
                        self.is_applicable = True
                        return
        
        self.generic_visit(node)

    def visit_Assign(self, node):
        if (len(node.targets) == 1 and 
            isinstance(node.targets[0], ast.Name) and
            isinstance(node.value, ast.ListComp)):
            self.is_applicable = True
        self.generic_visit(node)

    def _is_append_call(self, expr):
        return (isinstance(expr, ast.Call) and 
                isinstance(expr.func, ast.Attribute) and
                expr.func.attr == "append" and 
                isinstance(expr.func.value, ast.Name))

class ForToListComprehensionTransformer(ast.NodeTransformer):
    """
    AST Transformer to convert for-loops appending to a list into list comprehensions.
    """
    def visit_For(self, node):
        if len(node.body) != 1:
            return self.generic_visit(node)
        
        stmt = node.body[0]
        
        # Case 1: Simple for loop with append
        if isinstance(stmt, ast.Expr) and self._is_append_call(stmt.value):
            return self._create_simple_list_comp(node, stmt.value)
        
        # Case 2: For loop with if (no else)
        if isinstance(stmt, ast.If) and not stmt.orelse:
            if_body = stmt.body[0] if len(stmt.body) == 1 else None
            if isinstance(if_body, ast.Expr) and self._is_append_call(if_body.value):
                return self._create_if_only_list_comp(
                    node, if_body.value, stmt.test
                )
        
        # Case 3: For loop with if-else
        if isinstance(stmt, ast.If):
            if_body = stmt.body[0] if len(stmt.body) == 1 else None
            else_body = stmt.orelse[0] if len(stmt.orelse) == 1 else None
            
            if (isinstance(if_body, ast.Expr) and self._is_append_call(if_body.value) and
                isinstance(else_body, ast.Expr) and self._is_append_call(else_body.value)):
                return self._create_conditional_list_comp(
                    node, if_body.value, else_body.value, stmt.test
                )
        
        return self.generic_visit(node)
    
    def _is_append_call(self, expr):
        return (isinstance(expr, ast.Call) and 
                isinstance(expr.func, ast.Attribute) and
                expr.func.attr == "append" and 
                isinstance(expr.func.value, ast.Name))

    def _create_simple_list_comp(self, for_node, append_call):
        list_name = append_call.func.value.id
        elt = append_call.args[0]
        generators = [
            ast.comprehension(
                target=for_node.target,
                iter=for_node.iter,
                ifs=[],
                is_async=0
            )
        ]
        list_comp = ast.ListComp(elt=elt, generators=generators)
        return ast.Assign(targets=[ast.Name(id=list_name, ctx=ast.Store())], value=list_comp)

    def _create_if_only_list_comp(self, for_node, append_call, test):
        list_name = append_call.func.value.id
        elt = append_call.args[0]
        generators = [
            ast.comprehension(
                target=for_node.target,
                iter=for_node.iter,
                ifs=[test],
                is_async=0
            )
        ]
        list_comp = ast.ListComp(elt=elt, generators=generators)
        return ast.Assign(targets=[ast.Name(id=list_name, ctx=ast.Store())], value=list_comp)

    def _create_conditional_list_comp(self, for_node, if_append, else_append, test):
        list_name = if_append.func.value.id
        if_value = if_append.args[0]
        else_value = else_append.args[0]
        
        elt = ast.IfExp(
            test=test,
            body=if_value,
            orelse=else_value
        )
        
        generators = [
            ast.comprehension(
                target=for_node.target,
                iter=for_node.iter,
                ifs=[],
                is_async=0
            )
        ]
        
        list_comp = ast.ListComp(elt=elt, generators=generators)
        return ast.Assign(targets=[ast.Name(id=list_name, ctx=ast.Store())], value=list_comp)


class ConvertForLoopsToListComprehensionTransformation(Transformation):
    def __init__(self):
        self.transformation_id = "convert_for_loops_to_list_comprehension"
        self.transformation_name = "Convert For-Loops to List Comprehensions  "
        
    def is_applicable(self, code: str) -> bool:
        """
        Checks if any for-loop appending to a list can be converted into a list comprehension.
        """
        try:
            tree = ast.parse(code)
            checker = ForToListComprehensionChecker()
            checker.visit(tree)
            return checker.is_applicable
        except Exception as e:
            print(f"Error during applicability check: {e}")
            return False

    def transform(self, code: str) -> str:
        """
        Transforms the code by converting applicable for-loops to list comprehensions.
        """
        try:
            tree = ast.parse(code)
            transformer = ForToListComprehensionTransformer()
            transformed_tree = transformer.visit(tree)
            transformed_code = astunparse.unparse(transformed_tree)
            return transformed_code
        except Exception as e:
            print(f"Error during transformation: {e}")
            return code