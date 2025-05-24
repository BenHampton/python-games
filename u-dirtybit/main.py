import sys
from enum import Enum

class TokenType(Enum):
    Number='Number',
    Identifier='Identifier',
    Equals='Equals',
    OpenParen='OpenParen',
    CloseParen='CloseParen',
    BinaryOperator='BinaryOperator',
    Let='Let'

class Token:
    def __init__(self, value, tokenType):
     self.value = value
     self.type = tokenType

def token(value, type):
    return Token(value, list(TokenType).index(type))

def is_alpha(src):
    return src.upper() != src.lower()

def is_integer(src):
    c = ord(src)
    bounds = [ord(str(0)), ord(str(9))]
    return c >= bounds[0] and c <= bounds[1]

KEYWORDS = {
    'let': TokenType.Let,
}

def is_skippable(str):
    return str == ' ' or str == '\n' or str == '\t'

def tokenize(sourcecode=''):

    tokens = []
    src = list(sourcecode)
    while len(src) > 0:
        if src[0] == '(':
            tokens.append(token(src.pop(0), TokenType.OpenParen))
        elif src[0] == ')':
            tokens.append(token(src.pop(0), TokenType.CloseParen))
        elif src[0] == '+' or src[0] == '-' or src[0] == '*' or src[0] == '/':
            tokens.append(token(src.pop(0), TokenType.BinaryOperator))
        elif src[0] == '=':
            tokens.append(token(src.pop(0), TokenType.Equals))
        else:
            #handle mutilcharacter tokens.ie '>='
            #build number token

            if is_integer(src[0]):
                num = ''
                while len(src) > 0 and is_integer(src[0]):
                    num += src.pop(0)
                tokens.append(token(num, TokenType.Number))

            elif is_alpha(src[0]):
                identifier = ''
                while len(src) > 0 and is_alpha(src[0]):
                    identifier += src.pop(0)

                reserved = KEYWORDS.get(identifier)
                if reserved is None:
                    tokens.append(token(identifier, TokenType.Identifier))
                else:
                    tokens.append(token(identifier, reserved))
            elif is_skippable(src[0]):
                src.pop(0)
            else:
                print('unrecognized character found in source: ', src[0])
                sys.exit()
    return tokens


if __name__ == '__main__':
    file = open("test.txt", "r")
    content = file.read()
    for token in tokenize(content):
        print(str(token.value) + ' ' + str(token.type))
