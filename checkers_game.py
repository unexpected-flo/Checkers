
import checkers_rules as rules
import gui


class Game:
    def __init__(self, players):
        self.players = players
        self.active_player = players[0]
        self.ongoing = True

    def change_active_player(self):
        for player in self.players:
            if player is not self.active_player:
                self.active_player = player
                break

    def play_turn(self, board, window):
        end_turn = False
        turn = rules.Turn(self.active_player, board)
        while not end_turn:
            start_line, start_row = gui.get_event(window)
            end_line, end_row = gui.get_event(window)
            print(start_line, start_row, end_line, end_row)
            end_turn = turn.play_turn(start_line, start_row, end_line, end_row, board)
            gui.redraw_board(window, board)
            if end_turn:
                self.change_active_player()

    def play_game_cli(self, rules):
        size = rules.board_size
        game_board = rules.initialize_board(size)
        while self.ongoing:
            gui.draw_cli_board(game_board)
            start_line, start_row = [int(x) for x in input().split(sep=",")]


    def play_game_gui(self, rules):
        size = rules.board_size
        game_board = rules.initialize_board(size)
        window = gui.create_window("Checkers", size, game_board)
        while self.ongoing:
            print("{} turn".format(self.active_player))
            self.play_turn(game_board, window)
            finished, winner = rules.game_over(game_board)
            if finished:
                self.ongoing = False
                print("{} won".format(winner))


if __name__ == "__main__":
    gui_enabled = True
    game = Game(rules.players)
    if gui_enabled:
        game.play_game_gui(rules)
    else:
        game.play_game_cli(rules)
