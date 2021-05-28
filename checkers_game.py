import checkers_rules as rules
import gui
import ai_list as ai


class Player:
    def __init__(self, color, human, ai_selected=None, ai_args=None):
        self.color = color
        self.human = human
        if not human:
            self.skynet = ai.ai_types[ai_selected](*ai_args)

    def select_move(self, board, window):
        if self.human:
            return Game.get_user_input(game, window)
        else:
            return self.skynet.play(board)


class Game:
    def __init__(self, players, interface="gui"):
        self.players = players
        self.active_player = players[0]
        self.ongoing = True
        self.interface = interface

    def change_active_player(self):
        for player in self.players:
            if player is not self.active_player:
                self.active_player = player
                break

    def play_turn(self, board, window=None):
        end_turn = False
        turn = rules.Turn(self.active_player.color, board)
        while not end_turn:
            start_line, start_row, end_line, end_row = self.active_player.select_move(board, window)
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
            print("input start line, start column, end line, end column")
            start_line, start_row, end_line, end_row = [int(x) for x in input().split(sep=",")]
        else:
            raise(ValueError("Interface selected invalid, possible choices are \"gui\" or \"cli\""))
        return start_line, start_row, end_line, end_row

    def display_board(self, board, window=None):
        if self.interface == "gui":
            gui.redraw_board(window, board)
        elif self.interface == "cli":
            gui.draw_cli_board(board)

    def play_game(self):
        size = rules.board_size
        game_board = rules.initialize_board(size)
        if self.interface == "gui":
            window = gui.create_window("Checkers", size, game_board)
        elif self.interface == "cli":
            window = None
            self.display_board(game_board)
        else:
            window = None
            print("game_start")
        while self.ongoing:
            print("{} turn".format(self.active_player.color))
            self.play_turn(game_board, window)
            game_over, winner = rules.game_over(game_board, self.active_player.color)
            if game_over:
                self.ongoing = False
                print("{} won".format(winner))


if __name__ == "__main__":
    player1_ai = "random"
    player1_ai_settings = (rules.players[0], rules.players[1])
    player2_ai = "random"
    player2_ai_settings = (rules.players[1], rules.players[0])
    player1 = Player(rules.players[0], False, player1_ai, player1_ai_settings)
    player2 = Player(rules.players[1], False, player2_ai, player2_ai_settings)
    players = [player1, player2]
    game = Game(players, interface="gui")
    game.play_game()
