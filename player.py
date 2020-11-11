from board import Direction, Rotation
from random import Random

class Candidate():
    def __init__(self, board = None, step = 0, rotation = 0):
        self.board = board
        self.step = step    # the number of horizontal translation required by the block.
        self.rotation = rotation    # the number of anciclockwise rotation required for the block.
    
    @property
    def score(self):
        if self.board:
            return self.board.score
        else:
            return 0

    @property
    def height(self):
        self.board.score += self.board.clean()
        return min(y for (x, y) in self.board.cells)

    def rotate(self):
        """
        Rotate the block to the desired orientation.
        """
        if self.board.falling == None:
            return False

        if self.rotation >= 4:
            self.rotate(self.board, self.rotation - 4)

        elif self.rotation <= 2:
            for i in range(self.rotation):
                if not self.board.rotate(Rotation.Anticlockwise):
                    return False
            return True
        else:
            return self.board.rotate(Rotation.Clockwise) # 3 anticlockwise is equivalent to 1 clockwise rotation.
    
    def move(self):
        """
        Move the block to the desired column.
        """
        if self.board.falling == None:
            return False

        if self.step >= 0:
            for i in range(self.step):
                if not self.board.move(Direction.Right):
                    return False    # The required rotation cannot be done
            return True
        else:
            step = -self.step
            for i in range(step):
                if not self.board.move(Direction.Left):
                    return False    # The required rotation cannot be done
            return True

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
        result = [Candidate()]
        for i in array:
            if i.score > result[0].score:
                result = [i]
            elif i.score == result[0].score:
                result.append(i)
        return result

    def min_height(self, array = None):
        """
        The height at ground is 24, so the higher the board, the smaller the value. returns a list of the lowest boards.
        """
        if array == None:
            array = self.candidates
        result = [Candidate()]
        for i in array:
            if i.height > result[0].height:
                result = [i]
            elif i.height == result[0].height:
                result.append(i)
        return result

    def score(self, board):
        return board.height

    def choose_action(self, board):
        if (not board.cells) or (not board.falling):
            return None
        else:
            # create clones for each positions that can be falled on.
            for orientation in range(4):
                for horizontal in range(-1 - board.falling.left, board.width - board.falling.right + 1):
                    new_board = board.clone()
                    self.candidates.append(Candidate(new_board, step=horizontal, rotation=orientation));
            
            for candidate in self.candidates:
                if candidate.rotate() and candidate.move():
                    # the moves can be done. 
                    if candidate.board.falling == None:
                        # the falling block has landed.
                        candidate.board.score += candidate.board.clean()
                    else:
                        # the falling block hasn't landed yet.
                        pass
                else:
                    # either the move or the rotation cannot be done. remove the candidate.
                    self.candidates.remove(candidate)
            
            # determin the best position for the board (highest score with lowest height).
            best_score = self.max_score(self.candidates)
            if len(best_score) == 1:
                best_score = self.min_height(best_score)
            
            best_candidate = best_score[0]
            result = []
            if not (best_candidate.step == best_candidate.rotation == 0):
                # actions need to be taken.
                if best_candidate.rotation <= 2:
                    result += [Rotation.Anticlockwise] * best_candidate.rotation
                else:
                    result += [Rotation.Clockwise]

                if best_candidate.step < 0:
                    result += [Direction.Left] * (-best_candidate.step)
                else:
                    result += [Direction.Right] * best_candidate.step
            result.append(Direction.Drop)
            self.candidates = []
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
