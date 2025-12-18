import json
from parser import PuzzleParser
from solver import CSPSolver

def debug_puzzle(puzzle_id):
    # Load data
    with open("zebra_puzzles.json", "r") as f:
        puzzles = json.load(f)
    
    # Find the specific puzzle
    puzzle = next((p for p in puzzles if p["id"] == puzzle_id), None)
    if not puzzle:
        print("Puzzle not found!")
        return

    print(f"--- Debugging {puzzle_id} ---")
    print("TEXT:\n", puzzle["puzzle"])
    
    # Run Parser
    parser = PuzzleParser(puzzle)
    variables, domains, constraints, groups = parser.parse()
    
    print(f"\nExtracted {len(variables)} variables.")
    print(f"Extracted {len(constraints)} constraints.")
    
    # PRINT THE CONSTRAINTS to see what is missing
    # Note: parsing constraints usually results in functions, so we can't print source code easily,
    # but we can count them.
    
    # Run Solver
    print("\nAttempting to solve...")
    solver = CSPSolver(variables, domains)
    for func, scope in constraints:
        solver.add_constraint(func, scope)
        
    assignment = solver.solve()
    
    if assignment:
        print("✅ SOLVED!")
        print(assignment)
    else:
        print("❌ FAILED. The constraints led to a contradiction or search exhaustion.")

# Pick an ID from your 'Failed' list in the logs
# Example: lgp-test-2x6-8 (Low steps failure) or lgp-test-6x6-13 (High steps failure)
debug_puzzle("lgp-test-2x6-8")