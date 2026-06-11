# board.py

from turtle import color


FILES = "abcdefgh"
RANKS = "12345678"


def opposite(color):
    return "b" if color == "w" else "w"


class Board:
    def __init__(self):
        self.board = {}
        self.turn = "w"

        self.en_passant = None

        self.castling = {
            "wK": True,
            "wR_kingside": True,
            "wR_queenside": True,
            "bK": True,
            "bR_kingside": True,
            "bR_queenside": True
        }

        self.setup()

    def setup(self):
        # pawns
        for f in FILES:
            self.board[f + "2"] = "wP"
            self.board[f + "7"] = "bP"

        # pieces
        back = ["R", "N", "B", "Q", "K", "B", "N", "R"]

        for i, f in enumerate(FILES):
            self.board[f + "1"] = "w" + back[i]
            self.board[f + "8"] = "b" + back[i]

    def copy(self):
        new = Board.__new__(Board)

        new.board = self.board.copy()
        new.turn = self.turn
        new.en_passant = self.en_passant
        new.castling = self.castling.copy()
        return new

    def piece_at(self, sq):
        return self.board.get(sq)

    def move_piece(self, move):
        frm = move["from"]
        to = move["to"]

        piece = self.board.get(frm)
        if not piece:
            return

        # =========================
        # EN PASSANT
        # =========================
        if piece[1] == "P" and self.en_passant and to == self.en_passant:

            self.board[to] = piece
            del self.board[frm]

            f_from, r_from = self.from_coord(frm)
            f_to, r_to = self.from_coord(to)

            direction = -1 if piece[0] == "w" else 1

            cap_r = r_to + direction
            cap_sq = self.to_coord(f_to, cap_r)

            self.board.pop(cap_sq, None)

            self.en_passant = None
            self.turn = opposite(self.turn)
            return

        # reset en passant
        self.en_passant = None

        # =========================
        # NORMAL MOVE
        # =========================
        self.board[to] = piece
        del self.board[frm]

        # =========================
        # CASTLING - MOVE THE ROOK
        # =========================
        if move.get("castling"):
            if to == "g1":
                self.board["f1"] = self.board.pop("h1")
            elif to == "c1":
                self.board["d1"] = self.board.pop("a1")
            elif to == "g8":
                self.board["f8"] = self.board.pop("h8")
            elif to == "c8":
                self.board["d8"] = self.board.pop("a8")

        # =========================
        # PROMOTION
        # =========================
        if "promotion" in move:
            self.board[to] = piece[0] + move["promotion"]

        # =========================
        # UPDATE CASTLING RIGHTS
        # =========================
        if piece == "wK":
            self.castling["wK"] = False
            self.castling["wR_queenside"] = False
        elif piece == "bK":
            self.castling["bK"] = False
            self.castling["bR_queenside"] = False

        for sq, flag in (
            ("h1", "wK"), ("a1", "wR_queenside"),
            ("h8", "bK"), ("a8", "bR_queenside"),
        ):
            if frm == sq or to == sq:
                self.castling[flag] = False

        # =========================
        # SET EN PASSANT TARGET
        # =========================
        if piece[1] == "P":
            frm_r = int(frm[1])
            to_r = int(to[1])

            if abs(to_r - frm_r) == 2:
                mid_r = (frm_r + to_r) // 2
                self.en_passant = to[0] + str(mid_r)

        self.turn = opposite(self.turn)

        # =====================================================
        # CHECK DETECTION
        # =====================================================

    def king_square(self, color):
        target = color + "K"

        for sq, piece in self.board.items():
            if piece == target:
                return sq

        return None

    def is_square_attacked(self, square, by_color):
        f, r = self.from_coord(square)

        # -------------------------
        # Pawn attacks
        # -------------------------

        pawn_dir = -1 if by_color == "w" else 1

        for df in (-1, 1):
            nf = f + df
            nr = r + pawn_dir

            if self.in_bounds(nf, nr):
                sq = self.to_coord(nf, nr)

                if self.board.get(sq) == by_color + "P":
                    return True

        # -------------------------
        # Knight attacks
        # -------------------------

        jumps = [
            (1, 2), (2, 1),
            (-1, 2), (-2, 1),
            (1, -2), (2, -1),
            (-1, -2), (-2, -1)
        ]

        for df, dr in jumps:
            nf = f + df
            nr = r + dr

            if self.in_bounds(nf, nr):
                sq = self.to_coord(nf, nr)

                if self.board.get(sq) == by_color + "N":
                    return True

        # -------------------------
        # Rook / Queen attacks
        # -------------------------

        rook_dirs = [
            (1, 0), (-1, 0),
            (0, 1), (0, -1)
        ]

        for df, dr in rook_dirs:
            nf = f + df
            nr = r + dr

            while self.in_bounds(nf, nr):
                sq = self.to_coord(nf, nr)
                piece = self.board.get(sq)

                if piece:
                    if (
                        piece[0] == by_color
                        and piece[1] in ("R", "Q")
                    ):
                        return True

                    break

                nf += df
                nr += dr

        # -------------------------
        # Bishop / Queen attacks
        # -------------------------

        bishop_dirs = [
            (1, 1), (1, -1),
            (-1, 1), (-1, -1)
        ]

        for df, dr in bishop_dirs:
            nf = f + df
            nr = r + dr

            while self.in_bounds(nf, nr):
                sq = self.to_coord(nf, nr)
                piece = self.board.get(sq)

                if piece:
                    if (
                        piece[0] == by_color
                        and piece[1] in ("B", "Q")
                    ):
                        return True

                    break

                nf += df
                nr += dr

        # -------------------------
        # King attacks
        # -------------------------

        for df in (-1, 0, 1):
            for dr in (-1, 0, 1):
                if df == 0 and dr == 0:
                    continue

                nf = f + df
                nr = r + dr

                if self.in_bounds(nf, nr):
                    sq = self.to_coord(nf, nr)

                    if self.board.get(sq) == by_color + "K":
                        return True

        return False

    def in_check(self, color):
        king = self.king_square(color)

        if king is None:
            return False

        return self.is_square_attacked(
            king,
            opposite(color)
        )

    # =====================================================
    # MOVE GENERATION
    # =====================================================

    def generate_moves(self, color):
        pseudo_moves = []

        for sq, piece in list(self.board.items()):
            if piece[0] != color:
                continue

            ptype = piece[1]

            if ptype == "P":
                pseudo_moves.extend(
                    self.pawn_moves(sq, color)
                )

            elif ptype == "N":
                pseudo_moves.extend(
                    self.knight_moves(sq, color)
                )

            elif ptype == "B":
                pseudo_moves.extend(
                    self.sliding_moves(
                        sq,
                        color,
                        "B",
                        [(1, 1), (1, -1),
                         (-1, 1), (-1, -1)]
                    )
                )

            elif ptype == "R":
                pseudo_moves.extend(
                    self.sliding_moves(
                        sq,
                        color,
                        "R",
                        [(1, 0), (-1, 0),
                         (0, 1), (0, -1)]
                    )
                )

            elif ptype == "Q":
                pseudo_moves.extend(
                    self.sliding_moves(
                        sq,
                        color,
                        "Q",
                        [
                            (1, 0), (-1, 0),
                            (0, 1), (0, -1),
                            (1, 1), (1, -1),
                            (-1, 1), (-1, -1)
                        ]
                    )
                )

            elif ptype == "K":
                pseudo_moves.extend(
                    self.king_moves(sq, color)
                )

        legal_moves = []

        for move in pseudo_moves:
            copy_board = self.copy()

            copy_board.move_piece(move)

            if not copy_board.in_check(color):
                legal_moves.append(move)

        return legal_moves

    # =====================================================
    # HELPERS
    # =====================================================

    def in_bounds(self, f, r):
        return 0 <= f < 8 and 0 <= r < 8

    def to_coord(self, f, r):
        return FILES[f] + RANKS[r]

    def from_coord(self, sq):
        return FILES.index(sq[0]), RANKS.index(sq[1])

    def is_enemy(self, piece, color):
        return piece and piece[0] != color

    # =====================================================
    # PIECE MOVES
    # =====================================================

    def pawn_moves(self, sq, color):
        moves = []

        f, r = self.from_coord(sq)

        direction = 1 if color == "w" else -1
        start_rank = 1 if color == "w" else 6

        # one square forward
        forward = (f, r + direction)

        if self.in_bounds(*forward):
            to_sq = self.to_coord(*forward)

            if to_sq not in self.board:
                moves.append({
                    "piece": "P",
                    "from": sq,
                    "to": to_sq
                })

                # two squares forward
                if r == start_rank:
                    fwd2 = (f, r + 2 * direction)
                    to2 = self.to_coord(*fwd2)

                    if to2 not in self.board:
                        moves.append({
                            "piece": "P",
                            "from": sq,
                            "to": to2
                        })

        # captures
        for df in (-1, 1):
            nf = f + df
            nr = r + direction

            if self.in_bounds(nf, nr):
                to_sq = self.to_coord(nf, nr)

                if self.is_enemy(self.board.get(to_sq), color):
                    moves.append({
                        "piece": "P",
                        "from": sq,
                        "to": to_sq
                    })

        # =====================================================
        # EN PASSANT
        # =====================================================

        if self.en_passant:
            ep_f, ep_r = self.from_coord(self.en_passant)

            # pion musi być obok pionowej kolumny celu
            if abs(ep_f - f) == 1:

                # poprawny rząd dla en passant:
                # white: 5th rank (r == 4)
                # black: 4th rank (r == 3)
                if (color == "w" and r == 4) or (color == "b" and r == 3):

                    moves.append({
                        "piece": "P",
                        "from": sq,
                        "to": self.en_passant,
                        "en_passant": True
                    })

        return moves

    def knight_moves(self, sq, color):
        moves = []

        f, r = self.from_coord(sq)

        jumps = [
            (1, 2), (2, 1),
            (-1, 2), (-2, 1),
            (1, -2), (2, -1),
            (-1, -2), (-2, -1)
        ]

        for df, dr in jumps:
            nf = f + df
            nr = r + dr

            if self.in_bounds(nf, nr):
                to_sq = self.to_coord(nf, nr)

                piece = self.board.get(to_sq)

                if not piece or self.is_enemy(piece, color):
                    moves.append({
                        "piece": "N",
                        "from": sq,
                        "to": to_sq
                    })

        return moves

    def sliding_moves(self, sq, color, piece_type, dirs):
        moves = []

        f, r = self.from_coord(sq)

        for df, dr in dirs:
            nf = f + df
            nr = r + dr

            while self.in_bounds(nf, nr):
                to_sq = self.to_coord(nf, nr)

                piece = self.board.get(to_sq)

                if not piece:
                    moves.append({
                        "piece": piece_type,
                        "from": sq,
                        "to": to_sq
                    })

                else:
                    if self.is_enemy(piece, color):
                        moves.append({
                            "piece": piece_type,
                            "from": sq,
                            "to": to_sq
                        })

                    break

                nf += df
                nr += dr

        return moves

    def king_moves(self, sq, color):
        moves = []

        f, r = self.from_coord(sq)

        # =========================
        # NORMAL KING MOVES
        # =========================
        for df in (-1, 0, 1):
            for dr in (-1, 0, 1):
                if df == 0 and dr == 0:
                    continue

                nf = f + df
                nr = r + dr

                if self.in_bounds(nf, nr):
                    to_sq = self.to_coord(nf, nr)

                    piece = self.board.get(to_sq)

                    if not piece or self.is_enemy(piece, color):
                        moves.append({
                            "piece": "K",
                            "from": sq,
                            "to": to_sq
                        })

        # =========================
        # CASTLING (FULL LEGAL CHECK)
        # =========================

        # helper: check squares not attacked
        def safe(squares, enemy_color):
            for s in squares:
                if self.is_square_attacked(s, enemy_color):
                    return False
            return True

        enemy = opposite(color)

        # -------------------------
        # WHITE CASTLING
        # -------------------------
        if color == "w" and sq == "e1":

            # kingside (e1 -> g1)
            if (
                self.castling.get("wK") and
                self.board.get("h1") == "wR" and
                "f1" not in self.board and
                "g1" not in self.board and
                not self.in_check("w") and
                safe(["f1", "g1"], enemy)
            ):
                moves.append({
                    "piece": "K",
                    "from": "e1",
                    "to": "g1",
                    "castling": True
                })

            # queenside (e1 -> c1)
            if (
                self.castling.get("wR_queenside") and
                self.board.get("a1") == "wR" and
                "b1" not in self.board and
                "c1" not in self.board and
                "d1" not in self.board and
                not self.in_check("w") and
                safe(["d1", "c1"], enemy)
            ):
                moves.append({
                    "piece": "K",
                    "from": "e1",
                    "to": "c1",
                    "castling": True
                })

        # -------------------------
        # BLACK CASTLING
        # -------------------------
        if color == "b" and sq == "e8":

            # kingside (e8 -> g8)
            if (
                self.castling.get("bK") and
                self.board.get("h8") == "bR" and
                "f8" not in self.board and
                "g8" not in self.board and
                not self.in_check("b") and
                safe(["f8", "g8"], enemy)
            ):
                moves.append({
                    "piece": "K",
                    "from": "e8",
                    "to": "g8",
                    "castling": True
                })

            # queenside (e8 -> c8)
            if (
                self.castling.get("bR_queenside") and
                self.board.get("a8") == "bR" and
                "b8" not in self.board and
                "c8" not in self.board and
                "d8" not in self.board and
                not self.in_check("b") and
                safe(["d8", "c8"], enemy)
            ):
                moves.append({
                    "piece": "K",
                    "from": "e8",
                    "to": "c8",
                    "castling": True
                })

        return moves
    
def test(): ##testuje wykrywanie szachów i generowanie ruchów
    board = Board()

    moves = board.generate_moves("w")

    print("Liczba ruchów:", len(moves))

    for m in moves: ##sprawdzamy ilosc ruchów startowych
        print(m)

    board.board = { #sprawdzamy czy król może wyjść z pod szacha
        "e1": "wK",
        "e8": "bR",
        "a8": "bK"
    }

    board.turn = "w"

    moves = board.generate_moves("w") 

    print(moves)

    board.board = { #sprawdzamy czy figury nie mogą się poruszyć jeśli ich ruch spowoduje szacha
    "e1": "wK",
    "e2": "wR",
    "e8": "bR",
    "a8": "bK"
}
    board.turn = "w"

    moves = board.generate_moves("w")

    print(moves)

    board.board = { #wykrywanie szacha
    "e1": "wK",
    "e8": "bR",
    "a8": "bK"
}

    print(board.in_check("w")) #brak szacha

    board.board = {
    "e1": "wK",
    "a8": "bK"
}

    print(board.in_check("w"))

if __name__ == "__main__":
    test()