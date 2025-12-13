from typing import List
from typing import TypedDict

class Person:
    properties = TypedDict[str, str]

class Solution:
    var = List[Person]

class Constraint:
    def isStatisfied(self, Solution) -> bool:
        pass

class RawProblem:
    ID: str

class ParsedProblem:
    ID: str

class Importer:
    def next(self) -> RawProblem:
        pass

class Parser:
    def parse(self, raw: RawProblem) -> ParsedProblem:
        pass
class Solver:
    def solve(self, problem: ParsedProblem) -> Solution:
        pass