import Type 
import pandas as pd
import pyarrow.parquet as pq

def read_row_from_parquet(path: str, row_index: int):
    df = pd.read_parquet(path)  # requires pyarrow or fastparquet
    try:
        row = df.iloc[row_index]
    except IndexError:
        raise IndexError(f"Row index {row_index} out of range (0..{len(df)-1}).")
    return row.to_dict()

def main():
    df: pd.DataFrame = pq.read_table("./Gridmode-00000-of-00001.parquet", columns=["id", "size", "puzzle", "solution"]).to_pandas()
    rawProblems = df.apply(lambda row: Type.RawProblem(row["id"], row["puzzle"]), axis=1)

    parser = Type.Parser()

    parsedProblems = rawProblems.apply(lambda raw: parser.parse(raw))

    solver = Type.Solver()

    solutions = parsedProblems.apply(lambda parsed: solver.solve(parsed))

if __name__ == "__main__":
    main()