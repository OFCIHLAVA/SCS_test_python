# Biggest Square Finder

Finds the largest square area without obstacles in a rectangular grid (room floor). Uses dynamic programming to solve efficiently.

## Usage

bash
python app.py <input_file>

Example:

bash
python app.py test_input.txt

## Input File Format

The input file must follow this structure:

1. **First line** — two integers `M` and `N` representing grid width and height. Can be space-separated (`5 4`) or concatenated for single digits (`54`).
2. **Next N lines** — exactly `M` characters each, representing the grid:
   - `.` — empty space
   - `X` — obstacle (case-insensitive, `x` also accepted)

### Example

```txt
5 4
..X..
.....
.X...
.....
```



This describes a 5-wide, 4-tall room with two obstacles.

## Output

Prints the area (side²) of the largest square that fits in the room without covering any obstacle.