import checkers_rules as rules
import gui
import checkers_AI as ai


class Game:
    def __init__(self, players, play_with_ai=True, interface="gui", ai_args=None):
        self.players = players
        self.active_player = players[0]
        self.ongoing = True
        self.interface = interface
        self.play_with_ai = play_with_ai
        if self.play_with_ai:
            self.skynet = ai.ai_types[ai_selected](*ai_args)

    def change_active_player(self):
        for player in self.players:
            if player is not self.active_player:
                self.active_player = player
                break

    def play_turn(self, board, window=None):
        end_turn = False
        turn = rules.Turn(self.active_player, board)
        while not end_turn:
            if self.play_with_ai and self.active_player == self.skynet.color:
                start_line, start_row, end_line, end_row = self.skynet.play(board)
            else:
                start_line, start_row, end_line, end_row = self.get_user_input(window)
            print(start_line, start_row, end_line, end_row)
            end_turn = turn.play_turn(start_line, start_row, end_line, end_row, board)
            self.display_board(board, window)
            if end_turn:
                self.change_active_player()

    def get_user_input(self, window):
        if self.interface == "gui":
            start_line, start_row = gui.get_event(window)
            end_line, end_row = gui.get_event(window)
        elif self.interface == "cli":
            print("input x_start, y_start, x_end, y_end")
            start_line, start_row, end_line, end_row = [int(x) for x in input().split(sep=",")]
        else:
            raise(ValueError("Interface selected invalid, possible choices are \"gui\" or \"cli\""))
        return start_line, start_row, end_line, end_row

    def display_board(self, board, window=None):
        if self.interface == "gui":
            gui.redraw_board(window, board)
        elif self.interface == "cli":
            gui.draw_cli_board(board)
        else:
            raise (ValueError("Interface selected invalid, possible choices are \"gui\" or \"cli\""))

    def play_game(self):
        size = rules.board_size
        game_board = rules.initialize_board(size)
        if self.interface == "gui":
            window = gui.create_window("Checkers", size, game_board)
        else:
            window = None
            self.display_board(game_board)
        while self.ongoing:
            print("{} turn".format(self.active_player))
            self.play_turn(game_board, window)
            game_over, winner = rules.game_over(game_board, self.active_player)
            if game_over:
                self.ongoing = False
                print("{} won".format(winner))


if __name__ == "__main__":
    ai_selected = "minmax"
    ai_settings = (rules.players[1], rules.players[0])
    game = Game(rules.players, play_with_ai=True, interface="gui", ai_args=ai_settings)
    game.play_game()
