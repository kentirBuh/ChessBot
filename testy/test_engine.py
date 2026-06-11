import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from board import Board
from engine import Engine

board = Board()
engine = Engine()

for i in range(20):
    move = engine.choose_move(board)
    print("BOT MOVE:", move)

    board.move_piece(move)

    print("POSITION SIZE:", len(board.board))