import math

from abc import ABC, abstractmethod

ROW = 0
POSITION = 1


class BoardException(Exception):
    "The board has errors"
    pass


class Cell:
    key = None
    coordinates = (None, None)
    square_box_number = None
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
        return f"Cell ({self.coordinates[ROW]},{self.coordinates[POSITION]})"

    def __check_value_exist(self, cell_array, value):
        for cell in cell_array:
            if cell.key and cell.key == value:
                return True
        return False

    def __check_value_exist_in_row(self, value):
        # row = self.board.board[self.coordinates[ROW] - 1]
        row = self.board.get_row(self.coordinates)
        return self.__check_value_exist(row, value)

    def __check_value_exist_in_column(self, value):
        # cell_position = self.coordinates[POSITION] - 1
        # column = [row[cell_position] for row in self.board.board]
        column = self.board.get_column(self.coordinates)
        return self.__check_value_exist(column, value)

    def __check_value_exist_in_square_box(self, value):
        # square_box = self.board.square_boxes[str(self.square_box_number)]
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

        return str(result)

    def print_box_numbers(self):
        dashed_string = ('-' * (self.max_value * 2 + 1) + '\n')
        result = '\n' + dashed_string
        result += '\n Box Numbers \n'

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
        self.board[converted_row][converted_position].key = key
        self.not_resolve_cell_count -= 1

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
        print("Start resolving")
        alg = AlgorithmOnlyOnePossibility(self)
        alg.run()
        print("Resolving have been complete")

    def __load_board(self, fname='input.txt'):
        with open(fname, 'r') as f:

            for line_number, line in enumerate(f, 1):
                self.board.append(
                    [Cell(int(x), (line_number, cell_position), self) for cell_position, x in enumerate(line.strip('\n').split(','), 1)]
                    )

        self.max_value = len(self.board)

    def __calc_square_size(self):
        self.square_size = math.sqrt(self.max_value)

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
    board = None

    @abstractmethod
    def __init__(self, board: Board) -> None:
        super().__init__()
        self.board = board

    @abstractmethod
    def run(self):
        pass


class AlgorithmOnlyOnePossibility(Algorithm):
    has_changes = False

    def __init__(self, board: Board) -> None:
        super().__init__(board)

    def __algorithm(self, cell: Cell):
        if self.board.not_resolve_cell_count <= 0:
            return

        if not cell.key and len(cell.possible_values) == 1:
            self.has_changes = True
            self.board.set_key(cell.coordinates, cell.possible_values.pop())
            self.board.remove_possible_values_from_row(cell.coordinates, [cell.key])
            self.board.remove_possible_values_from_column(cell.coordinates, [cell.key])
            self.board.remove_possible_values_from_box(cell.square_box_number, [cell.key])

    def run(self):
        self.has_changes = True
        i = 1
        while self.has_changes:
            print(f"\nIteration {str(i)}")
            print("Start only one possibility algorithm")

            self.has_changes = False
            self.board.for_each_cell(self.__algorithm)

            print(self.board)
            print(f"Not resolve cells: {board.not_resolve_cell_count}")

            i += 1


if __name__ == "__main__":
    print("Inserting sudoku from the file...")
    filename = input("Please enter a filename: ") or 'easy_level.txt'

    board = Board(filename)
    print(board)
    board.print_box_numbers()
    board.resolve()
