from board import Direction, Rotation
from random import Random

class Candidate():
    def __init__(self, board = None, step = 0, rotation = 0):
        self.board = board
        self.step = step    # the number of horizontal translation required by the block.
        self.rotation = rotation    # the number of anciclockwise rotation required for the block.
        if board:
            self.score = board.score
            self.height = board.height

        else:
            self.score = 0
            self.height = 100

    def rotate(self):
        """
        Rotate the block to the desired orientation.
        """
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

class Sequence():
    def __init__(self, actions=[], score = 0):
        self.score = 0
        self.actions = actions

    def __iter__(self):
        for i in self.actions:
            yield i

    def __list__(self):
        return self.actions

    def __gt__(self, other):
        return self.score > other.score

    def __lt__(self, other):
        return self.score < other.score

    def __eq__(self, other):
        return self.score == other.score

    def __ge__(self, other):
        return self == other or self > other

    def __le__(self, other):
        return self == other or self < other

    def __add__(self, other):
        self.append(other)
        return self

    def __iadd__(self, other):
        self.append(other)

    def append(self, item):
        if isinstance(item, (Direction, Rotation)):
            self.actions.append(item)
        elif isinstance(item, (list, tuple)):
            for i in item:
                self.append(i)

    def copy(self):
        return Sequence(actions=self.actions, score = self.score)

class Player:
    """
    Target score:300
    Current best: 0
    """
    def choose_action(self, board):
        raise NotImplementedError
        
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
        if array == None:
            array = self.candidates
        result = [Candidate()]
        for i in array:
            if i.height < result[0].height:
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
            for rotation in range(4):
                for horizontal in range(-board.falling.left, board.width - board.falling.right + 1):
                    self.candidates.append(Candidate(board.clone(), horizontal, rotation));

            for candidate in self.candidates:
                if candidate.rotate() and candidate.move():
                    if candidate.board.falling == None:
                        candidate.board.score += candidate.board.clean()
                    else:
                        candidate.rotation = 0
                        candidate.step = 0
                else:
                    self.candidates.remove(candidate)
            
            best_score = self.max_score(self.candidates)
            if len(best_score) == 1:
                best_score = self.min_height(best_score)

            best_candidate = best_score[0]
            result = []
            if best_candidate.rotation <= 2:
                result += [Rotation.Anticlockwise] * best_candidate.rotation
            else:
                result += [Rotation.Clockwise]

            if best_candidate.step < 0:
                result += [Direction.Left] * (-best_candidate.step)
            else:
                result += [Direction.Right] * best_candidate.step

            return result

SelectedPlayer = MyPlayer
