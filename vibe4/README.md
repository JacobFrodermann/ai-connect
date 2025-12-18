# CSP Solver for Logic Grid Puzzles (ZebraLogicBench)

## 📌 Overview
This project implements a **Constraint Satisfaction Problem (CSP)** solver combined with a **Regex-based Natural Language Parser** to solve logic grid puzzles from the ZebraLogicBench dataset. The system is designed to maximize accuracy and efficiency (minimizing search steps) using the Minimum Remaining Values (MRV) heuristic and Forward Checking.

## ⚙️ Architecture

### 1. Data Parsing (`parser.py`)
* **Variable Extraction:** Parses entities from the puzzle text using Regex (identifying backticked items like \`Red\`).
* **Constraint Mapping:** Converts natural language clues into lambda functions.
    * *Equality:* "The Englishman is in the red house" → `var1 == var2`
    * *Topology:* "Next to" → `abs(var1 - var2) == 1`
    * *Ordering:* "Left of" → `var1 < var2`
* **Robustness:** Implements "Longest Match First" to handle overlapping variable names (e.g., distinguishing "Very Short" from "Short") and sorts variables by sentence position to correctly interpret directional clues.

### 2. CSP Engine (`solver.py`)
* **Model:** Uses a "House-Index" representation where variables are entities (e.g., `Dog`, `Red`) and values are House Numbers (1-N).
* **MRV Heuristic:** Always selects the unassigned variable with the smallest remaining domain to fail fast.
* **Forward Checking:** Prunes domains of neighboring variables immediately after an assignment to drastically reduce the search space.

## 🚀 How to Run
1. Ensure `zebra_puzzles.json` is in the directory.
2. Run the evaluation script:
   ```bash
   python run.py