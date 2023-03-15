# Sudoku

## Launch

`python app.py`

The program will prompt you to enter the name of the file with the initial data. If you do not enter a name, the initial data will be taken from the file `hard_level.txt `.

## Algorithms

First of all, the program calculates what values are possible for each of the cells.
Next, the algorithms are executed in turn until the puzzle is solved or until
the number of attempts ends.
4 algorithms are used to solve the puzzle.
If desired, you can extend this list.

### Algorithm 1: The only possible value in the cell

The program searches for cells with the only possible value and writes the value to the cell.

### Algorithm 2: The only possible position in the block

The program searches the blocks for the only possible position for specific value in block. Cells may has multiple possible values.
Each block must contain all set of values without exceptions.

### Algorithm 3: Multiple cells with the same set of possible values

If there are several cells with the same set of possible values in block, then there cannot be these values in the other cells of the block. Program exclude unnecessary possible values from the cell block.

### Algorithm 4: Hidden pairs of possible values

The algorithm searches for pairs of cells with same pair of possible values within a single block. Two possible values in these pairs of cells mast be missing in other cells of the block. If there are other possible values in these cells, they will be removed from the candidate list.

## Scalability

When I wrote the code, I add the possibility for solving a puzzle of 16 *16, 25 *25, and more.
But I didn't test it. The program calculates the maximum value for cell, calculates blocks depending on the maximum value.

## Performance

Between readability and performance, I chose readability. I tried to make the methods atomic, and without complicated logic. I isolated the work of the algorithms. Each algorithm starts sorting through the cells from the beginning to the end. With this architecture, you can easily add new algorithms and change old ones. This will not affect the rest of the algorithms.
The lowest-performing algorithm is the "Search for hidden pairs" O(N^3).