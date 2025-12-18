import json

def inspect_first_puzzle():
    filename = "zebra_puzzles.json"
    
    try:
        with open(filename, 'r') as f:
            data = json.load(f)
            
        print(f"Total puzzles found: {len(data)}")
        
        # Get the first puzzle
        first_puzzle = data[0]
        
        print("\n--- Keys in the Data ---")
        print(first_puzzle.keys())
        
        print("\n--- Sample Content (First Puzzle) ---")
        print(json.dumps(first_puzzle, indent=2))
        
    except FileNotFoundError:
        print("❌ Error: 'zebra_puzzles.json' not found. Make sure it's in this folder.")

if __name__ == "__main__":
    inspect_first_puzzle()