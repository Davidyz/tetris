from board import Board, Direction, Rotation
from constants import BOARD_WIDTH, BOARD_HEIGHT, INTERVAL
from player import Player, SelectedPlayer, RandomPlayer, MyPlayer
from adversary import RandomAdversary


def run(seed, player):
    board = Board(BOARD_WIDTH, BOARD_HEIGHT)
    adversary = RandomAdversary(seed=seed)

    for move in board.run(player=player, adversary=adversary):
        pass

    return board.score


if __name__ == "__main__":
    index = 0
    signed = []
    weights = []
    for i in range(5):
        player = MyPlayer()

        print(run(42, RandomPlayer()))
