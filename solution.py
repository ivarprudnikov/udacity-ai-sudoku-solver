assignments = []

rows = 'ABCDEFGHI'
cols = '123456789'

def cross(A, B):
    "Cross product of elements in A and elements in B."
    return [s+t for s in A for t in B]

boxes = cross(rows, cols)

row_units = [cross(r, cols) for r in rows]
column_units = [cross(rows, c) for c in cols]
square_units = [cross(rs, cs) for rs in ('ABC','DEF','GHI') for cs in ('123','456','789')]
unitlist = row_units + column_units + square_units
units = dict((s, [u for u in unitlist if s in u]) for s in boxes)
peers = dict((s, set(sum(units[s],[]))-set([s])) for s in boxes)

def assign_value(values, box, value):
    """
    Please use this function to update your values dictionary!
    Assigns a value to a given box. If it updates the board record it.
    """

    # Don't waste memory appending actions that don't actually change any values
    if values[box] == value:
        return values

    values[box] = value
    if len(value) == 1:
        assignments.append(values.copy())
    return values

def sorted_string(v):
    return ''.join(sorted(v))

def naked_twins(values):
    """Eliminate values using the naked twins strategy.
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}

    Returns:
        the values dictionary with the naked twins eliminated from peers.
    """

    for unit in unitlist:
        twins = []
        unit_values = { box_name: values[box_name] for box_name in unit }
        # sort values for later equality check so that '12' and '21' become `12` and `12`
        # here (k,''.join(sorted(v))) makes tuple with sorted value string
        # needs to be wrapped in `dict()` as iteration produces tuples
        sorted_values_with_2_possibilities = dict([(k,sorted_string(v)) for (k,v) in unit_values.items() if len(v) == 2])

        # find naked twins in this unit
        if len(sorted_values_with_2_possibilities) > 1:
            values_seen = []
            for val in sorted_values_with_2_possibilities.values():
                if (val in values_seen) and (val not in twins):
                    twins.append(val)
                values_seen.append(val)

        # Eliminate the naked twins as possibilities for their peers
        if len(twins) > 0:
            for box_name in unit:
                if sorted_string(values[box_name]) not in twins:
                    for twin in twins:
                        assign_value(values, box_name, values[box_name].translate({ord(x): '' for x in twin}))

    return values


def grid_values(grid):
    """
    Convert grid into a dict of {square: char} with '123456789' for empties.
    Args:
        grid(string) - A grid in string form.
    Returns:
        A grid in dictionary form
            Keys: The boxes, e.g., 'A1'
            Values: The value in each box, e.g., '8'. If the box has no value, then the value will be '123456789'.
    """
    chars = []
    digits = '123456789'
    for c in grid:
        if c in digits:
            chars.append(c)
        if c == '.':
            chars.append(digits)
    assert len(chars) == 81
    return dict(zip(boxes, chars))

def display(values):
    """
    Display the values as a 2-D grid.
    Args:
        values(dict): The sudoku in dictionary form
    """
    width = 1+max(len(values[s]) for s in boxes)
    line = '+'.join(['-'*(width*3)]*3)
    for r in rows:
        print(''.join(values[r+c].center(width)+('|' if c in '36' else '')
                      for c in cols))
        if r in 'CF': print(line)
    return

def eliminate(values):
    solved_values = [box for box in values.keys() if len(values[box]) == 1]
    for box in solved_values:
        digit = values[box]
        for peer in peers[box]:
            values[peer] = values[peer].replace(digit,'')
    return values

def only_choice(values):
    for unit in unitlist:
        for digit in '123456789':
            dplaces = [box for box in unit if digit in values[box]]
            if len(dplaces) == 1:
                values[dplaces[0]] = digit
    return values

def reduce_puzzle(values):
    solved_values = [box for box in values.keys() if len(values[box]) == 1]
    stalled = False
    while not stalled:
        solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])
        values = eliminate(values)
        values = only_choice(values)
        solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])
        stalled = solved_values_before == solved_values_after
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False
    return values

def search(values):
    "Using depth-first search and propagation, create a search tree and solve the sudoku."
    # First, reduce the puzzle using the previous function
    reduced = reduce_puzzle(values)

    if reduced == False:
        return reduced

    # get list of key value tuples, where multiple values exist
    moreThanOneValue = [(k,v) for (k,v) in reduced.items() if len(v) > 1]

    # return if everything is solved
    if len(moreThanOneValue) == 0:
        return reduced

    # sort by amount of unslved values, first one has the least
    unsolvedSorted = sorted(moreThanOneValue, key=lambda tupleItem: len(tupleItem[1]))

    # Choose one of the unfilled squares with the fewest possibilities
    boxName = unsolvedSorted[0][0]
    boxValues = unsolvedSorted[0][1]
    for guessedValue in boxValues:
        alternativeClone = reduced.copy()
        alternativeClone[boxName] = guessedValue
        guessedResolved = search(alternativeClone)
        if guessedResolved:
            return guessedResolved

    return False

def solve(grid):
    """
    Find the solution to a Sudoku grid.
    Args:
        grid(string): a string representing a sudoku grid.
            Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    Returns:
        The dictionary representation of the final sudoku grid. False if no solution exists.
    """

if __name__ == '__main__':
    diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    display(solve(diag_sudoku_grid))

    try:
        from visualize import visualize_assignments
        visualize_assignments(assignments)

    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')
