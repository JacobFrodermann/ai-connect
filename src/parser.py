from typing import List

from textblob import TextBlob

from src.types import RawProblem, ParsedProblem, Constraint
from src.constraints import ValueConstraint, LeftRightConstraint, ImplicationConstraint
import pandas as pd
import unittest

class Parser:
    """
    Responsible for converting raw natural language text into structured Constraints
    using an NLP pipeline (Pandas + TextBlob).
    """
        
    def parse(self, raw: RawProblem) -> ParsedProblem:
        parsed = ParsedProblem(raw.ID)
        
        # 1. Ingestion: Load text into DataFrame for vectorized processing
        # We split by '.' to analyze the puzzle sentence-by-sentence.
        sentences = raw.text.split('.')
        df = pd.DataFrame(sentences, columns=["raw_text"])
        
        # Filter out empty rows caused by splitting
        df = df[df["raw_text"].str.strip() != ""]
        
        # 2. Preprocessing Pipeline
        # Convert to lowercase to standardize (e.g., "Red" -> "red")
        df["processed"] = df["raw_text"].apply(lambda x: " ".join(x.lower().split()))
        
        # Clean punctuation but preserve sentence structure
        # regex=True ensures we remove special chars like '!', ',' but keep spaces
        df["processed"] = df["processed"].str.replace(r"[^\w\s]", "", regex=True)
        
        # Note: We intentionally skip Stopword Removal.
        # Logic keywords like "not", "next to", "same" are crucial for puzzles.

        # 3. Feature Extraction (POS Tagging)
        # We use TextBlob to identify parts of speech:
        # NN (Noun), JJ (Adjective), VB (Verb)
        try:
            df["tags"] = df["processed"].apply(lambda x: TextBlob(x).tags)
        except Exception as e:
            print(f"NLP Error: {e}. Ensure TextBlob corpora is downloaded.")
            return parsed

        # 4. Logic Extraction Loop
        # Iterate through processed sentences to generate Constraints
        for index, row in df.iterrows():
            self._extract_constraints(row["tags"], parsed)
            
        return parsed

    def _extract_constraints(self, tags: List[tuple], parsed_obj: ParsedProblem):
        """
        Analyzes POS tags to extract logical relationships.
        """
        # Extract potential entities (Nouns) and properties (Adjectives/Nouns)
        # NN* captures NN, NNS, NNP, NNPS
        nouns = [word for word, tag in tags if tag.startswith('NN')]
        adjectives = [word for word, tag in tags if tag.startswith('JJ')]
        
        # Heuristic 1: Attribution (Subject + Adjective)
        # Example: "The Englishman(NN) lives in the Red(JJ) house."
        if len(nouns) >= 1 and len(adjectives) >= 1:
            subject = nouns[0]
            value = adjectives[0]
            self._add_constraint(parsed_obj, subject, value)

        # Heuristic 2: Direct Association (Noun + Noun)
        # Example: "The Spaniard(NN) owns the Dog(NN)."
        elif len(nouns) >= 2:
            subject = nouns[0]
            value = nouns[1]
            # Avoid self-referencing (e.g., "The house is a house")
            if subject != value:
                self._add_constraint(parsed_obj, subject, value)

        # -------------------------------
    # NEW: LEFT / RIGHT CONSTRAINT
    # -------------------------------
    words = [w for w, _ in tags]

    if "left" in words or "right" in words:
        direction = "left" if "left" in words else "right"
        nouns_lr = [w for w, t in tags if t.startswith("NN")]

        if len(nouns_lr) >= 2:
            parsed_obj.constraints.append(
                LeftRightConstraint(
                    key1="color",
                    value1=nouns_lr[0],
                    key2="color",
                    value2=nouns_lr[1],
                    direction=direction
                )
            )

    # -------------------------------
    # NEW: IMPLICATION CONSTRAINT
    # -------------------------------
    if "if" in words and "then" in words:
        nouns_impl = [w for w, t in tags if t.startswith("NN")]

        if len(nouns_impl) >= 4:
            parsed_obj.constraints.append(
                ImplicationConstraint(
                    if_key="attr1",
                    if_value=nouns_impl[0],
                    then_key="attr2",
                    then_value=nouns_impl[1]
                )
            )


    def _add_constraint(self, parsed_obj: ParsedProblem, entity1: str, entity2: str):
        """
        Helper to add a constraint and register entities.
        """
        parsed_obj.entities.add(entity1)
        parsed_obj.entities.add(entity2)
        parsed_obj.constraints.append(ValueConstraint(entity1, entity2))
    
    def parseGridmode(self, raw: RawProblem) -> ParsedProblem:
        parsed = self.parse(raw)

        sp = raw.size.split('*')
        parsed.size = (int(sp[0]), int(sp[1]))
        
        return parsed
        
    def parseMultipleChoice(self, raw: RawProblem) -> ParsedProblem:
        parsed = self.parse(raw)

        parsed.requestedProperty = raw.question.split(' ')[2]
        parsed.houseNumber = int(raw.question.split(' ')[-1].removesuffix('?'))
         
        return parsed
    

class TestParser(unittest.TestCase):
    def setUp(self):
        self.parser = Parser()

    def test_parse_gridmode(self):
        raw = RawProblem(id="lgp-test-2x3-13", size="2*3",text="There are 2 houses, numbered 1 to 2 from left to right, as seen from across the street. Each house is occupied by a different person. Each house has a unique attribute for each of the following characteristics:\n - Each person has a unique name: `Arnold`, `Eric`\n - Each person has a unique level of education: `high school`, `associate`\n - The mothers' names in different houses are unique: `Aniya`, `Holly`\n\n## Clues:\n1. The person with an associate's degree is in the first house.\n2. The person whose mother's name is Holly is Arnold.\n3. The person whose mother's name is Holly is not in the second house.\n")
        #"solution":{"header":["House","Name","Education","Mother"],"rows":[["1","Arnold","associate","Holly"],["2","Eric","high school","Aniya"]]},"created_at":"2024-07-03T21:21:29.204735"}
        parsed = self.parser.parseGridmode(raw)
        
        self.assertEqual(parsed.size, (2, 3))
