class Pawn:

    def __init__(self, color):
        self.owner = color
        self.alive = True
        self.promoted = False
        self.type = "{}_pawn".format(color)

    def promote(self):
        self.promoted = True
        self.type = "{}_queen".format(self.owner)

    def taken(self):
        self.alive = False


if __name__ == "__main__":
    pion = Pawn("white")
    print(pion.__dict__)
    # pion.move(2, 4)
    pion.taken()
    print(pion.__dict__)
