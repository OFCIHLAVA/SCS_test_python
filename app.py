OBSTACLE = "X"
EMPTY = "."


def find_biggest_square(grid: list[str]):
    solve_top_left_first_rows(grid)
    solve_rest(grid)


def solve_top_left_first_rows(grid: list[str]):
    # Solve 1st row
    for i, field in enumerate(grid[0]):
        if field.upper() != OBSTACLE:
            grid[0][i] = "1"

    # Solve 1st column
    for row in grid:
        if row[0].upper() != OBSTACLE:
            row[0] = "1"


def solve_rest(grid: list):
    """_summary_

    NOTE: Key is to solve fields from one corner to oposite one. For each field without obstacle, record biggest
     possible square that has its farhest corner in that field. If all 3 neighbour fields closest to the starting corner
     already have a number, use minimum amongst them +1 for this field. If any of these 3 has obstacle in them, put 1 to
     this field. Highest number represents the farthers from the starting corner square corner of the biggest possible
     carpet.

    Args:
        grid (list): List of rows each element representing column of that row.
    """
    for r, row in enumerate(grid):
        for c, column in enumerate(row):
            # Skip solved and obstacles
            if column == EMPTY:
                clues_str_list = [
                    row[c - 1],
                    grid[r - 1][c],
                    grid[r - 1][c - 1],
                ]  # left, top, and top-left diagonal neighbour fields.
                if OBSTACLE in clues_str_list:
                    row[c] = "1"
                    continue
                clues_int_list = [int(c) for c in clues_str_list]
                row[c] = str(min(clues_int_list) + 1)


with open(
    R"/home/Repos-linux/aws_training/exercise/test_input.txt", "r", encoding="utf-8"
) as f:
    data = f.readlines()

dimensions = data.pop(0)

grid = [[char for char in line.strip()] for line in data]

find_biggest_square(grid)
print("Solved:")
for row in grid:
    print(row)

possible_squares_areas = []
for row in grid:
    possible_squares_areas.extend(
        [int(field) for field in row if field not in [OBSTACLE]]
    )

biggest_area_square_possible = max(possible_squares_areas)

print(f"Největší možný čtvercový koberec má plochu: {biggest_area_square_possible} cm.")


def main():

    