import math

from abc import ABC, abstractmethod

ROW = 0
POSITION = 1


class BoardException(Exception):
    "The board has errors"
    pass


class Cell:
    key = None
    square_box_number = None
    coordinates = (None, None)
    possible_values = None
    board = None

    def __init__(self, key, coordinates, board):
        if not key == 0:
            self.key = key

        self.coordinates = coordinates
        self.board = board
        self.possible_values = set()

    def __str__(self):
        return str(self.key) if self.key else ' '

    def __repr__(self):
        key = f' key={self.key}' if self.key else ''
        pos_values = f' possible={self.possible_values}' if self.possible_values else ''
        return f"Cell ({self.coordinates[ROW]},{self.coordinates[POSITION]}){key}{pos_values}"

    def __check_value_exist(self, cell_array, value):
        for cell in cell_array:
            if cell.key and cell.key == value:
                return True
        return False

    def __check_value_exist_in_row(self, value):
        row = self.board.get_row(self.coordinates)
        return self.__check_value_exist(row, value)

    def __check_value_exist_in_column(self, value):
        column = self.board.get_column(self.coordinates)
        return self.__check_value_exist(column, value)

    def __check_value_exist_in_square_box(self, value):
        square_box = self.board.get_square_box(self.square_box_number)
        return self.__check_value_exist(square_box, value)

    def find_possible_cell_value(self):
        for value in range(1, self.board.max_value + 1):
            is_exist_in_row = self.__check_value_exist_in_row(value)
            is_exist_in_column = self.__check_value_exist_in_column(value)
            is_exist_in_box = self.__check_value_exist_in_square_box(value)
            if not is_exist_in_row and not is_exist_in_column and not is_exist_in_box:
                self.possible_values.add(value)


RowType = list[Cell]


class Board:
    board: list[RowType] = []
    max_value = None
    square_size = None
    square_boxes = {}
    not_resolve_cell_count = 0

    def __init__(self, fname):
        self.__load_board(fname)
        self.__calc_square_size()
        self.__set_square_box_for_cells()

        if not self.__check_board_health():
            raise BoardException()

        self.__find_possible_values()

    def __str__(self):
        dashed_string = ('-' * (self.max_value * 2 + 1) + '\n')
        result = '\n' + dashed_string
        for index_i, i in enumerate(self.board, 1):
            result += '|'
            for index_j, cell in enumerate(i, 1):
                result += str(cell)
                result += '|' if index_j % self.square_size == 0.0 else ' '
            result += '\n'
            result += dashed_string if index_i % self.square_size == 0.0 else ''

        result += f'\nNot resolve cells: {self.not_resolve_cell_count}'
        return str(result)

    def print_box_numbers(self):
        dashed_string = ('-' * (self.max_value * 2 + 1) + '\n')
        result = '\n Box Numbers \n'
        result += '\n' + dashed_string

        for index_i, i in enumerate(self.board, 1):
            result += '|'
            for index_j, cell in enumerate(i, 1):
                result += str(cell.square_box_number)
                result += '|' if index_j % self.square_size == 0.0 else ' '
            result += '\n'
            result += dashed_string if index_i % self.square_size == 0.0 else ''

        print(result)

    def get_row(self, cell_coordinates):
        return self.board[cell_coordinates[ROW] - 1]

    def get_column(self, cell_coordinates):
        cell_position = cell_coordinates[POSITION] - 1
        return [row[cell_position] for row in self.board]

    def get_square_box(self, cell_box_number):
        return self.square_boxes[str(cell_box_number)]

    def set_key(self, cell_coordinates, key):
        converted_row = cell_coordinates[ROW] - 1
        converted_position = cell_coordinates[POSITION] - 1
        cell = self.board[converted_row][converted_position]

        if not cell.key:
            cell.key = int(key)
            cell.possible_values.clear()
            self.not_resolve_cell_count -= 1

        self.remove_possible_values_from_row(cell.coordinates, set([int(key)]))
        self.remove_possible_values_from_column(cell.coordinates, set([int(key)]))
        self.remove_possible_values_from_box(cell.square_box_number, set([int(key)]))

    def get_cell(self, cell_coordinates):
        return self.board[cell_coordinates[ROW] - 1][cell_coordinates[POSITION] - 1]

    def remove_possible_values(self, cell_coordinates, values):
        cell = self.get_cell(cell_coordinates)
        cell.possible_values.intersection_update(values)

    def remove_possible_values_from_row(self, cell_coordinates, values):
        if not isinstance(values, set):
            values = set(values)
        row = self.get_row(cell_coordinates)
        for cell in row:
            cell.possible_values.difference_update(values)

    def remove_possible_values_from_column(self, cell_coordinates, values):
        if not isinstance(values, set):
            values = set(values)
        column = self.get_column(cell_coordinates)
        for cell in column:
            cell.possible_values.difference_update(values)

    def remove_possible_values_from_box(self, cell_box_number, values):
        if not isinstance(values, set):
            values = set(values)
        box = self.get_square_box(cell_box_number)
        for cell in box:
            cell.possible_values.difference_update(values)

    def for_each_cell(self, func):
        for row in self.board:
            for cell in row:
                func(cell)

    def resolve(self):
        attempts = 10

        alg = AlgorithmOnlyOnePossibility(self)
        algN = AlgorithmNPossibility(self)
        algPlace = AlgorithmOnlyOnePlace(self)
        algHiddenPairs = AlgorithmHiddenPairs(self)

        print(self)
        print(f"Attempts: {attempts}")

        while (attempts > 0) and (self.not_resolve_cell_count > 0):
            attempts -= 1

            alg.run()
            algN.run()
            algPlace.run()
            algHiddenPairs.run()

            print(f"Not resolve cells: {self.not_resolve_cell_count}")
            print(f"{attempts} attempts left\n")

        print(self)
        if attempts <= 0:
            print("The number of attempts was exceeded.")
            print("Sorry but solution not found. Try add more algorithms or increase the number of attempts.")
        else:
            print("Resolving have been complete")
            print(f"{attempts} attempts left")

    def __load_board(self, fname='input.txt'):
        with open(fname, 'r') as f:

            for line_number, line in enumerate(f, 1):
                self.board.append(
                    [Cell(int(x), (line_number, cell_position), self) for cell_position, x in enumerate(line.strip('\n').split(','), 1)]
                    )

        self.max_value = len(self.board)

    def __calc_square_size(self):
        self.square_size = int(math.sqrt(self.max_value))

    def __set_square_box_for_cells(self):
        for row_number, row in enumerate(self.board, 0):
            row_part = math.floor(float(row_number) / self.square_size) * self.square_size
            for cell in row:
                position_part = math.ceil(float(cell.coordinates[POSITION]) / self.square_size)
                cell.square_box_number = int(row_part + position_part)

                stringify_square_number = str(cell.square_box_number)
                if stringify_square_number in self.square_boxes.keys():
                    self.square_boxes[stringify_square_number].append(cell)
                else:
                    self.square_boxes[stringify_square_number] = [cell]

    def __check_board_health(self):
        if self.max_value <= 0:
            return False

        if not self.square_size % 1 == 0.0:
            return False

        return True

    def __find_possible_values(self):
        for row in self.board:
            for cell in row:
                if cell.key:
                    continue
                self.not_resolve_cell_count += 1
                cell.find_possible_cell_value()


class Algorithm(ABC):
    has_changes: bool = False
    board: Board

    @abstractmethod
    def __init__(self, board: Board) -> None:
        super().__init__()
        self.board = board
        self.has_changes = False

    @abstractmethod
    def run(self):
        pass


class AlgorithmNPossibility(Algorithm):
    def __init__(self, board: Board) -> None:
        super().__init__(board)

    def find_same_cells(self, reference: Cell, row: list[Cell]):
        result = []
        for cell in row:
            if id(reference) == id(cell):
                continue
            if reference.possible_values == cell.possible_values:
                result.append(cell)
        return result

    def __algorithm(self, cell: Cell):
        if self.board.not_resolve_cell_count <= 0:
            return

        row = self.board.get_row(cell.coordinates)
        column = self.board.get_column(cell.coordinates)
        box = self.board.get_square_box(cell.square_box_number)

        if cell.key:
            return

        for n in range(2, (self.board.square_size + 1)):
            if (len(cell.possible_values) == n):
                row_same_cells = self.find_same_cells(cell, row)
                column_same_cells = self.find_same_cells(cell, column)
                box_same_cells = self.find_same_cells(cell, box)
                self._remove_same_possible_values(cell, row, n, row_same_cells)
                self._remove_same_possible_values(cell, column, n, column_same_cells)
                self._remove_same_possible_values(cell, box, n, box_same_cells)

    def _remove_same_possible_values(self, cell, cell_array, n, same_cells):
        if (len(same_cells) == (n - 1)):
            for i in cell_array:
                if i.coordinates == cell.coordinates:
                    continue
                same = False
                for same_cell in same_cells:
                    if i.coordinates == same_cell.coordinates:
                        same = True
                if same:
                    continue
                i.possible_values.difference_update(cell.possible_values)

    def run(self):
        print("Start N possibility algorithm")
        self.board.for_each_cell(self.__algorithm)


class AlgorithmOnlyOnePlace(Algorithm):
    def __init__(self, board: Board) -> None:
        super().__init__(board)

    def _find_another_place(self, cell, cells_array, value):
        for c in cells_array:
            position = c.coordinates[POSITION]
            row = c.coordinates[ROW]

            if (position == cell.coordinates[POSITION]) and (row == cell.coordinates[ROW]):
                continue

            if value in c.possible_values:
                return True
        return False

    def __algorithm(self, cell: Cell):
        if self.board.not_resolve_cell_count <= 0:
            return

        if (not cell) or cell.key or (not cell.possible_values):
            return

        row = self.board.get_row(cell.coordinates)
        column = self.board.get_column(cell.coordinates)
        box = self.board.get_square_box(cell.square_box_number)

        set_copy = cell.possible_values.copy()
        for value in set_copy:

            has_another_place_in_row = self._find_another_place(cell, row, value)
            has_another_place_in_column = self._find_another_place(cell, column, value)
            has_another_place_in_box = self._find_another_place(cell, box, value)

            for has_place in [has_another_place_in_row, has_another_place_in_column, has_another_place_in_box]:
                if not has_place:
                    self.board.set_key(cell.coordinates, value)
                    self.has_changes = True
                    return

    def run(self):
        self.has_changes = True
        i = 1
        while self.has_changes:
            print(f"Start Only One Place algorithm: Iteration {str(i)}")
            self.has_changes = False
            if not (self.board.not_resolve_cell_count <= 0):
                self.board.for_each_cell(self.__algorithm)
            i += 1


class AlgorithmOnlyOnePossibility(Algorithm):

    def __init__(self, board: Board) -> None:
        super().__init__(board)

    def __algorithm(self, cell: Cell):
        if self.board.not_resolve_cell_count <= 0:
            return

        if not cell.key and len(cell.possible_values) == 1:
            self.has_changes = True
            self.board.set_key(cell.coordinates, cell.possible_values.pop())

    def run(self):
        self.has_changes = True
        i = 1
        while self.has_changes:
            print(f"Start Only One Possibility algorithm: Iteration {str(i)}")
            self.has_changes = False
            self.board.for_each_cell(self.__algorithm)
            i += 1


class AlgorithmHiddenPairs(Algorithm):

    def __init__(self, board: Board) -> None:
        super().__init__(board)

    def __find_paired_cell(self, reference, cell_array):
        def __check_only_two_positions(value, cell_array):
            counter = 0
            for cell in cell_array:
                if value in cell.possible_values:
                    counter += 1
            return False if counter != 2 else True

        pairs = []
        reference_values = list(reference.possible_values)

        for i, value in enumerate(reference_values):
            if not __check_only_two_positions(value, cell_array):
                continue

            for j in range(i + 1, len(reference_values)):
                if not __check_only_two_positions(reference_values[j], cell_array):
                    continue

                pair_candidate = {value, reference_values[j]}
                pair_counter = 0
                tmp_pair = {
                    'cell': reference,
                    'pair_values': pair_candidate
                }
                for cell in cell_array:
                    if cell.key:
                        continue
                    if (cell.coordinates != reference.coordinates) and pair_candidate.issubset(cell.possible_values):
                        pair_counter += 1

                if pair_counter != 1:
                    continue
                pairs.append(tmp_pair)

        if pairs:
            if len(pairs) > 1:
                print(len(pairs))
            return pairs
        return None

    def __algorithm(self, cell: Cell):
        if self.board.not_resolve_cell_count <= 0:
            return

        if self.board is None and not isinstance(self.board, Board):
            return

        row = self.board.get_row(cell.coordinates)
        column = self.board.get_column(cell.coordinates)
        box = self.board.get_square_box(cell.square_box_number)

        if cell.key:
            return

        pairs_row = self.__find_paired_cell(cell, row)
        pairs_column = self.__find_paired_cell(cell, column)
        pairs_box = self.__find_paired_cell(cell, box)

        for pair in [pairs_row, pairs_column, pairs_box]:
            if not pair:
                continue
            for d in pair:
                self.board.remove_possible_values(d['cell'].coordinates, d['pair_values'])

    def run(self):
        print("Start hidden pairs algorithm")
        self.board.for_each_cell(self.__algorithm)


if __name__ == "__main__":
    print("Inserting sudoku from the file...")
    filename = input("Please enter a filename: ") or 'hard_level.txt'

    board = Board(filename)
    print(f"Start resolving for {filename}")
    board.resolve()
