# tetris
The codes for the tetris coursework for ENGF0002.  
_Requirement:_ Write an auto-player in player.py that can beat RandomPlayer.  
_Marking Criteria:_ Push the player.py to CS Department gitlab instance and an auto-grader will import player.py and test it with 5 fixed (but unknown) sequences of blocks. Each trial is limited to 15 minutes and can use up to 500 MB of memory and half of a CPU core. The number of blocks is 400 so that the game will always finish, thus the algorithm needs to be optimised for higher mark with the same blocks. The process is terminated is exceeded and the trial doesn't count. The final score of this commit is the median of all 5 runs.  
  
_The game have a fixed seed by default so it generates the same sequence of blocks every time. To run the game with random seed, modify the DEFAULT_SEED variable in constants.py_  
