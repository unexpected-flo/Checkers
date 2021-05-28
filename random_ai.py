from random import randint
from abstract_AI import AI

class RandomAI(AI):
    def play(self, board):
        pot_moves, pot_takes = self.potential_actions(board, self.color)
        if pot_moves:
            guess = randint(0, len(pot_moves)-1)
            (sl, sr), (el, er) = pot_moves[guess]
            return sl, sr, el, er
        if pot_takes:
            guess = randint(0, len(pot_takes)-1)
            node = pot_takes[guess]
            pot_dest = []
            destinations = [node.upper_left, node.upper_right, node.lower_left, node.lower_right]
            for branch in destinations:
                for dest in branch:
                    if dest:
                        pot_dest.append(dest)
            dest_guess = randint(0, len(pot_dest)-1)
            dest = pot_dest[dest_guess]
            sl, sr = node.coords
            el, er = dest.coords
            return sl, sr, el, er

if __name__ == "__main__":

    print(RandomAI.__dict__.keys())
    rand = RandomAI("ia_color", "adv_color")
    print(rand.__dict__.keys())