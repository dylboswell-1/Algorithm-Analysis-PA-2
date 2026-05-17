"""PA2 starter: implement a SAT solver for CNF formulas.

Clauses are lists of integer literals. For example:
  [1, -3, 4] means x1 OR not x3 OR x4.

Assignments are dictionaries from positive variable numbers to booleans.
"""

from __future__ import annotations

import ast
import sys


def literal_variable(literal):
    """Return the variable number appearing in a literal."""
    return abs(literal)


def literal_required_value(literal):
    """Return the value that makes a literal true."""
    return literal > 0


def evaluate_literal(literal, assignment):
    """Evaluate one literal under a partial assignment.

    Return:
      True if the literal is already true,
      False if the literal is already false,
      None if its variable is not assigned yet.
    """
    variable = literal_variable(literal)
    if variable not in assignment:
        return None
    return assignment[variable] == literal_required_value(literal)


def simplify(clauses, assignment):
    """Simplify clauses under a partial assignment.

    Clauses that are already true disappear. Literals that are already false are
    removed from their clauses. If a clause becomes empty, the current partial
    assignment cannot lead to a solution.
    """
    simplified = []
    for clause in clauses:
        new_clause = []
        clause_satisfied = False

        for literal in clause:
            value = evaluate_literal(literal, assignment)
            if value is True:
                clause_satisfied = True
                break
            if value is None:
                new_clause.append(literal)

        if clause_satisfied:
            continue
        if len(new_clause) == 0:
            return None
        simplified.append(new_clause)

    return simplified


def unit_propagate(clauses, assignment):
    """Repeatedly apply unit clauses.

    This is one of the key algorithmic parts of the assignment.
    """

    # Make a copy so we do not accidentally change the caller's dictionary.
    assignment = assignment.copy()

    while True:
        # First simplify the formula using the assignments we already know.
        clauses = simplify(clauses, assignment)

        # If simplify returns None, a clause became empty.
        # That means the current assignment creates a contradiction.
        if clauses is None:
            return None, None

        # Look for a unit clause, which is a clause with only one literal.
        # Example: [3] forces x3 = True.
        # Example: [-4] forces x4 = False.
        unit_literal = None

        for clause in clauses:
            if len(clause) == 1:
                unit_literal = clause[0]
                break

        # If there are no unit clauses left, propagation is done.
        if unit_literal is None:
            return clauses, assignment

        variable = literal_variable(unit_literal)
        required_value = literal_required_value(unit_literal)

        # If the variable was already assigned the opposite value,
        # then this branch is impossible.
        if variable in assignment and assignment[variable] != required_value:
            return None, None

        # Otherwise, force the variable to the value required
        # by the unit clause.
        assignment[variable] = required_value


def choose_variable(clauses, assignment):
    """Choose an unassigned variable to branch on.

    This simple helper returns the first unassigned variable it sees. You may
    replace it by a smarter heuristic.
    """
    for clause in clauses:
        for literal in clause:
            variable = literal_variable(literal)
            if variable not in assignment:
                return variable
    return None


def sat_solve(clauses, assignment):
    """Solve SAT for a CNF formula by extending the given partial assignment.

    Return a satisfying assignment if one exists. Return None otherwise.
    """

    # First, use unit propagation to apply all forced choices.
    clauses, assignment = unit_propagate(clauses, assignment)

    # If unit propagation found a contradiction, this branch fails.
    if clauses is None or assignment is None:
        return None

    # If no clauses remain, every clause has been satisfied.
    if len(clauses) == 0:
        return assignment

    # Choose an unassigned variable to guess on.
    variable = choose_variable(clauses, assignment)

    # If there is no unassigned variable left, return the current assignment.
    if variable is None:
        return assignment

    # Try setting the chosen variable to True.
    true_assignment = assignment.copy()
    true_assignment[variable] = True

    result = sat_solve(clauses, true_assignment)

    if result is not None:
        return result

    # If True did not work, try setting the variable to False.
    false_assignment = assignment.copy()
    false_assignment[variable] = False

    return sat_solve(clauses, false_assignment)

def print_result(assignment):
    """Print the SAT result using the assignment handout format."""
    print(f'satisfiable: {str(assignment is not None).lower()}')
    print(f'assignment: {assignment}')


def main():
    """Run the solver from the command line on a CNF formula."""
    raw = sys.argv[1] if len(sys.argv) > 1 else sys.stdin.read()
    clauses = ast.literal_eval(raw)
    print_result(sat_solve(clauses, {}))


if __name__ == '__main__':
    main()