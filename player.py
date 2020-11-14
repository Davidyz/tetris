from board import Direction, Rotation
from random import Random
import math

def same(array):
    """
    return false if the array is not consist of the same item.
    otherwise return the item.
    """
    reference = array[0]
    for i in array:
        if i != reference:
            return False
    return reference

class Candidate():
    """
    A wrapper of Board().
    Contains some data and function that help choose_action().
    """
    def __init__(self, board = None, target = 0, rotation = 0):
        self.board = board
        self.target = target    # the number of horizontal translation required by the block.
        self.rotation_target = rotation    # the number of anciclockwise rotation required for the block.
        self.rotation_count = 0
        if board.cells:
            self.height = min(y for (x, y) in board.cells)    # different from Board().height. Keep tracking the tallest position.
        else:
            self.height = 24

    @property
    def score(self):
        if self.board:
            return self.board.score
        else:
            return 0

    def __call__(self):
        return (self.target, self.rotation)

    def rotate(self):
        """
        Rotate the block to the desired orientation.
        return True if the block lands.
        False if not land
        """
        if self.board.falling == None:
            return True

        while self.rotation_count < self.rotation_target:
            if self.board.rotate(Rotation.Anticlockwise) or self.board.falling.supported(self.board):
                self.rotation_target = self.rotation_count
                return True
            self.rotation_count += 1
        return self.board.falling.supported(self.board)

    def move(self):
        """ 
        Move the block to the desired column.
        return True if the block lands.
        False if not landed
        """
        if not self.board.falling:
            return True

        while self.board.falling and self.target != self.board.falling.left:
            if self.target > self.board.falling.left:
                # no translation or move to the right.
                if self.board.move(Direction.Right) or self.board.falling.supported(self.board):
                    self.target = self.board.falling.left
                    return True
            else:
                # move to the left.
                if self.board.move(Direction.Left) or self.board.falling.supported(self.board):
                    self.target = self.board.falling.left
                    return True
        return self.board.falling.supported(self.board)

    def try_move(self):
        """
        Apply the move and rotation.
        return True if the action is applied (self.height and self.board.score are updated).
        return False if the action is not (or cannot be) applied.
        """
        if self.board.falling == None:
            return True
        
        try:
            self.height = min(y for (x, y) in self.board.cells)
        except ValueError:
            self.height - 24
        self.falling = self.board.falling
        moved = self.move()
        rotated = self.rotate()
        return moved and rotated

class Player:
    """
    Target score:300
    Current best: 0
    """
    def choose_action(self, board):
        raise NotImplementedError

class MyPlayer(Player):
    def __init__(self):
        self.actions = [Direction.Left, Direction.Right, Direction.Down, Rotation.Anticlockwise, Rotation.Clockwise]
        self.translation = [Direction.Left, Direction.Right, Direction.Down]
        self.rotation = [Rotation.Anticlockwise, Rotation.Clockwise]
        self.candidates = []

    def max_score(self, array = None):
        if array == None:
            array = self.candidates
        best_score = 0
        result = []
        for i in array:
            if i.board.score > best_score:
                result = [i]
                best_score = i.board.score
            elif i.board.score == best_score:
                result.append(i)
            else:
                array.remove(i)
        return result

    def min_height(self, array = None):
        """
        The height at ground is 24, so the higher the board, the smaller the value. returns a list of the lowest boards.
        """
        if array == None:
            array = self.candidates

        best_height = array[0].height
        result = [array[0]]
        for i in array:
            if i.height > best_height:
                result = [i]
                best_height = i.height
            elif i.height == best_height:
                result.append(i)
            else:
                array.remove(i)
        return result

    def choose_action(self, board):
        result = [] # initialisation of the list of actions

        if (not board.falling):
            # no blocks falling.
            result = [Direction.Drop]
        else:
            # create clones for each positions that can be falled on.
            for horizontal in range(board.width - (board.falling.right - board.falling.left)):
                for orientation in range(4):
                    new_board = board.clone()
                    falling = new_board.falling
                    new_candidate = Candidate(new_board, target=horizontal, rotation=orientation)
                    self.candidates.append(new_candidate)
                    new_candidate.try_move()

                    if new_candidate.board.falling:
                        new_candidate.board.move(Direction.Drop)
                    new_candidate.board.score += new_candidate.board.clean()
                    new_candidate.height = min(y for (x,y) in new_candidate.board.cells)
            
            print(list(i.height for i in self.candidates))
            # determin the best position for the board (highest score with lowest height).
            best_candidate = self.max_score(self.min_height(self.candidates))[-1]
            
            if (best_candidate.target != board.falling.left or best_candidate.rotation_target):
                # generate the series of actions need to be taken.
                if best_candidate.rotation_target <= 2:
                    result += [Rotation.Anticlockwise] * best_candidate.rotation_target
                else:
                    result += [Rotation.Clockwise]

                if best_candidate.target < board.falling.left:
                    result += [Direction.Left] * (board.falling.left - best_candidate.target)
                elif best_candidate.target > board.falling.left:
                    result += [Direction.Right] * (best_candidate.target - board.falling.left)
                else:
                    result.append(Direction.Down)
            else:
                result.append(Direction.Down)
        return result

class RandomPlayer(Player):
    def __init__(self, seed=None):
        self.random = Random(seed)

    def choose_action(self, board):
        return self.random.choice([
            Direction.Left,
            Direction.Right,
            Direction.Down,
            Rotation.Anticlockwise,
            Rotation.Clockwise,
            ])

SelectedPlayer = MyPlayer
