from board import Board
from engine import Engine

board = Board()
engine = Engine()

for i in range(10):
    move = engine.choose_move(board)
    print("BOT MOVE:", move)

    board.move_piece(move)

    print("POSITION SIZE:", len(board.board))