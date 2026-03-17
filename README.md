# Carpet Finder

Finds the largest obstacle-free **square** or **rectangle** that fits in a rectangular grid (room floor). Uses dynamic programming to solve efficiently.

Requires **Python 3.9+**.

## Usage

The app provides two subcommands:

## Find the biggest square

```bash
python app.py square <input_file>
```

## Find the biggest rectangle

```bash
python app.py rectangle <input_file>
```

### Examples

```bash
python app.py square test_input.txt
python app.py rectangle test_input.txt
```

The output is the area (in cm²) of the largest shape that fits without covering any obstacle.

## Input File Format

The input file is a plain text file with the following structure:


<width> <height>
<row 1>

<row 2>

.

.

.

row n
...
<row N>

1. **First line** — two integers: grid width (`M`) and height (`N`).
   - Space-separated for any dimensions: `10 12`
   - Concatenated for single-digit only: `54` (meaning width=5, height=4)
2. **Remaining N lines** — exactly `M` characters each, representing the grid:
   - `.` — empty space (carpet can be placed here)
   - `X` — obstacle (case-insensitive, `x` is also accepted)

### Example Input

A 5×4 room with two obstacles:

5 4

..X..

.....

.X...

.....

A 6×6 room (single-digit concatenated dimensions) mostly filled with obstacles:

66

xXXXXX

xXXXXX

xX.xxX

xX.xXX

xxxxXX

xXXXXX

### Validation

The app validates the input and exits with a clear error if:

- The file is missing or empty
- The dimension line is malformed or contains non-positive values
- Grid rows have inconsistent lengths
- Grid dimensions don't match the declared width/height
- The grid contains characters other than `.`, `X`, or `x`

## How It Works

- **Square mode** — uses a table where each cell stores the side length of the largest square whose bottom-right corner is at that cell. The answer is the maximum value squared.
- **Rectangle mode** — builds a height histogram per column (how many consecutive empty cells above), then for each row scans left/right to find the widest rectangle at each cell's height. The answer is the largest area found.