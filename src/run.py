import Type 
import pandas as pd
import pyarrow.parquet as pq
from argparse import ArgumentParser

def read_row_from_parquet(path: str, row_index: int):
    df = pd.read_parquet(path)  # requires pyarrow or fastparquet
    try:
        row = df.iloc[row_index]
    except IndexError:
        raise IndexError(f"Row index {row_index} out of range (0..{len(df)-1}).")
    return row.to_dict()

def main():
    argParse = ArgumentParser()
    argParse.add_argument("-f", "--file", type=str, help="Path to the Parquet file containing problems.", dest="file")
    argParse.add_argument("-gm", "--GridMode", type=bool, dest="grid_mode")
    argParse.add_argument("-mc", "--MultipleChoice", type=bool, dest="multiple_choice")

    args = argParse.parse_args()

    df = pd.DataFrame()
    rawProblems = pd.Series(dtype=object)
    if (args.grid_mode):
        df: pd.DataFrame = pq.read_table(args.file, columns=["id", "size", "puzzle", "solution"]).to_pandas()
        rawProblems = df.apply(lambda row: Type.RawProblem(row["id"], row["puzzle"], size=row["size"]), axis=1)
    elif (args.multiple_choice):
        df: pd.DataFrame = pq.read_table(args.file, columns=["id", "text", "size", "question", "choiches"]).to_pandas()
        rawProblems = df.apply(lambda row: Type.RawMultipleChoiceProblem(row["id"], row["text"], size=row["size"], question=row["question"], choiches=row["choiches"]), axis=1)

    parser = Type.Parser()

    parsedProblems = rawProblems.apply(lambda raw: parser.parseGridmode(raw) if args.grid_mode else parser.parseMultipleChoice(raw))

    solver = Type.Solver()

    solutions = parsedProblems.apply(lambda parsed: solver.solve(parsed))

if __name__ == "__main__":
    main()