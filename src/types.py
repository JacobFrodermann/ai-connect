import pandas as pd
from textblob import TextBlob
from typing import List, TypedDict, Set

# --- Core Data Structures (Updated for Parser needs) ---

class Person(TypedDict):
    properties: dict[str, str]


class Constraint:
    """
    Base interface for all logical rules.
    """
    def isSatisfied(self, solution: Solution) -> bool:
        return True



class RawProblem:
    """
    Holds the raw data ingested from the dataset.
    Updated to include 'text' which comes from the 'puzzle' column in ZebraLogicBench.
    """
    ID: str
    text: str

    """
    Gridmode specific
    """
    size: str
    
    """"
    Multiple Choice Mode specific
    """
    question: str
    choiches: str

    def __init__(self, id: str, text: str, size: str, question: str, choiches: str):
        self.ID = id
        self.text = text
        self.size = size

class ParsedProblem:
    """
    The structured output produced by the Parser.
    Updated to store the extracted constraints and entities.
    """
    ID: str
    constraints: List[Constraint]
    entities: Set[str] # Valid entities found (e.g., 'Englishman', 'Red', 'Dog')
    
    """
    Gridmode specific
    """
    size: tuple[int, int]

    """"
    Multiple Choice Mode specific
    """
    requestedProperty: str
    houseNumber: int

    def __init__(self, id: str, width: int, height: int):
        self.ID = id
        self.constraints = []
        self.entities = set()
        self.size = (width, height)

class Solution:
    problem: ParsedProblem
    # List Index = House Number
    var: List[Person] = []

# --- THE PARSER (Your Part) ---

# --- verification (Not part of the class file, but for testing) ---
if __name__ == "__main__":
    # Simulating data from the ZebraLogicBench 'puzzle' column
    sample_puzzle_text = "There are 5 houses. The Englishman lives in the red house. The Spaniard owns the dog."
    
    raw = RawProblem("lgp-test-5x6-16", sample_puzzle_text)
    parser = Parser()
    result = parser.parse(raw)
    
    print(f"Parsed ID: {result.ID}")
    print(f"Entities: {result.entities}")
    print(f"Constraints: {result.constraints}")
