from types import ParsedProblem, Solution
class Solver:
    """
    Complete symbolic CSP solver for ZebraLogicBench-style puzzles.
    """

    def __init__(self):
        self.steps = 0

    def solve(self, problem: ParsedProblem) -> Solution:
        self.steps = 0

        width, height = problem.size
        n = width  # number of houses

        solution = Solution()
        solution.var = [{"properties": {}} for _ in range(n)]

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

        self.steps += 1
        entity = next(e for e in entities if e not in assigned_entities)

        for house_idx in domains[entity]:
            if entity in solution.var[house_idx]["properties"].values():
                continue

            solution.var[house_idx]["properties"][entity] = entity
            assigned_entities.add(entity)

            if self._check_constraints(solution, constraints):
                if self._backtrack(solution, entities, domains, constraints, assigned_entities):
                    return True

            del solution.var[house_idx]["properties"][entity]
            assigned_entities.remove(entity)

        return False

    def _check_constraints(self, solution, constraints):
        for constraint in constraints:
            if not constraint.isSatisfied(solution):
                return False

        seen = set()
        for house in solution.var:
            for value in house["properties"].values():
                if value in seen:
                    return False
                seen.add(value)

        return True