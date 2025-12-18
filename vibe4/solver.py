import copy

class CSPSolver:
    def __init__(self, variables, domains):
        self.variables = variables
        self.domains = domains
        self.constraints = []
        self.steps = 0
        self.trace = []  # Required for competition

    def add_constraint(self, func, scope):
        self.constraints.append((func, scope))

    def is_consistent(self, assignment, var, value):
        """
        Checks if the current assignment is consistent with all constraints.
        """
        # Temporarily add the new assignment to check consistency
        temp_assignment = assignment.copy()
        temp_assignment[var] = value

        for func, scope in self.constraints:
            # Only check constraints where all variables are assigned/present
            if all(v in temp_assignment for v in scope):
                args = [temp_assignment[v] for v in scope]
                if not func(*args):
                    return False
        return True

    def forward_check(self, assignment, var, value, domains):
        """
        Prunes domains of unassigned variables based on the new assignment.
        Returns a new domain dict or None if a domain becomes empty (failure).
        """
        new_domains = copy.deepcopy(domains)
        new_domains[var] = [value] # Collapsed to single value

        # Iterate over constraints involving this variable
        for func, scope in self.constraints:
            if var in scope:
                # Find the other variable in the constraint (assuming binary constraints mostly)
                others = [v for v in scope if v != var]
                if not others: continue # Unary constraint
                
                other = others[0] # Focus on the neighbor
                if other in assignment: continue # Already assigned

                # Filter the neighbor's domain
                valid_options = []
                for other_val in new_domains[other]:
                    # Check if (value, other_val) is valid
                    args_map = {var: value, other: other_val}
                    
                    # reconstruct args list in order of scope
                    # This is a simplified check logic for binary constraints
                    try:
                        args = [args_map[s] for s in scope]
                        if func(*args):
                            valid_options.append(other_val)
                    except:
                        # Fallback if scope logic is complex
                        valid_options.append(other_val)
                
                if not valid_options:
                    return None # Domain wipeout! Backtrack.
                new_domains[other] = valid_options
        
        return new_domains

    def mrv_heuristic(self, assignment, current_domains):
        """
        Selects unassigned variable with smallest domain size.
        """
        unassigned = [v for v in self.variables if v not in assignment]
        if not unassigned: return None
        # Return variable with minimum remaining values
        return min(unassigned, key=lambda v: len(current_domains[v]))

    def solve(self):
        self.steps = 0
        self.trace = []
        # Initial Forward Check (Arc Consistency on unary constraints)
        return self.backtrack({}, self.domains)

    def backtrack(self, assignment, current_domains):
        # 1. Solution Found
        if len(assignment) == len(self.variables):
            return assignment

        # 2. Select Variable (MRV)
        var = self.mrv_heuristic(assignment, current_domains)

        # 3. Try Values
        # Optimally, we would sort these by LCV (Least Constraining Value), 
        # but purely iterating is often fast enough for Zebra puzzles.
        for value in current_domains[var]:
            self.steps += 1
            
            # Log for Trace Requirement
            self.trace.append({
                "step": self.steps,
                "variable": var,
                "value": value,
                "domain_size": len(current_domains[var])
            })

            # Check Consistency
            if self.is_consistent(assignment, var, value):
                
                # Forward Checking (Lookahead)
                new_domains = self.forward_check(assignment, var, value, current_domains)
                
                if new_domains is not None:
                    assignment[var] = value
                    result = self.backtrack(assignment, new_domains)
                    if result:
                        return result
                    del assignment[var] # Backtrack
        
        return None