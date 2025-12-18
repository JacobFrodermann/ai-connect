import json
import pandas as pd
import time
from parser import PuzzleParser
from solver import CSPSolver

def format_grid_solution(solution, groups):
    """
    Formats the solver output into the specific JSON structure required.
    """
    if not solution:
        return {"header": [], "rows": []}

    # Find the categories (headers)
    # The groups list from parser gives us the categories
    # We need headers. Usually, we don't have explicit headers in the text, 
    # so we name them Group1, Group2, or infer from content. 
    # For now, generic headers match the row count.
    
    num_houses = max(solution.values())
    
    # Sort groups to ensure consistent column order
    # (Optional: In a real scenario, you try to match the header names provided in the 'solution' dummy)
    
    rows = []
    for h in range(1, num_houses + 1):
        row = [str(h)] # First column is always House Number
        
        for group in groups:
            # Find which member of this group is in house h
            found_member = "None"
            for member in group:
                if solution.get(member) == h:
                    found_member = member
                    break
            row.append(found_member)
        rows.append(row)

    # Construct Header
    headers = ["House"] + [f"Category_{i+1}" for i in range(len(groups))]
    
    return {"header": headers, "rows": rows}

def main():
    print("🚀 Starting Solver Pipeline...")
    
    # Load Data
    try:
        with open("zebra_puzzles.json", "r") as f:
            puzzles = json.load(f)
    except FileNotFoundError:
        print("❌ Error: zebra_puzzles.json not found.")
        return

    results = []
    
    # Limit for testing? Set to None to run all.
    # puzzles = puzzles[:5] 

    total_puzzles = len(puzzles)
    solved_count = 0

    for idx, puzzle_data in enumerate(puzzles):
        pid = puzzle_data.get("id", idx)
        print(f"[{idx+1}/{total_puzzles}] Parsing {pid}...", end="\r")

        try:
            # 1. Parse
            parser = PuzzleParser(puzzle_data)
            variables, domains, constraints, groups = parser.parse()

            # 2. Solve
            solver = CSPSolver(variables, domains)
            for func, scope in constraints:
                solver.add_constraint(func, scope)

            start_time = time.time()
            assignment = solver.solve()
            duration = time.time() - start_time

            # 3. Store Results
            if assignment:
                solved_count += 1
                grid_json = format_grid_solution(assignment, groups)
                status = "✅ Solved"
            else:
                grid_json = {} # Empty if failed
                status = "❌ Failed"

            print(f"[{idx+1}/{total_puzzles}] {status} ID: {pid} | Steps: {solver.steps} | Time: {duration:.4f}s")

            results.append({
                "id": pid,
                "grid_solution": json.dumps(grid_json), # Needs to be a JSON string
                "steps": solver.steps
            })
            
        except Exception as e:
            print(f"\nError on {pid}: {e}")
            results.append({"id": pid, "grid_solution": "{}", "steps": 0})

    # Save CSV
    df = pd.DataFrame(results)
    df.to_csv("results.csv", index=False) # Competition usually uses comma or pipe
    print(f"\n🎉 Finished! Solved {solved_count}/{total_puzzles}.")
    print("Results saved to 'results.csv'.")

if __name__ == "__main__":
    main()