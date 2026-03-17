from .tokens import TokenType
from .exceptions import (
    LuzError, ReturnException, MathFault, LogicFault, 
    AccessFault, SyntaxFault, SystemFault, UserFault
)

class Environment:
    def __init__(self, parent=None):
        self.records = {}
        self.parent = parent

    def define(self, name, value):
        self.records[name] = value
        return value

    def lookup(self, name):
        if name in self.records:
            return self.records[name]
        if self.parent:
            return self.parent.lookup(name)
        raise AccessFault(f"Variable '{name}' not defined")

    def assign(self, name, value):
        if name in self.records:
            self.records[name] = value
            return value
        if self.parent:
            return self.parent.assign(name, value)
        self.records[name] = value
        return value

class LuzFunction:
    def __init__(self, node, closure):
        self.node = node
        self.closure = closure

    def __call__(self, interpreter, arguments):
        env = Environment(self.closure)
        for i in range(len(self.node.arg_tokens)):
            env.define(self.node.arg_tokens[i].value, arguments[i])
        
        try:
            interpreter.execute_block(self.node.block, env)
        except ReturnException as e:
            return e.value
        return None

class Interpreter:
    def __init__(self):
        self.global_env = Environment()
        self.current_env = self.global_env
        self.builtins = {
            'write': self.builtin_write,
            'listen': self.builtin_listen,
            'len': self.builtin_len,
            'append': self.builtin_append,
            'pop': self.builtin_pop,
            'keys': self.builtin_keys,
            'values': self.builtin_values,
            'remove': self.builtin_remove
        }

    def execute_block(self, block, env):
        previous_env = self.current_env
        self.current_env = env
        try:
            result = None
            for statement in block:
                result = self.visit(statement)
            return result
        finally:
            self.current_env = previous_env

    def visit(self, node):
        if isinstance(node, list):
            result = None
            for statement in node:
                result = self.visit(statement)
            return result

        method_name = f'visit_{type(node).__name__}'
        method = getattr(self, method_name, self.no_visit_method)
        return method(node)

    def no_visit_method(self, node):
        raise SystemFault(f'No visit_{type(node).__name__} method defined')

    def visit_NumberNode(self, node):
        return node.token.value

    def visit_StringNode(self, node):
        return node.token.value

    def visit_BooleanNode(self, node):
        return True if node.token.type == TokenType.TRUE else False

    def visit_ListNode(self, node):
        return [self.visit(element) for element in node.elements]

    def visit_DictNode(self, node):
        res = {}
        for key_node, value_node in node.pairs:
            key = self.visit(key_node)
            value = self.visit(value_node)
            res[key] = value
        return res

    def visit_IndexAccessNode(self, node):
        base = self.visit(node.base_node)
        index = self.visit(node.index_node)
        
        if isinstance(base, list):
            try:
                return base[int(index)]
            except IndexError:
                raise AccessFault(f"Index {index} out of range")
            except ValueError:
                raise LogicFault(f"List index must be an integer")
        elif isinstance(base, dict):
            try:
                return base[index]
            except KeyError:
                raise AccessFault(f"Key '{index}' not found in dictionary")
        else:
            raise LogicFault("Object does not support indexing")

    def visit_IndexAssignNode(self, node):
        base = self.visit(node.base_node)
        index = self.visit(node.index_node)
        value = self.visit(node.value_node)
        
        if isinstance(base, list):
            try:
                base[int(index)] = value
                return value
            except IndexError:
                raise AccessFault(f"Index {index} out of range")
            except ValueError:
                raise LogicFault(f"List index must be an integer")
        elif isinstance(base, dict):
            base[index] = value
            return value
        else:
            raise LogicFault("Object does not support index assignment")

    def visit_AttemptRescueNode(self, node):
        try:
            return self.visit(node.try_block)
        except LuzError as e:
            if isinstance(e, ReturnException):
                raise e
            
            previous_env = self.current_env
            rescue_env = Environment(previous_env)
            self.current_env = rescue_env
            try:
                self.current_env.define(node.error_var_token.value, e.message)
                return self.visit(node.catch_block)
            finally:
                self.current_env = previous_env
        except Exception as e:
            previous_env = self.current_env
            rescue_env = Environment(previous_env)
            self.current_env = rescue_env
            try:
                self.current_env.define(node.error_var_token.value, f"SystemFault: {str(e)}")
                return self.visit(node.catch_block)
            finally:
                self.current_env = previous_env

    def visit_AlertNode(self, node):
        msg = self.visit(node.expression_node)
        raise UserFault(str(msg))

    def visit_UnaryOpNode(self, node):
        res = self.visit(node.node)
        if node.op_token.type == TokenType.NOT:
            return not res
        return res

    def visit_VarAssignNode(self, node):
        var_name = node.var_name_token.value
        value = self.visit(node.value_node)
        self.current_env.assign(var_name, value)
        return value

    def visit_VarAccessNode(self, node):
        var_name = node.token.value
        return self.current_env.lookup(var_name)

    def visit_BinOpNode(self, node):
        left = self.visit(node.left_node)
        right = self.visit(node.right_node)

        if node.op_token.type == TokenType.PLUS:
            return left + right
        elif node.op_token.type == TokenType.MINUS:
            if isinstance(left, str) or isinstance(right, str):
                raise LogicFault("Operation '-' not supported for strings")
            return left - right
        elif node.op_token.type == TokenType.MUL:
            if isinstance(left, str) and isinstance(right, float):
                return left * int(right)
            if isinstance(left, float) or isinstance(right, float):
                 return left * right
            raise LogicFault("Operation '*' only supported between numbers or string and number")
        elif node.op_token.type == TokenType.DIV:
            if isinstance(left, str) or isinstance(right, str):
                raise LogicFault("Operation '/' not supported for strings")
            if right == 0:
                raise MathFault("Division by zero")
            return left / right
        elif node.op_token.type == TokenType.EE:
            return left == right
        elif node.op_token.type == TokenType.NE:
            return left != right
        elif node.op_token.type == TokenType.LT:
            if isinstance(left, (int, float)) and isinstance(right, (int, float)):
                return left < right
            raise LogicFault("Comparison '<' only supported between numbers")
        elif node.op_token.type == TokenType.GT:
            if isinstance(left, (int, float)) and isinstance(right, (int, float)):
                return left > right
            raise LogicFault("Comparison '>' only supported between numbers")
        elif node.op_token.type == TokenType.LTE:
            if isinstance(left, (int, float)) and isinstance(right, (int, float)):
                return left <= right
            raise LogicFault("Comparison '<=' only supported between numbers")
        elif node.op_token.type == TokenType.GTE:
            if isinstance(left, (int, float)) and isinstance(right, (int, float)):
                return left >= right
            raise LogicFault("Comparison '>=' only supported between numbers")
        elif node.op_token.type == TokenType.AND:
            return left and right
        elif node.op_token.type == TokenType.OR:
            return left or right

    def visit_IfNode(self, node):
        for condition, block in node.cases:
            if self.visit(condition):
                return self.visit(block)
        
        if node.else_case:
            return self.visit(node.else_case)
        
        return None

    def visit_WhileNode(self, node):
        while self.visit(node.condition_node):
            self.visit(node.block)
        return None

    def visit_ForNode(self, node):
        var_name = node.var_name_token.value
        start_value = self.visit(node.start_value_node)
        end_value = self.visit(node.end_value_node)

        i = start_value
        previous_env = self.current_env
        self.current_env = Environment(previous_env)
        try:
            while i <= end_value:
                self.current_env.define(var_name, i)
                self.visit(node.block)
                i += 1
        finally:
            self.current_env = previous_env
        return None

    def visit_FuncDefNode(self, node):
        func_name = node.name_token.value
        function = LuzFunction(node, self.current_env)
        self.current_env.define(func_name, function)
        return None

    def visit_ReturnNode(self, node):
        value = None
        if node.expression_node:
            value = self.visit(node.expression_node)
        raise ReturnException(value)

    def visit_CallNode(self, node):
        func_name = node.func_name_token.value
        arguments = [self.visit(arg) for arg in node.arguments]

        if func_name in self.builtins:
            return self.builtins[func_name](*arguments)
        
        try:
            function = self.current_env.lookup(func_name)
            if not isinstance(function, LuzFunction):
                raise LogicFault(f"'{func_name}' is not a function")
            
            if len(arguments) != len(function.node.arg_tokens):
                raise LogicFault(f"Expected {len(function.node.arg_tokens)} arguments, received {len(arguments)}")
            
            return function(self, arguments)
        except LuzError as e:
            raise e
        except Exception as e:
            if "no definida" in str(e) or "not defined" in str(e):
                raise AccessFault(f"Function '{func_name}' not defined")
            raise SystemFault(str(e))

    def builtin_write(self, *args):
        print(*args)
        return None

    def builtin_listen(self, prompt=""):
        res = input(prompt)
        try:
            return float(res)
        except ValueError:
            return res

    def builtin_len(self, obj):
        try:
            return float(len(obj))
        except:
            raise LogicFault("Object has no length")

    def builtin_append(self, list_obj, element):
        if not isinstance(list_obj, list):
            raise LogicFault("append() requires a list as first argument")
        list_obj.append(element)
        return None

    def builtin_pop(self, list_obj, index=None):
        if not isinstance(list_obj, list):
            raise LogicFault("pop() requires a list as first argument")
        try:
            if index is None:
                return list_obj.pop()
            return list_obj.pop(int(index))
        except IndexError:
            raise AccessFault("Index out of range in pop()")

    def builtin_keys(self, dict_obj):
        if not isinstance(dict_obj, dict):
            raise LogicFault("keys() requires a dictionary")
        return list(dict_obj.keys())

    def builtin_values(self, dict_obj):
        if not isinstance(dict_obj, dict):
            raise LogicFault("values() requires a dictionary")
        return list(dict_obj.values())

    def builtin_remove(self, dict_obj, key):
        if not isinstance(dict_obj, dict):
            raise LogicFault("remove() requires a dictionary")
        return dict_obj.pop(key, None)
