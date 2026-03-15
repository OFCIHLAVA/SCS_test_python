import argparse
from pathlib import Path

OBSTACLE = "X"
EMPTY = "."


def find_biggest_square(grid: list[list[str]]) -> None:
    """Solve the grid in-place to find the biggest square without obstacles."""
    solve_top_left_first_rows(grid)
    solve_rest(grid)


def solve_top_left_first_rows(grid: list[list[str]]) -> None:
    """Initialize first row and first column of the DP grid.

    Any non-obstacle cell in the first row or column can only form a 1x1 square,
    so it gets value "1".
    """
    for i, field in enumerate(grid[0]):
        if field.upper() != OBSTACLE:
            grid[0][i] = "1"

    for row in grid:
        if row[0].upper() != OBSTACLE:
            row[0] = "1"


def solve_rest(grid: list[list[str]]) -> None:
    """Solve remaining fields using dynamic programming.

    NOTE: Key is to solve fields from one corner to opposite one (this app starts in top left). For each field without
     obstacle, record biggest possible square that has its farthest corner in that field. If all 3 neighbour fields
     closest to the starting corner already have a number, use minimum amongst them +1 for this field. If any of these
     3 has obstacle in them, put 1 to this field. Highest number represents the farthest from the starting corner square
     corner of the biggest possible carpet.
    """
    for r, row in enumerate(grid):
        for c, column in enumerate(row):
            if column.upper() == EMPTY:
                neighbours: list[str] = [
                    row[c - 1],
                    grid[r - 1][c],
                    grid[r - 1][c - 1],
                ]  # left, top, and top-left diagonal neighbour fields.
                if any(n.upper() == OBSTACLE for n in neighbours):
                    row[c] = "1"
                    continue
                min_neighbour: int = min(int(n) for n in neighbours)
                row[c] = str(min_neighbour + 1)


def find_biggest_rectangle(grid: list[list[str]]) -> None:
    """Solve the grid in-place to find the biggest rectangle without obstacles."""
    score_first_row(grid[0])
    get_tallest_rectangle_from_fields(grid)


def score_first_row(first_row):
    for i, c in enumerate(first_row):
        if c == EMPTY:
            first_row[i] = "1"


def score_rest(grid):
    for row in grid:
        print(row)

    for i, row in enumerate(grid):
        print(f"resim {i}tou row - {row}")
        for j, column in enumerate(row):
            print(f"resim {j}ty column - {column}")
            # Ignore obstacles
            if column == EMPTY:
                if grid[i - 1][j] != OBSTACLE:
                    print(f"incrementing: {row[j]}")
                    print(f"pricitam : {grid[i - 1][j]}")
                    row[j] = str(int(grid[i - 1][j]) + 1)
                else:
                    row[j] = "1"


def get_tallest_rectangle_from_fields(grid):
    # TODO - put here logic to find highest from cosequent c cominations


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments with square/rectangle subcommands."""
    parser = argparse.ArgumentParser(
        description="Find the biggest shape without obstacles in a grid."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    for name, help_text in [
        ("square", "Find the biggest square without obstacles."),
        ("rectangle", "Find the biggest rectangle without obstacles."),
    ]:
        sub = subparsers.add_parser(name, help=help_text)
        sub.add_argument(
            "input_file",
            type=Path,
            help="Path to the input file containing the grid.",
        )

    return parser.parse_args()


def validate_grid(grid: list[list[str]], width: int, height: int) -> None:
    """Validate the parsed grid against expected dimensions and content."""
    if not grid:
        raise ValueError("ERROR - Grid is empty, no rows found.")

    row_lengths = set(len(row) for row in grid)
    if len(row_lengths) != 1:
        raise ValueError(
            "ERROR - Input grid is not rectangular. Rows have different lengths."
        )

    (actual_width,) = row_lengths

    if actual_width != width:
        raise ValueError(
            f"ERROR - Input grid width {actual_width} does not match expected width {width}."
        )

    if len(grid) != height:
        raise ValueError(
            f"ERROR - Input grid height {len(grid)} does not match expected height {height}."
        )

    symbols_present = {symbol for row in grid for symbol in row}
    invalid = symbols_present - {OBSTACLE, EMPTY}
    if invalid:
        raise ValueError(
            f"ERROR - Input grid contains invalid symbols: {invalid}. Only '{EMPTY}' and '{OBSTACLE}' are allowed."
        )


def parse_dimensions(line: str) -> tuple[int, int]:
    """Parse dimension line into (width, height).

    Supports two formats:
    - Space-separated: "10 12" (required for multi-digit numbers)
    - No space: "54" (single-digit only, first char = width, second = height)
    """
    try:
        parts = line.strip().split()
        if len(parts) == 2:
            width, height = int(parts[0]), int(parts[1])
        elif len(parts) == 1 and len(parts[0]) == 2:
            width, height = int(parts[0][0]), int(parts[0][1])
        else:
            raise ValueError
    except ValueError:
        raise ValueError(
            "ERROR - First line must contain two numbers M and N (width and height). "
            "Use 'M N' (space-separated) for multi-digit dimensions, or 'MN' for single-digit."
        )
    if width <= 0 or height <= 0:
        raise ValueError("ERROR - Dimensions must be positive integers.")
    return width, height


def load_grid(input_file: Path) -> tuple[list[list[str]], int, int]:
    """Load and validate grid from input file. Returns (grid, width, height)."""
    if not input_file.is_file():
        raise FileNotFoundError(f"ERROR - File not found: {input_file}")

    with open(input_file, "r", encoding="utf-8") as f:
        data = f.readlines()

    if not data:
        raise ValueError("ERROR - Input file is empty.")

    width, height = parse_dimensions(data.pop(0))
    grid: list[list[str]] = [list(line.strip()) for line in data]
    validate_grid(grid, width, height)
    return grid, width, height


def run_square(input_file: Path) -> int:
    """Find the biggest square without obstacles and print the result."""
    grid, width, height = load_grid(input_file)

    count_obstacles: int = sum(row.count(OBSTACLE) for row in grid)

    if not count_obstacles:
        area: int = min(height, width) ** 2
        print(
            f"There are no obstacles in this room. Can fit a carpet with area of {area} cm2."
        )
        return area
    if count_obstacles == height * width:
        print(
            "There are only obstacles in this room. Can fit no carpet in here, unless you have a flying one."
        )
        return 0

    find_biggest_square(grid)

    biggest_side: int = max(
        int(field) for row in grid for field in row if field.upper() != OBSTACLE
    )
    area = biggest_side**2
    print(f"Biggest possible square carpet has an area of: {area} cm2.")
    return area


def run_rectangle(input_file: Path) -> int:
    """Find the biggest rectangle without obstacles. ."""
    grid, width, height = load_grid(input_file)

    count_obstacles: int = sum(row.count(OBSTACLE) for row in grid)

    if not count_obstacles:
        area: int = height * width
        print(
            f"There are no obstacles in this room. Can fit a carpet with area of {area} cm2."
        )
        return area
    if count_obstacles == height * width:
        print(
            "There are only obstacles in this room. Can fit no carpet in here, unless you have a flying one."
        )
        return 0

    find_biggest_rectangle(grid)


def main() -> int:
    """Entry point — dispatch to square or rectangle based on subcommand."""
    args = parse_args()

    if args.command == "square":
        return run_square(args.input_file)
    elif args.command == "rectangle":
        return run_rectangle(args.input_file)

    return 0


if __name__ == "__main__":
    main()
