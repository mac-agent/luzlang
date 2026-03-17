# Excepciones personalizadas de Luz

class LuzError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(message)

class ReturnException(LuzError):
    def __init__(self, value):
        self.value = value
        super().__init__("Return")

class MathFault(LuzError): pass
class LogicFault(LuzError): pass
class AccessFault(LuzError): pass

class SyntaxFault(LuzError): pass
class UnexpectedTokenFault(SyntaxFault): pass
class InvalidTokenFault(SyntaxFault): pass
class StructureFault(SyntaxFault): pass
class UnexpectedEOFault(SyntaxFault): pass

class SystemFault(LuzError): pass
class UserFault(LuzError): pass # Para 'alert'
