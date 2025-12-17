from typing import List, TypedDict, Set, Dict

# --- Core Data Structures (Updated for Parser needs) ---

class Person(TypedDict):
    properties: dict[str, str]


class Constraint:
    """
    Base interface for all logical rules.
    """
    def isSatisfied(self, solution: "Solution") -> bool:
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

    def __init__(self, id: str, text: str, size: str, question: str = "", choiches: str = ""):
        self.ID = id
        self.text = text
        self.size = size
        # Make these optional to prevent errors.
        self.question = question
        self.choiches = choiches

class ParsedProblem:
    """
    The structured output produced by the Parser.
    Updated to store the extracted constraints and entities.
    """
    ID: str
    constraints: List[Constraint]
    entities: Dict[str, List[str]] # Valid entities found (e.g., 'Englishman', 'Red', 'Dog')
    
    """
    Gridmode specific
    """
    size: tuple[int, int]

    """"
    Multiple Choice Mode specific
    """
    requestedEntity: str
    houseNumber: int

    def __init__(self, id: str, width: int, height: int):
        self.ID = id
        self.constraints = []
        self.entities: dict[str, list[str]] = {}
        self.size = (width, height)

        # Initialize with default values to prevent errors
        self.requestedEntity = ""
        self.houseNumber = 0

class Solution:
    # List Index = House Number
    ppl: List[Person] = []
    steps: int
    ID: str
    entities: Set[str]


# --- THE PARSER (Your Part) ---

# --- verification (Not part of the class file, but for testing) ---
#if __name__ == "__main__":
#    # Simulating data from the ZebraLogicBench 'puzzle' column
 #   sample_puzzle_text = "There are 5 houses. The Englishman lives in the red house. The Spaniard owns the dog."
 #
 #   raw = RawProblem("lgp-test-5x6-16", sample_puzzle_text)
 #   parser = Parser()
 #   result = parser.parse(raw)
    
 #   print(f"Parsed ID: {result.ID}")
 #   print(f"Entities: {result.entities}")
 #   print(f"Constraints: {result.constraints}")
