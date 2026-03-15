from luz.lexer import Lexer
from luz.parser import Parser
from luz.interpreter import Interpreter

def test_luz_write():
    interpreter = Interpreter()
    
    print("Probando write()...")
    
    # 1. Simple write
    lexer = Lexer('write("Hola mundo desde Luz!")')
    ast = Parser(lexer.get_tokens()).parse()
    interpreter.visit(ast)
    
    # 2. Write with variables and numbers
    lexer = Lexer('x = 100; write("El valor de x es:", x)')
    # Note: Our lexer/parser doesn't support ';' to separate statements in one line easily yet unless they are in a block or processed one by one.
    # Let's do it in two steps for the test.
    
    Lexer('x = 100').get_tokens()
    interpreter.visit(Parser(Lexer('x = 100').get_tokens()).parse())
    interpreter.visit(Parser(Lexer('write("El valor de x es:", x)').get_tokens()).parse())

    # 3. Write with expression
    interpreter.visit(Parser(Lexer('write("Suma:", 5 + 5)').get_tokens()).parse())

    print("\n¡Pruebas de write() completadas!")

if __name__ == "__main__":
    test_luz_write()
