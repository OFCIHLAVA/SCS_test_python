import pytest
from pathlib import Path
from app import (
    parse_dimensions,
    validate_grid,
    load_grid,
    _count_obstacles,
    SqrFinder,
    RectFinder,
    OBSTACLE,
    EMPTY,
)


# ── Helpers ──────────────────────────────────────────────────────────────────


def _write_grid(tmp_path: Path, text: str) -> Path:
    p = tmp_path / "grid.txt"
    p.write_text(text, encoding="utf-8")
    return p


# ── parse_dimensions ─────────────────────────────────────────────────────────


class TestParseDimensions:
    @pytest.mark.parametrize(
        "line, expected",
        [
            ("5 4", (5, 4)),
            ("10 12", (10, 12)),
            (" 3  7 ", (3, 7)),
            ("54", (5, 4)),
            ("19", (1, 9)),
        ],
    )
    def test_valid(self, line: str, expected: tuple[int, int]):
        assert parse_dimensions(line) == expected

    @pytest.mark.parametrize(
        "line",
        [
            "abc",
            "",
            "123",
            "5",
            "0 5",
            "5 0",
            "-1 5",
            "5 -3",
            "0 0",
        ],
    )
    def test_invalid(self, line: str):
        with pytest.raises(ValueError):
            parse_dimensions(line)


# ── validate_grid ────────────────────────────────────────────────────────────


class TestValidateGrid:
    def test_valid_grid(self):
        validate_grid([[".", "X"], ["X", "."]], 2, 2)

    def test_empty_grid(self):
        with pytest.raises(ValueError, match="empty"):
            validate_grid([], 2, 2)

    def test_ragged_rows(self):
        with pytest.raises(ValueError, match="not rectangular"):
            validate_grid([[".", "X"], ["X"]], 2, 2)

    def test_wrong_width(self):
        with pytest.raises(ValueError, match="width"):
            validate_grid([[".", "X", "."], ["X", ".", "X"]], 2, 2)

    def test_wrong_height(self):
        with pytest.raises(ValueError, match="height"):
            validate_grid([[".", "X"]], 2, 2)

    def test_invalid_symbols(self):
        with pytest.raises(ValueError, match="invalid symbols"):
            validate_grid([[".", "Z"], ["X", "."]], 2, 2)

    def test_lowercase_obstacle_accepted(self):
        validate_grid([[".", "x"], ["X", "."]], 2, 2)


# ── _count_obstacles ─────────────────────────────────────────────────────────


class TestCountObstacles:
    @pytest.mark.parametrize(
        "grid, expected",
        [
            ([[".", "."], [".", "."]], 0),
            ([["X", "X"], ["X", "X"]], 4),
            ([["X", "."], [".", "X"]], 2),
            ([["x", "."], [".", "x"]], 2),
            ([["X", "x"]], 2),
        ],
    )
    def test_counts(self, grid: list[list[str]], expected: int):
        assert _count_obstacles(grid) == expected


# ── load_grid ────────────────────────────────────────────────────────────────


class TestLoadGrid:
    def test_valid_file(self, tmp_path: Path):
        p = _write_grid(tmp_path, "3 2\n..X\nX..\n")
        grid, w, h = load_grid(p)
        assert (w, h) == (3, 2)
        assert grid == [[".", ".", "X"], ["X", ".", "."]]

    def test_file_not_found(self, tmp_path: Path):
        with pytest.raises(FileNotFoundError):
            load_grid(tmp_path / "nope.txt")

    def test_empty_file(self, tmp_path: Path):
        p = _write_grid(tmp_path, "")
        with pytest.raises(ValueError, match="empty"):
            load_grid(p)

    def test_bad_dimensions(self, tmp_path: Path):
        p = _write_grid(tmp_path, "abc\n...\n")
        with pytest.raises(ValueError):
            load_grid(p)

    def test_grid_width_mismatch(self, tmp_path: Path):
        p = _write_grid(tmp_path, "2 2\n...\n...\n")
        with pytest.raises(ValueError, match="width"):
            load_grid(p)

    def test_single_digit_dimensions(self, tmp_path: Path):
        p = _write_grid(tmp_path, "32\n...\n.X.\n")
        grid, w, h = load_grid(p)
        assert (w, h) == (3, 2)


# ── SqrFinder internals ─────────────────────────────────────────────────────


class TestSqrFinderInitBorders:
    def test_first_row_and_column(self):
        grid = [[".", "X", "."], [".", ".", "X"], ["X", ".", "."]]
        SqrFinder._init_borders(grid)
        assert grid[0] == ["1", "X", "1"]
        assert [row[0] for row in grid] == ["1", "1", "X"]

    def test_all_obstacles_border(self):
        grid = [["X", "X"], ["X", "."]]
        SqrFinder._init_borders(grid)
        assert grid[0] == ["X", "X"]
        assert grid[1][0] == "X"


class TestSqrFinderSolveRest:
    def test_dp_propagation_all_empty(self):
        grid = [[".", ".", "."], [".", ".", "."], [".", ".", "."]]
        SqrFinder._init_borders(grid)
        SqrFinder._solve_rest(grid)
        assert grid[1][1] == "2"
        assert grid[2][2] == "3"

    def test_obstacle_blocks_propagation(self):
        grid = [[".", "."], [".", "X"]]
        SqrFinder._init_borders(grid)
        SqrFinder._solve_rest(grid)
        assert grid[1][1] == "X"

    def test_neighbour_obstacle_resets_to_one(self):
        grid = [[".", "X"], [".", "."]]
        SqrFinder._init_borders(grid)
        SqrFinder._solve_rest(grid)
        assert grid[1][1] == "1"


class TestSqrFinderRun:
    def test_no_obstacles(self, tmp_path: Path):
        p = _write_grid(tmp_path, "3 3\n...\n...\n...\n")
        assert SqrFinder.run(p) == 9

    def test_all_obstacles(self, tmp_path: Path):
        p = _write_grid(tmp_path, "2 2\nXX\nXX\n")
        assert SqrFinder.run(p) == 0

    def test_mixed(self, tmp_path: Path):
        p = _write_grid(tmp_path, "3 3\n..X\n...\n...\n")
        assert SqrFinder.run(p) == 4

    def test_single_cell_empty(self, tmp_path: Path):
        p = _write_grid(tmp_path, "1 1\n.\n")
        assert SqrFinder.run(p) == 1

    def test_single_cell_obstacle(self, tmp_path: Path):
        p = _write_grid(tmp_path, "1 1\nX\n")
        assert SqrFinder.run(p) == 0

    def test_wide_grid_limited_by_height(self, tmp_path: Path):
        p = _write_grid(tmp_path, "5 2\n.....\n.....\n")
        assert SqrFinder.run(p) == 4  # 2x2

    def test_sample_input(self, tmp_path: Path):
        text = "6 6\nxXXXXX\nxXXXXX\nxX..xX\nxX..XX\nxxxxXX\nxXXXXX\n"
        p = _write_grid(tmp_path, text)
        assert SqrFinder.run(p) == 4

    def test_verticaly_split_room(self, tmp_path: Path):
        p = _write_grid(tmp_path, "5 5\n..x..\n..x..\n..x..\n..x..\n..x..")
        assert SqrFinder.run(p) == 4

    def test_horizontaly_split_room(self, tmp_path: Path):
        p = _write_grid(tmp_path, "5 5\n.....\n.....\nxxxxx\n.....\n.....")
        assert SqrFinder.run(p) == 4

    def test_cross_split_room(self, tmp_path: Path):
        p = _write_grid(tmp_path, "5 5\n..x..\n..x..\nxxxxx\n..x..\n..x..")
        assert SqrFinder.run(p) == 4


# ── RectFinder internals ────────────────────────────────────────────────────


class TestRectFinderScoreFirstRow:
    def test_scores_empty_cells(self):
        row = [".", "X", ".", "."]
        RectFinder._score_first_row(row)
        assert row == ["1", "X", "1", "1"]

    def test_all_obstacles(self):
        row = ["X", "X"]
        RectFinder._score_first_row(row)
        assert row == ["X", "X"]


class TestRectFinderScoreRest:
    def test_vertical_accumulation(self):
        grid = [[".", "."], [".", "."], [".", "."]]
        RectFinder._score_first_row(grid[0])
        RectFinder._score_rest(grid)
        assert grid[2] == ["3", "3"]

    def test_obstacle_resets_count(self):
        grid = [[".", "."], ["X", "."], [".", "."]]
        RectFinder._score_first_row(grid[0])
        RectFinder._score_rest(grid)
        assert grid[2][0] == "1"
        assert grid[2][1] == "3"


class TestRectFinderGetBiggestThisRow:
    @pytest.mark.parametrize(
        "row, expected",
        [
            (["3", "3", "3"], 9),
            (["5"], 5),
            (["2", "X", "2"], 2),
            (["X", "X"], 0),
            (["1", "3", "3"], 6),
        ],
    )
    def test_cases(self, row: list[str], expected: int):
        assert RectFinder._get_biggest_this_row(row) == expected


class TestRectFinderRun:
    def test_no_obstacles(self, tmp_path: Path):
        p = _write_grid(tmp_path, "3 2\n...\n...\n")
        assert RectFinder.run(p) == 6

    def test_all_obstacles(self, tmp_path: Path):
        p = _write_grid(tmp_path, "2 2\nXX\nXX\n")
        assert RectFinder.run(p) == 0

    def test_single_empty(self, tmp_path: Path):
        p = _write_grid(tmp_path, "1 1\n.\n")
        assert RectFinder.run(p) == 1

    def test_wide_single_row(self, tmp_path: Path):
        p = _write_grid(tmp_path, "5 1\n.....\n")
        assert RectFinder.run(p) == 5

    def test_tall_single_column(self, tmp_path: Path):
        p = _write_grid(tmp_path, "1 4\n.\n.\n.\n.\n")
        assert RectFinder.run(p) == 4
