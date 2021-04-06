import PySimpleGUI as sg
import string
import checkers_gui as game_gui

alphabet = string.ascii_uppercase
even_color = '#B58863'
odd_color = '#F0D9B5'


def draw_cli_board(game_board):
    for line_nb, line in enumerate(game_board.tiles):
        print(line_nb, [game_gui.cli_display[x.type] if x else "_" for x in line])
        print()  # To try to make the displayed board a bit more square
    print(" ", ["{}".format(x) for x in range(game_board.size)])
    print()


def redraw_board(window, board):
    size = board.size
    for i in range(size):
        for j in range(size):
            color = even_color if (i + j) % 2 else odd_color
            if board.tiles[i][j]:
                piece_image = game_gui.images[board.tiles[i][j].type]
            else:
                piece_image = game_gui.images["empty"]
            elem = window.FindElement(key=(i, j))
            elem.Update(button_color=('white', color),
                        image_filename=piece_image, )
    window.Refresh()


def create_window(game_name, size, board):
    layout = [[sg.T('{}'.format(a), pad=((24, 23), 0), font='Any 13') for a in alphabet[:size]]]
    for i in range(size):
        row = []
        for j in range(size):
            color = even_color if (i + j) % 2 else odd_color
            row. append(sg.RButton(' ', size=(8, 4), key=(i, j), pad=(0, 0), button_color=('white', color)))
        row.append(sg.T(str(size - i) + '   ', pad=((23, 0), 0), font='Any 13'))
        layout.append(row)

    window = sg.Window("{}".format(game_name), layout,  auto_size_buttons=False, finalize=True)
    redraw_board(window, board)
    return window


def get_event(window):
    event, _ = window.read()
    if event in (None, 'Exit'):
        window.close()
        exit()
    return event


if __name__ == "__main__":
    import checkers_rules
    size = 10
    game_board = checkers_rules.initialize_board(size)
    window = create_window("Checkers", size, game_board)
    while True:
        event, _ = window.read()
        print(event)
        if event in (None, 'Exit'):
            break
