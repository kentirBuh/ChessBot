# engine.py
import time
import math
from board import Board, PIECE_VALUES

class Engine:
    def __init__(self):
        self.start_time = 0
        self.time_limit = 3.0

    def evaluate(self, board: Board):
        score = 0

        for piece in board.board.values():
            color = piece[0]
            ptype = piece[1]
            val = PIECE_VALUES[ptype]

            if color == "w":
                score += val
            else:
                score -= val

        return score

    def search(self, board: Board, depth, alpha, beta, maximizing):
        if time.time() - self.start_time > self.time_limit:
            return self.evaluate(board), None

        moves = board.generate_moves(board.turn if maximizing else ("b" if board.turn=="w" else "w"))
        if depth == 0 or not moves:
            return self.evaluate(board), None

        best_move = None

        if maximizing:
            max_eval = -math.inf
            for m in moves:
                new_board = self.copy(board)
                new_board.move_piece(m)

                eval, _ = self.search(new_board, depth-1, alpha, beta, False)

                if eval > max_eval:
                    max_eval = eval
                    best_move = m

                alpha = max(alpha, eval)
                if beta <= alpha:
                    break

            return max_eval, best_move

        else:
            min_eval = math.inf
            for m in moves:
                new_board = self.copy(board)
                new_board.move_piece(m)

                eval, _ = self.search(new_board, depth-1, alpha, beta, True)

                if eval < min_eval:
                    min_eval = eval
                    best_move = m

                beta = min(beta, eval)
                if beta <= alpha:
                    break

            return min_eval, best_move

    def copy(self, board):
        new = Board()
        new.board = board.board.copy()
        new.turn = board.turn
        return new

    def choose_move(self, board: Board):
        self.start_time = time.time()

        best_move = None
        best_score = -math.inf

        depth = 1

        # iterative deepening
        while True:
            if time.time() - self.start_time > self.time_limit:
                break

            score, move = self.search(board, depth, -math.inf, math.inf, True)

            if move:
                best_move = move
                best_score = score

            depth += 1

        return best_move