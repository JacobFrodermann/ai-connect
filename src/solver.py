import unittest

from classes import ParsedProblem, Solution
class Solver:
    """
    Complete symbolic CSP solver for ZebraLogicBench-style puzzles.
    """

    def solve(self, problem: ParsedProblem) -> Solution:
        width, height = problem.size
        n = width  # number of houses

        solution = Solution()
        solution.ppl = [{"properties": {}} for _ in range(n)]
        solution.steps = 0
        solution.ID = problem.ID
        solution.entities = problem.entities

        entities = list(problem.entities)
        domains = {entity: set(range(n)) for entity in entities}

        success = self._backtrack(
            solution,
            entities,
            domains,
            problem.constraints,
            assigned_entities=set()
        )

        return solution if success else Solution()

    def _backtrack(self, solution, entities, domains, constraints, assigned_entities):
        if len(assigned_entities) == len(entities):
            return self._check_constraints(solution, constraints)

        solution.steps += 1
        entity = next(e for e in entities if e not in assigned_entities)

        for house_idx in domains[entity]:
            if entity in solution.ppl[house_idx]["properties"].values():
                continue

            solution.ppl[house_idx]["properties"][entity] = entity
            assigned_entities.add(entity)

            if self._check_constraints(solution, constraints):
                if self._backtrack(solution, entities, domains, constraints, assigned_entities):
                    return True

            del solution.ppl[house_idx]["properties"][entity]
            assigned_entities.remove(entity)

        return False

    @staticmethod
    def _check_constraints(solution, constraints):
        for constraint in constraints:
            if not constraint.isSatisfied(solution):
                return False

        seen = set()
        for house in solution.ppl:
            for value in house["properties"].values():
                if value in seen:
                    return False
                seen.add(value)

        return True

class SolverTest(unittest.TestCase):
    def testSolveBasic(self):
        pass
