from board import Direction, Rotation
from random import Random
import time

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

    @property
    def height(self):
        if self.board.cells:
            return min(y for (x, y) in self.board.cells)    # different from Board().height. Keep tracking the tallest position.
        else:
            return 24
    
    @property
    def falling(self):
        return self.board.falling

    @property
    def score(self):
        if self.board:
            return self.board.score
        else:
            return 0

    def __call__(self):
        return (self.target, self.rotation_target)

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
        return False #self.board.falling.supported(self.board)

    def move(self):
        """ 
        Move the block to the desired column.
        return True if the block lands.
        False if not landed
        """
        if not self.board.falling:
            return True
        
        left = self.board.falling.left
        while self.board.falling and self.target != self.board.falling.left:
            if self.target > self.board.falling.left:
                # no translation or move to the right.
                if self.board.move(Direction.Right) or self.board.falling.supported(self.board):
                    self.target = left
                    return left
                left += 1
            else:
                # move to the left.
                if self.board.move(Direction.Left) or self.board.falling.supported(self.board):
                    self.target = left
                    return True
                left -= 1
        return False #self.board.falling.supported(self.board)

    def try_move(self):
        """
        Apply the move and rotation.
        return True if the action is applied (self.height and self.board.score are updated).
        return False if the action is not (or cannot be) applied.
        """
        if self.board.falling == None:
            return True
           
        if not (self.rotate() or self.move()):
            self.board.move(Direction.Drop)

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

        return result
    
    def choose_action(self, board):
        result = list() # initialisation of the list of actions
        self.candidates = list()
        if (not board.falling):
            # no blocks falling.
            result = Direction.Drop
        else:
            # create clones for each positions that can be falled on.
            horizontal_range = board.width - (board.falling.right - board.falling.left)
            for horizontal in range(0, horizontal_range):
                for orientation in range(4):
                    new_board = board.clone()
                    #new_board.cells = board.cells

                    new_candidate = Candidate(new_board, target=horizontal, rotation=orientation)
                    self.candidates.append(new_candidate)
                    new_candidate.try_move()
            
            # determin the best position for the board (highest score with lowest height).
            list_of_best_candidates = self.min_height(self.max_score(self.candidates))
            best_candidate = self.choose(list_of_best_candidates)
            print(set(board) - set(best_candidate.board))
            
            #print(board.falling.right, board.falling.left)
            if ((best_candidate.target != board.falling.left) or best_candidate.rotation_target):
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
            result.append(Direction.Drop)
        return result
    
    def choose(self, array):
        return array[0]

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
