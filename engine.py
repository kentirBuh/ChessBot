import time
import math
import random

PIECE_VALUES = {
    "P": 100,
    "N": 320,
    "B": 330,
    "R": 500,
    "Q": 900,
    "K": 20000
}

CENTER = {"d4", "e4", "d5", "e5"}

FILES = "abcdefgh"


class Engine:
    def __init__(self):
        self.start_time = 0
        self.time_limit = 3.0
        self.tt = {}  # transposition table

    # -----------------------------
    # HASH (very simple Zobrist-like)
    # -----------------------------
    def hash_board(self, board):
        return (str(board.board), board.turn)

    # -----------------------------
    # EVALUATION FUNCTION
    # -----------------------------
    def evaluate(self, board):
        score = 0

        for sq, piece in board.board.items():
            color = piece[0]
            p = piece[1]

            val = PIECE_VALUES[p]

            if color == "w":
                score += val
            else:
                score -= val

            # center control
            if sq in CENTER:
                score += 25 if color == "w" else -25

        return score

    # -----------------------------
    # MOVE ORDERING (VERY IMPORTANT)
    # -----------------------------
    def order_moves(self, moves, board):
        def score_move(m):
            to_sq = m["to"]
            score = 0

            # capture
            if to_sq in board.board:
                score += 1000

            # center
            if to_sq in CENTER:
                score += 50

            # promotion
            if "promotion" in m:
                score += 900

            return score

        return sorted(moves, key=score_move, reverse=True)

    # -----------------------------
    # NEGAMAX (alpha-beta)
    # -----------------------------
    def search(self, board, depth, alpha, beta, color):
        if time.time() - self.start_time > self.time_limit:
            return self.evaluate(board), None

        key = self.hash_board(board)
        if key in self.tt:
            return self.tt[key]

        moves = board.generate_moves(board.turn)
        moves = self.order_moves(moves, board)

        if depth == 0 or not moves:
            val = self.evaluate(board)
            return val, None

        best_move = None
        best_score = -math.inf

        for move in moves:
            new_board = self.copy(board)
            new_board.move_piece(move)

            score, _ = self.search(
                new_board,
                depth - 1,
                -beta,
                -alpha,
                -color
            )

            score = -score

            if score > best_score:
                best_score = score
                best_move = move

            alpha = max(alpha, score)
            if alpha >= beta:
                break

        self.tt[key] = (best_score, best_move)
        return best_score, best_move

    # -----------------------------
    # ITERATIVE DEEPENING
    # -----------------------------
    def choose_move(self, board):
        self.start_time = time.time()
        self.tt.clear()

        best_move = None
        depth = 1

        while True:
            if time.time() - self.start_time > self.time_limit:
                break

            score, move = self.search(
                board,
                depth,
                -math.inf,
                math.inf,
                1
            )

            if move:
                best_move = move

            depth += 1

        return best_move

    # -----------------------------
    # COPY BOARD
    # -----------------------------
    def copy(self, board):
        new = type(board)()
        new.board = board.board.copy()
        new.turn = board.turn
        return new