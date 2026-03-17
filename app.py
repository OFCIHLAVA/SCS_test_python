import argparse
import logging
from pathlib import Path

logger: logging.Logger = logging.getLogger(__name__)

OBSTACLE = "X"
EMPTY = "."


class SqrFinder:
    """Finds the biggest square without obstacles in a grid using DP."""

    @staticmethod
    def run(input_file: Path) -> int:
        """Find the biggest square without obstacles and print the result."""
        grid, width, height = load_grid(input_file)

        count_obstacles: int = _count_obstacles(grid)
        if not count_obstacles:
            area: int = min(height, width) ** 2
            logger.info(
                "There are no obstacles in this room. "
                "Can fit a carpet with area of %d cm2.",
                area,
            )
            return area
        if count_obstacles == height * width:
            logger.info(
                "There are only obstacles in this room. "
                "Can fit no carpet in here, unless you have a flying one."
            )
            return 0

        SqrFinder._solve(grid)

        biggest_side: int = max(
            int(field) for row in grid for field in row if field.upper() != OBSTACLE
        )
        area = biggest_side**2
        logger.info("Biggest possible square carpet has an area of: %d cm2.", area)
        return area

    @staticmethod
    def _solve(grid: list[list[str]]) -> None:
        """Solve the grid in-place to find the biggest square without obstacles."""
        SqrFinder._init_borders(grid)
        SqrFinder._solve_rest(grid)

    @staticmethod
    def _init_borders(grid: list[list[str]]) -> None:
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

    @staticmethod
    def _solve_rest(grid: list[list[str]]) -> None:
        """Solve remaining fields using dynamic programming.

        Solve fields from top-left to bottom-right. For each
        non-obstacle field, record the biggest possible square that
        has its farthest corner in that field. If all three neighbour
        fields closest to the starting corner already have a number,
        use the minimum amongst them plus one. If any neighbour is an
        obstacle, set this field to one. The highest number represents
        the side length of the biggest possible square carpet.
        """
        for r, row in enumerate(grid):
            if r == 0:
                continue
            for c, column in enumerate(row):
                if c == 0:
                    continue
                if column == EMPTY:
                    neighbours: list[str] = [
                        row[c - 1],
                        grid[r - 1][c],
                        grid[r - 1][c - 1],
                    ]
                    if any(n.upper() == OBSTACLE for n in neighbours):
                        row[c] = "1"
                        continue
                    min_neighbour: int = min(int(n) for n in neighbours)
                    row[c] = str(min_neighbour + 1)


class RectFinder:
    """Finds the biggest rectangle without obstacles in a grid."""

    @staticmethod
    def run(input_file: Path) -> int:
        """Find the biggest rectangle without obstacles."""
        grid, width, height = load_grid(input_file)

        count_obstacles: int = _count_obstacles(grid)
        if not count_obstacles:
            area: int = height * width
            logger.info(
                "There are no obstacles in this room. "
                "Can fit a carpet with area of %d cm2.",
                area,
            )
            return area
        if count_obstacles == height * width:
            logger.info(
                "There are only obstacles in this room. "
                "Can fit no carpet in here, unless you have a flying one."
            )
            return 0

        return RectFinder._solve(grid)

    @staticmethod
    def _solve(grid: list[list[str]]) -> int:
        """Solve the grid in-place to find the biggest rectangle without obstacles."""
        RectFinder._score_first_row(grid[0])
        RectFinder._score_rest(grid)
        for row in grid:
            logger.debug("%s", row)
        biggest: int = 0
        for row in grid:
            logger.debug("Checking row: %s for biggest rectangle", row)
            biggest_this_row: int = RectFinder._get_biggest_this_row(row)
            if biggest_this_row > biggest:
                biggest = biggest_this_row
        logger.info(
            "Biggest possible rectangle carpet has an area of: %d cm2.",
            biggest,
        )
        return biggest

    @staticmethod
    def _score_first_row(first_row: list[str]) -> None:
        """Score the first row in-place, marking empty cells as '1'."""
        for i, c in enumerate(first_row):
            if c == EMPTY:
                first_row[i] = "1"

    @staticmethod
    def _score_rest(grid: list[list[str]]) -> None:
        """Score remaining rows by counting consecutive empty cells above.

        Each empty cell gets a score equal to the cell above it plus one,
        or '1' if the cell above is an obstacle.
        """
        for i, row in enumerate(grid):
            if i == 0:
                continue
            for j, column in enumerate(row):
                if column == EMPTY:
                    field_above: str = grid[i - 1][j]
                    if field_above.upper() != OBSTACLE:
                        row[j] = str(int(field_above) + 1)
                    else:
                        row[j] = "1"

    @staticmethod
    def _get_biggest_this_row(row: list[str]) -> int:
        """Find the largest rectangle area anchored in a single row.

        For each scored cell, expand left and right while neighbours
        have scores greater than or equal to the current cell, then
        compute the rectangle area as width times the cell score.
        """
        max_area_rectangles_this_row: list[int] = [0]
        for i, field in enumerate(row):
            if field.upper() == OBSTACLE:
                continue
            checked_field_score: int = int(field)
            popped_from_here: int = 0
            subrow: list[str] = [f for f in row]

            fields_to_left: list[str] = subrow[:i]
            fields_to_right: list[str] = subrow[i + 1 :]
            while fields_to_left:
                popped: str = fields_to_left.pop()
                if popped.upper() == OBSTACLE:
                    break
                if int(popped) >= checked_field_score:
                    popped_from_here += 1
                else:
                    break
            while fields_to_right:
                popped = fields_to_right.pop(0)
                if popped.upper() == OBSTACLE:
                    break
                if int(popped) >= checked_field_score:
                    popped_from_here += 1
                else:
                    break
            if (
                popped_from_here + 1 == checked_field_score
            ):  # This would be a square - ignore it
                continue
            biggest_area_rect_this_field: int = (
                popped_from_here + 1
            ) * checked_field_score
            max_area_rectangles_this_row.append(biggest_area_rect_this_field)
        return max(max_area_rectangles_this_row)


def _count_obstacles(grid: list[list[str]]) -> int:
    """Count total obstacle cells in the grid."""
    return sum(row.count(OBSTACLE) + row.count(OBSTACLE.lower()) for row in grid)


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

    row_lengths: set[int] = set(len(row) for row in grid)
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

    symbols_present: set[str] = {symbol for row in grid for symbol in row}
    invalid: set[str] = symbols_present - {OBSTACLE, OBSTACLE.lower(), EMPTY}
    if invalid:
        raise ValueError(
            f"ERROR - Input grid contains invalid symbols: {invalid}. "
            f"Only '{EMPTY}' and '{OBSTACLE}' are allowed."
        )


def parse_dimensions(line: str) -> tuple[int, int]:
    """Parse dimension line into (width, height).

    Supports two formats:
    - Space-separated: "10 12" (required for multi-digit numbers)
    - No space: "54" (single-digit only, first char = width, second = height)
    """
    try:
        parts: list[str] = line.strip().split()
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
        data: list[str] = f.readlines()

    if not data:
        raise ValueError("ERROR - Input file is empty.")

    width, height = parse_dimensions(data.pop(0))
    grid: list[list[str]] = [list(line.strip()) for line in data]
    validate_grid(grid, width, height)
    return grid, width, height


def main() -> int:
    """Entry point — dispatch to square or rectangle based on subcommand."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    args: argparse.Namespace = parse_args()

    if args.command == "square":
        SqrFinder.run(args.input_file)
    elif args.command == "rectangle":
        RectFinder.run(args.input_file)

    return 0


if __name__ == "__main__":
    main()
