from board import Direction, Rotation
from random import Random, choice
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
    def mean_height(self):

        cells = {i:[24] for i in range(self.board.width)}
        for (x, y) in self.board.cells:
            if y != 24:
                cells[x].append(y)

        height = []
        for i in cells:
            height.append(max(cells[i]))
        return sum(height) / len(height)

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
    
    @property
    def holes(self):
        """
        try to count the number of holes.
        """
        number = 0
        cells = {i:[24] for i in range(self.board.width)}
        for (x, y) in self.board.cells:
            cells[x].append(y)

        for column in cells:
            if cells[column] == [24]:
                continue
            temp_column = cells[column]
            temp_column.sort()
            temp_column = list(temp_column[i] for i in range(len(temp_column) - 1, -1, -1))
                

            for cell in range(len(temp_column) - 1):
                number += temp_column[cell] - temp_column[cell + 1] - 1

        return number

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
        
        moved = self.move()
        rotated = self.rotate()
        landed = moved or rotated
        if not landed:
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
        self.candidates = []
    
    def min_holes(self, array = None):
        """
        return candidates with minimum number of holes.
        """
        if array == None:
            array = self.candidates
        
        best_hole = 10 * 24
        result = []
        
        for i in array:
            if i.holes < best_hole:
                result = [i]
                best_hole = i.holes
            elif i.holes == best_hole:
                result.append(i)
        
        return result

    def max_score(self, array = None):
        """
        return candidates with highest scores.
        """
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

    def min_mean_height(self, array = None):
        """
        The height at ground is 24, so the higher the board, the smaller the value. returns a list of the lowest boards.
        """
        if array == None:
            array = self.candidates

        best_height = array[0].mean_height
        result = [array[0]]
        
        for i in array:
            if i.mean_height > best_height:
                result = [i]
                best_height = i.mean_height
            elif i.mean_height == best_height:
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
            result.append(Direction.Drop)
        else:
            # create clones for each positions that can be falled on.
            horizontal_range = board.width - (board.falling.right - board.falling.left)
            for horizontal in range(horizontal_range):
                for orientation in range(4):
                    new_board = board.clone()
                    new_candidate = Candidate(new_board, target=horizontal, rotation=orientation)
                    self.candidates.append(new_candidate)
                    new_candidate.try_move()
            
            # determin the best position for the board (highest score with lowest height).
            best_candidate = self.choose(self.min_height(self.min_mean_height(self.min_holes(self.max_score(self.candidates)))))
            
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
            result.append(Direction.Drop)
        return result
    
    def choose(self, array):
        return choice(array)   # tested to score better for some reason.

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
