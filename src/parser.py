from typing import List
from textblob import TextBlob
from classes import *
from constraints import *
import pandas as pd
import unittest
import re

class Parser:
    """
    Responsible for converting raw natural language text into structured Constraints
    using an NLP pipeline (Pandas + TextBlob).
    """
        
    def parse(self, raw: RawProblem) -> ParsedProblem:

        w, h = 0, 0

        if hasattr(raw, "size") and isinstance(raw.size, str) and "*" in raw.size:
            parts = raw.size.split("*")
            w, h = int(parts[0]), int(parts[1])

        parsed = ParsedProblem(raw.ID, w, h)

        # Read the headings (Colors: red...) and the entities dictionary
        self.extract_entities_and_categories(raw.text, parsed)
        
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
    
    def get_category_of_entity(self, entity_name: str, parsed_obj: ParsedProblem) -> str:
        
        # It finds which category (e.g., 'colors') the given word (e.g., 'red') belongs to. 
        for category, values in parsed_obj.entities.items():
            if entity_name in values:
                return category
        return "unknown"
    
    def _extract_constraints(self, tags: List[tuple], parsed_obj: ParsedProblem):
        """
        Analyzes the sentence to find logical rules.
        """
        # 1. Prepare words list for easy searching
        words = [w.lower() for w, _ in tags]

        ordinals = {
            "first": "1", "1st": "1",
            "second": "2", "2nd": "2",
            "third": "3", "3rd": "3", 
            "fourth": "4", "4th": "4",
            "fifth": "5", "5th": "5",
            "sixth": "6", "6th": "6"
        }
        
        total_houses = parsed_obj.size[0]
        mid_house = str((total_houses + 1) // 2) 

        # 2. Check for special keywords (Operators)
        is_negative = "not" in words or "n't" in words or "neither" in words
        is_neighbor = "next" in words or "beside" in words or "adjacent" in words
        is_or_logic = "or" in words
        is_between = "between" in words
        
        direction = None
        if "left" in words: direction = "left"
        elif "right" in words: direction = "right"

        # 3. Find valid entities (names, colors, etc.) in the sentence
        found_entities = []
        for word, tag in tags:
            category = self.get_category_of_entity(word, parsed_obj)
            
            if category != "unknown":
                found_entities.append((word, category))

            if word in ordinals:
                found_entities.append((ordinals[word], "house"))

            elif word == "middle":
                found_entities.append((mid_house, "house"))


        if len(found_entities) < 2:
            return
        
        # between logic
        if is_between and len(found_entities) > 2:
            subj = found_entities[0][0]
            val1 = found_entities[1][0]
            val2 = found_entities[2][0]
            
            parsed_obj.constraints.append(BetweenConstraint(subject=subj, value1=val1, value2=val2))
            return
        
        # or logic
        if is_or_logic and len(found_entities) > 2:
            subj = found_entities[0][0]
            val1 = found_entities[1][0]
            val2 = found_entities[2][0]
            parsed_obj.constraints.append(OrConstraint(subject=subj, value1=val1, value2=val2))
            return


        # Get the first two entities found
        val1, cat1 = found_entities[0]
        val2, cat2 = found_entities[1]

        # 4. Create the correct Constraint object based on keywords found
        
        # Case A: Neighbor Logic (e.g., "The blue house is next to the red house")
        if is_neighbor:
            con = NeighborConstraint(subject=val1, neighbor=val2)
            parsed_obj.constraints.append(con)
            return

        # Case B: Direction Logic (e.g., "The white house is to the left of the green house")
        if direction:
            con = LeftRightConstraint(
                key1=cat1,   
                value1=val1, 
                key2=cat2, 
                value2=val2, 
                direction=direction
            )
            parsed_obj.constraints.append(con)
            return

        # Case C: Negative Logic (e.g., "Bob does NOT live in the yellow house")
        if is_negative:
            con = IsNotConstraint(subject=val1, value=val2)
            parsed_obj.constraints.append(con)
            return

        # Case D: Standard Assignment (e.g., "Alice lives in the blue house")
        # Default case if no other special keywords are found
        con = ValueConstraint(subject=val1, value=val2)
        parsed_obj.constraints.append(con)


    def _add_constraint(self, parsed_obj: ParsedProblem, entity1: str, entity2: str):
        """
        Helper to add a constraint and register entities.
        """
        parsed_obj.constraints.append(ValueConstraint(entity1, entity2))
    
    def parseGridmode(self, raw: RawProblem) -> ParsedProblem:
        parsed = self.parse(raw)

        sp = raw.size.split('*')
        parsed.size = (int(sp[0]), int(sp[1]))
        
        return parsed
        
    def parseMultipleChoice(self, raw: RawProblem) -> ParsedProblem:
        parsed = self.parse(raw)

        parsed.requestedEntity = raw.question.split(' ')[2]
        parsed.houseNumber = int(raw.question.split(' ')[-1].removesuffix('?'))
         
        return parsed
    
    def extract_entities_and_categories(self, text: str, parsed_obj: ParsedProblem):
        
        #'Colors: red, blue.' -> {'colors': ['red', 'blue']}
        pattern = r"([A-Z][a-zA-Z]+):\s*([^.\n]+)"
        matches = re.findall(pattern, text)
        for category, values in matches:
            category_name = category.lower().strip()

            # skip the word 'Clues' so they don't mistake it for a category.
            if category_name == "clues":
                continue
            
            # (e.g. red and green -> red, green)
            cleaned_values = values.replace(" and ", ", ")

            val_list = [v.strip().lower() for v in cleaned_values.split(",")]
            parsed_obj.entities[category_name] = val_list

class TestParser(unittest.TestCase):
    def setUp(self):
        self.parser = Parser()

    def test_parse_gridmode(self):
        raw = RawProblem(id="lgp-test-2x3-13", size="2*3",text="There are 2 houses, numbered 1 to 2 from left to right, as seen from across the street. Each house is occupied by a different person. Each house has a unique attribute for each of the following characteristics:\n - Each person has a unique name: `Arnold`, `Eric`\n - Each person has a unique level of education: `high school`, `associate`\n - The mothers' names in different houses are unique: `Aniya`, `Holly`\n\n## Clues:\n1. The person with an associate's degree is in the first house.\n2. The person whose mother's name is Holly is Arnold.\n3. The person whose mother's name is Holly is not in the second house.\n")
        #"solution":{"header":["House","Name","Education","Mother"],"rows":[["1","Arnold","associate","Holly"],["2","Eric","high school","Aniya"]]},"created_at":"2024-07-03T21:21:29.204735"}
        parsed = self.parser.parseGridmode(raw)
        
        self.assertEqual(parsed.size, (2, 3))
        self.assertIn("mothers' name", parsed.entities)
        self.assertIn("level of education", parsed.entities)

        expectedConstrain = IsNotConstraint()
