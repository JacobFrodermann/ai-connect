import sys

import pandas as pd
import pyarrow.parquet as pq

from argparse import ArgumentParser
from parser import Parser
from solver import Solver
from classes import RawProblem, Solution
import json


def read_row_from_parquet(path: str, row_index: int):
	df = pd.read_parquet(path)  # requires pyarrow or fastparquet
	try:
		row = df.iloc[row_index]
	except IndexError:
		raise IndexError(f"Row index {row_index} out of range (0..{len(df)-1}).")
	return row.to_dict()


def readGridMode(row) -> RawProblem:
	return RawProblem(row["id"], row["puzzle"], size=row["size"])
def readMC(row) -> RawProblem :
	return  RawProblem(row["id"], row["puzzle"], question=row["question"], choiches=row["choices"])

def answerGridMode(sol: Solution):
	header = list(sol.entities)
	asDict = {
		"header": header,
		"rows": []
	}
	for i in range(len(sol.ppl)):
		row = []
		for entity in header:
			row.append(sol.ppl[i].get(entity))

	print(f"{sol.ID}|{json.dumps(asDict)}|{sol.steps}")
	pass

def main():
	argParse = ArgumentParser()
	argParse.add_argument("-f", "--file", type=str, help="Path to the Parquet file containing problems.", dest="file")
	argParse.add_argument("-gm", "--GridMode", type=bool, dest="grid_mode")
	argParse.add_argument("-mc", "--MultipleChoice", type=bool, dest="multiple_choice")

	args = argParse.parse_args()

	if not (args.grid_mode or args.multiple_choice):
		print("no mode provided")
		sys.exit(1)

	df = pd.DataFrame()
	rawProblems = pd.Series(dtype=object)

	if args.grid_mode:
		df: pd.DataFrame = pq.read_table(args.file, columns=["id", "size", "puzzle", "solution"]).to_pandas().head(100)
		rawProblems = df.apply(readGridMode , axis=1)
	elif args.multiple_choice:
		df: pd.DataFrame = pq.read_table(args.file, columns=["id", "puzzle", "question", "choices"]).to_pandas().head(100)
		rawProblems = df.apply(readMC , axis=1)

	parser = Parser()

	parsedProblems = rawProblems.apply(lambda raw: parser.parseGridmode(raw) if args.grid_mode else parser.parseMultipleChoice(raw))

	print(len(parsedProblems))

	solver = Solver()

	solutions = parsedProblems.apply(lambda parsed: solver.solve(parsed))


	if args.grid_mode:
		solutions.apply(answerGridMode)

if __name__ == "__main__":
	main()
