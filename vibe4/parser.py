import re

class PuzzleParser:
    def __init__(self, puzzle_data):
        self.puzzle_text = puzzle_data.get("puzzle", "")
        self.size_str = puzzle_data.get("size", "5*5")
        
        # Calculate Number of Houses from size string (e.g. "5*6" -> 5 houses)
        try:
            self.num_houses = int(self.size_str.split('*')[0])
        except:
            self.num_houses = 5

        self.groups = []
        self.variables = []
        self.domains = {}
        self.constraints = [] # List of tuples: (function, [var_names])

    def parse(self):
        lines = self.puzzle_text.split('\n')
        
        # --- 1. Extract Entities (Variables) ---
        current_group = []
        for line in lines:
            line = line.strip()
            if line.startswith("## Clues"): break
            items = re.findall(r'`([^`]+)`', line)
            if items:
                cleaned_items = [i.replace(" ", "_") for i in items]
                self.groups.append(cleaned_items)
                self.variables.extend(cleaned_items)

        # Set Domains
        house_domain = list(range(1, self.num_houses + 1))
        for var in self.variables:
            self.domains[var] = house_domain

        # --- 2. Implicit Constraints (AllDiff) ---
        for group in self.groups:
            for i in range(len(group)):
                for j in range(i+1, len(group)):
                    self.constraints.append((lambda x, y: x != y, [group[i], group[j]]))

        # --- 3. Parse Text Clues ---
        var_map = {v.lower().replace("_", " "): v for v in self.variables}
        
        # Helper for ordinals
        ordinals = {
            "first": 1, "1st": 1, "house 1": 1,
            "second": 2, "2nd": 2, "house 2": 2,
            "third": 3, "3rd": 3, "house 3": 3,
            "fourth": 4, "4th": 4, "house 4": 4,
            "fifth": 5, "5th": 5, "house 5": 5,
            "sixth": 6, "6th": 6, "house 6": 6
        }

        clue_section = False
        for line in lines:
            if line.startswith("## Clues"):
                clue_section = True
                continue
            if not clue_section: continue
            if not line.strip(): continue

            line_lower = line.lower()
            
            # --- FIXED: Longest Match First Strategy ---
            # 1. Sort variables by length (Longest first) to avoid "Short" matching inside "Very Short"
            sorted_vars = sorted(var_map.items(), key=lambda x: len(x[0]), reverse=True)
            
            found_vars = []
            # We use a temporary string to "mask out" found variables so they aren't found again
            temp_line = line_lower
            
            for v_key, v_real in sorted_vars:
                # Iterate to find ALL occurrences of this variable
                start = 0
                while True:
                    idx = temp_line.find(v_key, start)
                    if idx == -1:
                        break
                    
                    # Store original index (from line_lower) and variable
                    # Note: indices in temp_line correspond to line_lower because we only replace with spaces
                    found_vars.append((idx, v_real))
                    
                    # Mask this occurrence in temp_line with spaces to prevent substring matching
                    # e.g. "very short" -> "          " so "short" won't find it later
                    mask = " " * len(v_key)
                    temp_line = temp_line[:idx] + mask + temp_line[idx+len(v_key):]
                    
                    start = idx + len(v_key)

            # 2. Sort by position in the sentence (to handle "Left/Right" logic correctly)
            found_vars.sort(key=lambda x: x[0])
            
            # 3. Extract final list (deduplicated)
            mentioned = []
            seen = set()
            for _, v_real in found_vars:
                if v_real not in seen:
                    mentioned.append(v_real)
                    seen.add(v_real)
            
            # -------------------------------------------

            # --- CASE A: Unary Constraints ---
            if len(mentioned) == 1:
                target_var = mentioned[0]
                for word, house_num in ordinals.items():
                    if re.search(r'\b' + re.escape(word) + r'\b', line_lower):
                        self.constraints.append((lambda x, h=house_num: x == h, [target_var]))
                        break

            # --- CASE B: Binary Constraints ---
            if len(mentioned) >= 2:
                v1, v2 = mentioned[0], mentioned[1]

                if " is " in line_lower and not any(k in line_lower for k in ["next", "left", "right", "between", "neighbor"]):
                    self.constraints.append((lambda a, b: a == b, [v1, v2]))

                elif "next to" in line_lower or "neighbor" in line_lower:
                    self.constraints.append((lambda a, b: abs(a - b) == 1, [v1, v2]))

                elif "directly left" in line_lower or "immediately left" in line_lower:
                    self.constraints.append((lambda a, b: a == b - 1, [v1, v2]))
                
                elif "directly right" in line_lower or "immediately right" in line_lower:
                    self.constraints.append((lambda a, b: a == b + 1, [v1, v2]))

                elif "left" in line_lower:
                    self.constraints.append((lambda a, b: a < b, [v1, v2]))

                elif "right" in line_lower:
                    self.constraints.append((lambda a, b: a > b, [v1, v2]))

                elif "one house between" in line_lower:
                    self.constraints.append((lambda a, b: abs(a - b) == 2, [v1, v2]))
                
                elif "two houses between" in line_lower:
                    self.constraints.append((lambda a, b: abs(a - b) == 3, [v1, v2]))

        return self.variables, self.domains, self.constraints, self.groups