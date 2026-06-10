# board.py

FILES = "abcdefgh"
RANKS = "12345678"

PIECE_VALUES = {
    "P": 1, "N": 3, "B": 3,
    "R": 5, "Q": 9, "K": 0
}

def opposite(color):
    return "b" if color == "w" else "w"


class Board:
    def __init__(self):
        self.board = {}
        self.turn = "w"
        self.setup()

    def setup(self):
        # pawns
        for f in FILES:
            self.board[f + "2"] = "wp"
            self.board[f + "7"] = "bp"

        # pieces
        back = ["R", "N", "B", "Q", "K", "B", "N", "R"]
        for i, f in enumerate(FILES):
            self.board[f + "1"] = "w" + back[i]
            self.board[f + "8"] = "b" + back[i]

    def piece_at(self, sq):
        return self.board.get(sq)

    def move_piece(self, move):
        frm, to = move["from"], move["to"]
        piece = self.board.get(frm)
        if not piece:
            return

        self.board[to] = piece
        del self.board[frm]

        # promotion
        if "promotion" in move:
            self.board[to] = self.turn + move["promotion"]

        self.turn = opposite(self.turn)

    # ---------- MOVE GENERATION ----------

    def generate_moves(self, color):
        moves = []

        for sq, piece in self.board.items():
            if piece[0] != color:
                continue

            ptype = piece[1]

            if ptype == "P":
                moves.extend(self.pawn_moves(sq, color))
            elif ptype == "N":
                moves.extend(self.knight_moves(sq, color))
            elif ptype == "B":
                moves.extend(self.sliding_moves(sq, color, [(1,1),(1,-1),(-1,1),(-1,-1)]))
            elif ptype == "R":
                moves.extend(self.sliding_moves(sq, color, [(1,0),(-1,0),(0,1),(0,-1)]))
            elif ptype == "Q":
                moves.extend(self.sliding_moves(
                    sq, color,
                    [(1,0),(-1,0),(0,1),(0,-1),
                     (1,1),(1,-1),(-1,1),(-1,-1)]
                ))
            elif ptype == "K":
                moves.extend(self.king_moves(sq, color))

        return moves

    # ---------- HELPERS ----------

    def in_bounds(self, f, r):
        return 0 <= f < 8 and 0 <= r < 8

    def to_coord(self, f, r):
        return FILES[f] + RANKS[r]

    def from_coord(self, sq):
        return FILES.index(sq[0]), RANKS.index(sq[1])

    def is_enemy(self, piece, color):
        return piece and piece[0] != color

    # ---------- PIECES ----------

    def pawn_moves(self, sq, color):
        moves = []
        f, r = self.from_coord(sq)
        dir = 1 if color == "w" else -1
        start_rank = 1 if color == "w" else 6

        forward = (f, r + dir)
        if self.in_bounds(*forward):
            to_sq = self.to_coord(*forward)
            if to_sq not in self.board:
                moves.append({"piece":"P","from":sq,"to":to_sq})

                # double move
                if r == start_rank:
                    fwd2 = (f, r + 2*dir)
                    to2 = self.to_coord(*fwd2)
                    if to2 not in self.board:
                        moves.append({"piece":"P","from":sq,"to":to2})

        # captures
        for df in [-1, 1]:
            nf, nr = f + df, r + dir
            if self.in_bounds(nf, nr):
                to_sq = self.to_coord(nf, nr)
                if self.is_enemy(self.board.get(to_sq), color):
                    moves.append({"piece":"P","from":sq,"to":to_sq})

        return moves

    def knight_moves(self, sq, color):
        moves = []
        f, r = self.from_coord(sq)
        jumps = [(1,2),(2,1),(-1,2),(-2,1),
                 (1,-2),(2,-1),(-1,-2),(-2,-1)]

        for df, dr in jumps:
            nf, nr = f + df, r + dr
            if self.in_bounds(nf, nr):
                to_sq = self.to_coord(nf, nr)
                piece = self.board.get(to_sq)
                if not piece or self.is_enemy(piece, color):
                    moves.append({"piece":"N","from":sq,"to":to_sq})

        return moves

    def sliding_moves(self, sq, color, dirs):
        moves = []
        f, r = self.from_coord(sq)

        for df, dr in dirs:
            nf, nr = f + df, r + dr
            while self.in_bounds(nf, nr):
                to_sq = self.to_coord(nf, nr)
                piece = self.board.get(to_sq)

                if not piece:
                    moves.append({"piece":"", "from":sq, "to":to_sq})
                else:
                    if self.is_enemy(piece, color):
                        moves.append({"piece":"", "from":sq, "to":to_sq})
                    break

                nf += df
                nr += dr

        return moves

    def king_moves(self, sq, color):
        moves = []
        f, r = self.from_coord(sq)

        for df in [-1,0,1]:
            for dr in [-1,0,1]:
                if df == 0 and dr == 0:
                    continue
                nf, nr = f + df, r + dr
                if self.in_bounds(nf, nr):
                    to_sq = self.to_coord(nf, nr)
                    piece = self.board.get(to_sq)
                    if not piece or self.is_enemy(piece, color):
                        moves.append({"piece":"K","from":sq,"to":to_sq})

        return moves