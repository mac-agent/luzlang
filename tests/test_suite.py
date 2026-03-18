import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from luz.lexer import Lexer
from luz.parser import Parser
from luz.interpreter import Interpreter

def test_arithmetic():
    print("Testing arithmetic...")
    interpreter = Interpreter()
    cases = [("1 + 2 * 3", 7.0), ("(1 + 2) * 3", 9.0), ("10 / 2 - 1", 4.0)]
    for code, expected in cases:
        tokens = Lexer(code).get_tokens()
        ast = Parser(tokens).parse()
        assert interpreter.visit(ast) == expected
    print("Arithmetic: OK")

def test_variables_and_strings():
    print("Testing variables and strings...")
    interpreter = Interpreter()
    code = 'a = "hello" b = " world" res = a + b'
    interpreter.visit(Parser(Lexer(code).get_tokens()).parse())
    assert interpreter.global_env.lookup('res') == "hello world"
    
    code = 'risa = "ja" * 3'
    interpreter.visit(Parser(Lexer(code).get_tokens()).parse())
    assert interpreter.global_env.lookup('risa') == "jajaja"
    print("Variables and strings: OK")

def test_control_flow():
    print("Testing control flow (if, while, for)...")
    interpreter = Interpreter()
    
    code = 'x = 10 if x > 5 { res = "yes" } else { res = "no" }'
    interpreter.visit(Parser(Lexer(code).get_tokens()).parse())
    assert interpreter.global_env.lookup('res') == "yes"
    
    code = 'i = 0 while i < 5 { i = i + 1 }'
    interpreter.visit(Parser(Lexer(code).get_tokens()).parse())
    assert interpreter.global_env.lookup('i') == 5.0
    
    code = 'total = 0 for k = 1 to 5 { total = total + k }'
    interpreter.visit(Parser(Lexer(code).get_tokens()).parse())
    assert interpreter.global_env.lookup('total') == 15.0
    print("Control flow: OK")

def test_logical_and_booleans():
    print("Testing booleans and logic...")
    interpreter = Interpreter()
    cases = [
        ("true and false", False),
        ("true or false", True),
        ("not false", True),
        ("10 > 5 and not (2 == 3)", True)
    ]
    for code, expected in cases:
        tokens = Lexer(code).get_tokens()
        ast = Parser(tokens).parse()
        assert interpreter.visit(ast) == expected
    print("Booleans and logic: OK")

def test_functions():
    print("Testing functions...")
    interpreter = Interpreter()
    code = '''
    function factorial(n) {
        if n <= 1 { return 1 }
        return n * factorial(n - 1)
    }
    res = factorial(5)
    '''
    interpreter.visit(Parser(Lexer(code).get_tokens()).parse())
    assert interpreter.global_env.lookup('res') == 120.0
    print("Functions and recursion: OK")

def test_lists():
    print("Testing lists...")
    interpreter = Interpreter()
    code = 'l = [10, "hello", true] res = l[0] + 5'
    interpreter.visit(Parser(Lexer(code).get_tokens()).parse())
    assert interpreter.global_env.lookup('res') == 15.0
    
    code = 'l[1] = "world" val = l[1]'
    interpreter.visit(Parser(Lexer(code).get_tokens()).parse())
    assert interpreter.global_env.lookup('val') == "world"
    
    code = 'append(l, 40) tam = len(l) ultimo = pop(l)'
    interpreter.visit(Parser(Lexer(code).get_tokens()).parse())
    assert interpreter.global_env.lookup('tam') == 4.0
    assert interpreter.global_env.lookup('ultimo') == 40.0
    print("Lists: OK")

def test_dicts():
    print("Testing dictionaries...")
    interpreter = Interpreter()
    code = 'd = {"name": "Eloi", "age": 25} res = d["name"]'
    interpreter.visit(Parser(Lexer(code).get_tokens()).parse())
    assert interpreter.global_env.lookup('res') == "Eloi"
    
    code = 'd["age"] = 26 d["city"] = "BCN"'
    interpreter.visit(Parser(Lexer(code).get_tokens()).parse())
    d = interpreter.global_env.lookup('d')
    assert d["age"] == 26.0
    assert d["city"] == "BCN"
    
    code = 'ks = keys(d) tam = len(d)'
    interpreter.visit(Parser(Lexer(code).get_tokens()).parse())
    assert interpreter.global_env.lookup('tam') == 3.0
    ks = interpreter.global_env.lookup('ks')
    assert "name" in ks and "age" in ks and "city" in ks
    print("Dictionaries: OK")

def test_errors():
    print("Testing error handling...")
    interpreter = Interpreter()
    
    # attempt / rescue with ZeroDivisionFault
    code = '''
    msg = ""
    attempt {
        x = 10 / 0
    } rescue (error) {
        msg = error
    }
    '''
    interpreter.visit(Parser(Lexer(code).get_tokens()).parse())
    msg = interpreter.global_env.lookup('msg')
    assert "Division by zero" in str(msg)
    
    # alert
    code2 = '''
    caught = ""
    attempt {
        alert "My custom error"
    } rescue (e) {
        caught = e
    }
    '''
    interpreter.visit(Parser(Lexer(code2).get_tokens()).parse())
    caught = interpreter.global_env.lookup('caught')
    assert "My custom error" in str(caught)
    print("Error handling: OK")

def test_casting():
    print("Testing type conversion (casting)...")
    interpreter = Interpreter()
    
    # to_num
    code = 'res = to_num("123.45")'
    interpreter.visit(Parser(Lexer(code).get_tokens()).parse())
    assert interpreter.global_env.lookup('res') == 123.45
    
    # to_str
    code = 'res = to_str(true)'
    interpreter.visit(Parser(Lexer(code).get_tokens()).parse())
    assert interpreter.global_env.lookup('res') == "true"
    
    # to_bool
    code = 'res = to_bool(1)'
    interpreter.visit(Parser(Lexer(code).get_tokens()).parse())
    assert interpreter.global_env.lookup('res') is True
    
    print("Casting: OK")

def run_all():
    print("=== STARTING LUZ TEST SUITE ===\n")
    try:
        test_arithmetic()
        test_variables_and_strings()
        test_control_flow()
        test_logical_and_booleans()
        test_functions()
        test_lists()
        test_dicts()
        test_errors()
        test_casting()
        print("\n=== ALL TESTS PASSED SUCCESSFULLY! ===")
    except Exception as e:
        print(f"\nTEST ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    run_all()
