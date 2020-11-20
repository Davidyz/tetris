from board import Direction, Rotation
from random import Random, choice
import time
import multiprocessing as mp

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
        
        # correct the number of rotations required (shouldn't be necessary, just in case the logics in try_move goes wrong. increase the tolerance of other coding).
        while rotation > 3 or rotation < 0:
            if rotation > 3:
                rotation -= 4
            else:
                rotation += 4
        if self.board.falling and self.board.falling.bottom - self.board.falling.top == self.board.falling.right - self.board.falling.left == 1:
            rotation = 0
        elif self.board.falling and min(self.board.falling.right - self.board.falling.left, self.board.falling.bottom - self.board.falling.top) == 0 and rotation >= 2:
            rotation -= 2

        self.rotation_target = rotation    # the number of anciclockwise rotation required for the block.
        self.rotation_count = 0
        self.cells = {i:[] for i in range(self.board.width)}

        # parameters for the move of the current block.
        self.bottom_holes = -1
        self.mean_height = -1
        self.var_height = -1
        self.holes = -1
        self.range = -1
        self.score = 0

        # parameters for the best move of the next block
        self.next_mean_height = -1 
        self.next_var_height = -1
        self.next_holes = 240
        self.next_bottom_holes = -1
        self.next_range = -1
        
        self.weight = 100 # lower is better

    def cal_weight(self):
        """
        Generate the weight for the move.
        """
        #coefficients = [998,                    2,                      10,                          200,                            150,                          -300] 72418
        coefficients = [1001,                    2.03,                      10.02,                          205,                            150,                          -296]
        parameters = [self.get_holes() / 230 , self.get_range() / 23, self.get_var_height() / 144, self.get_mean_height() / 240, self.get_bottom_holes() / 100, self.score / 16]
        self.weight = sum(coefficients[i] * parameters[i] for i in range(len(coefficients)))
        return self.weight

    def get_mean_height(self):
        """
        Return the mean height (next block if applicable)
        """
        if self.next_mean_height != -1:
            return self.next_mean_height
        return self.mean_height

    def get_var_height(self):
        """
        Return the equivalence of the variance of heights (next block if applicable).
        """
        if self.next_var_height != -1:
            return self.next_var_height
        return self.var_height

    def get_holes(self):
        """
        Return the number of holes (empty space under cells) after a move (next block if applicable).
        """
        if self.next_holes != 240:
            return self.next_holes
        return self.holes

    def get_bottom_holes(self):
        """
        Return the number of holes at the bottom line after a move (next block if applicable).
        """
        if self.next_bottom_holes != -1:
            return self.next_bottom_holes
        return self.bottom_holes

    def get_range(self):
        """
        Return the range (max - min) of height (next block if applicable).
        """
        if self.next_range != -1:
            return self.next_range
        return self.range

    def cal_range(self):
        """
        Calculate the range (max - min) of height from the board.
        """
        peaks = []
        for i in self.cells:
            if self.cells[i]:
                peaks.append(min(self.cells[i]))
            else:
                peaks.append(24)
        self.range = max(peaks) - min(peaks)
        return self.range

    def update_cells(self):
        """
        Generate a dict for the cells according to column number.
        Store this data since this is used in many functions so it is more efficient to store it rather than generating every time.
        """
        self.cells = {i:[] for i in range(self.board.width)}
        for (x, y) in self.board.cells:
            self.cells[x].append(y)
        return self.cells

    def cal_var_height(self):
        """
        Calculate a equivalence (to avoid division which should be more expensive) of the variance of height.
        """
        height = []
        for i in self.cells:
            if self.cells[i] == []:
                height.append(24)
                continue
            height.append(min(self.cells[i]))

        # modified equiation to save time on computation. divition is too expensive.
        self.cal_var_height = sum(i**2 for i in height) * len(height) - (sum(height)) ** 2
        return self.cal_var_height

    def cal_bottom_holes(self):
        """
        Calculate the number of holes at the bottom of the board.
        """
        count = 0
        for (x, y) in self.board.cells:
            if y == 23:
                count += 1
        self.bottom_holes = self.board.width - count
        return self.board.width - count

    def cal_mean_height(self):
        """
        Calculate the mean height of the board.
        """
        cells = {i:[] for i in range(self.board.width)}
        
        height = []
        for i in self.cells:
            if self.cells[i] != []:
                height.append(min(self.cells[i]))
            else:
                height.append(24)
        self.mean_height = 24 - sum(height) / len(height)
        return self.mean_height

    @property
    def falling(self):
        return self.board.falling
    
    def cal_holes(self):
        """ 
        try to count the number of holes.
        """
        number = 0
        for column in self.cells:
            if not self.cells[column]:
                continue
            temp_column = self.cells[column]
            temp_column.sort()
            temp_column = list(temp_column[i] for i in range(len(temp_column) - 1, -1, -1))
            
            if temp_column[0] < 23:
                number += 23 - temp_column[0]

            for cell in range(len(temp_column) - 1):
                number += temp_column[cell] - temp_column[cell + 1] - 1
        
        self.holes = number
        return number

    def __call__(self):
        return (self.target, self.rotation_target)

    def rotate(self):
        """
        Rotate the block to the desired orientation.
        return True if the block lands.
        False if not landed
        """
        if self.board.falling == None:
            return True
        
        while self.rotation_target > 3 or self.rotation_target < 0:
            if self.rotation_target > 3:
                self.rotation_target -= 4
                continue
            self.rotation_target += 4

        while self.rotation_count < self.rotation_target:
            if self.board.rotate(Rotation.Anticlockwise):
                self.rotation_target = self.rotation_count
                return True
            self.rotation_count += 1
        return False

    def move(self):
        """ 
        Move the block to the desired column.
        return True if the block lands.
        False if not landed
        """
        if not self.board.falling:
            return True
        
        left = self.board.falling.left
        while self.target + (self.board.falling.right - self.board.falling.left) >= self.board.width:
            self.target -= 1

        while self.board.falling and self.target != self.board.falling.left:
            if self.target > self.board.falling.left:
                # no translation or move to the right.
                if self.board.move(Direction.Right):
                    self.target = left
                    return left
                left += 1
            else:
                # move to the left.
                if self.board.move(Direction.Left):
                    self.target = left
                    return True
                left -= 1
        return False

    def try_move(self, nested = False):
        """
        Apply the move and rotation.
        nested is True if the call is based on a board with no Board().next block, which means this is a nested simulation that work on the next block.
        False if this is simulating the falling block.
        """
        if self.board.falling == None:
            return
        
        initial_score = self.board.score
        moved = self.move()
        rotated = self.rotate()
        landed = moved or rotated
        if not landed:
            self.board.move(Direction.Drop)
        self.update_cells()
        final_score = self.board.score
        
        # update parameters
        self.holes = self.cal_holes()
        self.bottom_holes = self.cal_holes()
        self.mean_height = self.cal_mean_height()
        self.var_height = self.cal_var_height()
        self.range = self.cal_range()
        self.board.next == None
        
        if self.board.falling and self.board.next == None and not nested:
            # find out the best move for the next block
            subsequent_actions = SelectedPlayer().choose_action(board=self.board)

            # apply the best move for the next block
            target = self.board.falling.left + subsequent_actions.count(Direction.Right) - subsequent_actions.count(Direction.Left)
            rotation_target = max(subsequent_actions.count(Rotation.Anticlockwise), subsequent_actions.count(Rotation.Clockwise) * 3)
            next_candidate = Candidate(self.board.clone(), target = target, rotation=rotation_target)
            next_candidate.try_move(True)
            self.next_range = next_candidate.range
            self.next_holes = next_candidate.holes
            self.next_var_height = next_candidate.var_height
            self.next_bottom_holes = next_candidate.bottom_holes
            self.next_mean_height = next_candidate.mean_height

            # obtain the score after the placement of the next block.
            final_score = next_candidate.score

        self.score = (final_score - initial_score) // 100
        self.weight = self.cal_weight()

class Player:
    """
    Target score:300
    Current best: 0
    """
    def choose_action(self, board):
        raise NotImplementedError

class MyPlayer(Player):
    def __init__(self):
        self.candidates = []    # stores the candidates of possible moves.
    
    def min_range(self, array = None):
        """
        return candidates with smallest range (max - min) of height.
        """
        if array == None:
            array = self.candidates
        
        if len(array) <= 1:
            return array

        best_range = 24
        result = []
        
        for i in array:
            if i.get_range() < best_range:
                result = [i]
                best_range = i.get_range()
            elif i.get_range() == best_range:
                result.append(i)
        
        return result

    def min_holes(self, array = None):
        """
        return candidates with minimum number of holes.
        """
        if array == None:
            array = self.candidates
        
        if len(array) <= 1:
            return array

        best_hole = 10 * 24
        result = []
        
        for i in array:
            if i.get_holes() < best_hole:
                result = [i]
                best_hole = i.get_holes()
            elif i.get_holes() == best_hole:
                result.append(i)
        
        return result

    def max_score(self, array = None):
        """
        return candidates with highest scores.
        """
        if array == None:
            array = self.candidates
        
        if len(array) <= 1:
            return array

        best_score = 0
        result = []
        
        for i in array:
            if i.board.score > best_score:
                result = [i]
                best_score = i.board.score
            elif i.board.score == best_score:
                result.append(i)
        
        return result

    def min_bottom_holes(self, array = None):
        """
        find candidates with least holes at the bottom line.
        """
        if array == None:
            array = self.candidates

        if len(array) <= 1:
            return array

        best_num = array[0].get_bottom_holes()
        result = [array[0]]
        
        for i in array:
            if i.get_bottom_holes() < best_num:
                result = [i]
                best_num = i.get_bottom_holes()
            elif i.get_bottom_holes() == best_num:
                result.append(i)

        return result

    def min_var_height(self, array = None):
        """
        find candidates with lowest variances of the heights of each column.
        """
        if array == None:
            array = self.candidates

        if len(array) <= 1:
            return array

        best_var = array[0].get_var_height()
        result = [array[0]]
        
        for i in array:
            if i.get_var_height() < best_var:
                result = [i]
                best_var = i.get_var_height()
            elif i.get_var_height() == best_var:
                result.append(i)

        return result

    def min_mean_height(self, array = None):
        """
        Returns a list of the lowest boards.
        """
        if array == None:
            array = self.candidates

        if len(array) <= 1:
            return array

        best_height = array[0].get_mean_height()
        result = [array[0]]
        
        for i in array:
            if i.get_mean_height() < best_height:
                result = [i]
                best_height = i.get_mean_height()
            elif i.get_mean_height() == best_height:
                result.append(i)

        return result

    def min_weight(self, array = None):
        """
        determine a list of candidate with lowest weight.
        """
        if array == None:
            array = self.candidates

        if len(array) <= 1:
            return array

        least_weight = array[0].weight
        result = [array[0]]

        if len(array) > 1:
            for i in range(1, len(array)):
                if array[i].weight < least_weight:
                    least_weight = array[i].weight
                    result = [array[i]]
                elif array[i].weight == least_weight:
                    result.append(array[i])

        return result

    def choose_action(self, board):
        """
        Where all the 'magic' takes place.
        """
        result = list() # initialisation of the list of actions
        self.candidates = list()    # make sure the list is empty for each new block.
        
        if (not board.falling):
            # no blocks falling.
            result.append(Direction.Drop)
        else:
            # create clones for each positions that can be falled on.
            for horizontal in range(board.width):
                for orientation in range(4):
                    new_board = board.clone()
                    new_candidate = Candidate(new_board, target=horizontal, rotation=orientation)
                    self.candidates.append(new_candidate)
                    new_candidate.try_move()

            # determin the best position for the board according to their weight.

            best_candidates = self.min_mean_height(self.min_holes(self.max_score(self.min_weight(self.candidates))))
            best_candidate = best_candidates[0]

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
