class Board:
    def __init__(self, size):
        self.size = size
        self.tiles = []
        for line in range(size):
            row = []
            for _ in range(size):
                row.append(None)
            self.tiles.append(row)

    def add_piece(self, line, row, piece):
        if not self.tiles[line][row]:
            self.tiles[line][row] = piece
        else:
            raise ValueError("Tile already occupied")

    def remove_piece(self, line, row):
        self.tiles[line][row] = None

    def move_piece(self, start_line, start_row, end_line, end_row):
        if self.tiles[start_line][start_row]:
            if not self.tiles[end_line][end_row]:
                self.tiles[end_line][end_row] = self.tiles[start_line][start_row]
                self.tiles[start_line][start_row] = None
            else:
                raise ValueError("Destination tile already occupied")
        else:
            raise ValueError("No piece in origin tile")


if __name__ == "__main__":
    import checkers_pieces

    board = Board(8)
    print(board.tiles)
    board.add_piece(1, 1, checkers_pieces.Pawn("white"))
    board.add_piece(2, 1, checkers_pieces.Pawn("black"))
    print(board.tiles)
    print(board.tiles[1][1] == board.tiles[2][1])
    board.move_piece(1, 1, 2, 2)
    print(board.tiles)
    print(board.tiles[2][2].__dict__)
