from .matcher import compile, Match

def match(pattern: str, string: str):
    return compile(pattern).match(string)

def search(pattern: str, string: str):
    return compile(pattern).search(string)

def findall(pattern: str, string: str):
    return compile(pattern).findall(string)

def sub(pattern: str, repl, string: str, count: int = 0):
    return compile(pattern).sub(repl, string, count)
