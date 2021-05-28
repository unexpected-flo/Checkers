from abc import ABCMeta, abstractmethod


class AbstractTurn(metaclass=ABCMeta):
    def __init__(self):
        pass

    @abstractmethod
    def play_turn(self, start_line, start_row, end_line, end_row, board):
        """Must return True if the active player turn is finished, returns False if another movement should be done
        after the current one"""
        pass
