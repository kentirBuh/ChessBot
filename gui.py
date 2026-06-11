import tkinter as tk
from board import Board


LIGHT = "#f0d9b5"
DARK = "#b58863"

PIECE_UNICODE = {
    "wK": "♔", "wQ": "♕", "wR": "♖", "wB": "♗", "wN": "♘", "wP": "♙",
    "bK": "♚", "bQ": "♛", "bR": "♜", "bB": "♝", "bN": "♞", "bP": "♟"
}


class ChessGUI:
    def __init__(self):
        self.board = Board()

        self.root = tk.Tk()
        self.root.title("Chess Bot Tester")

        self.buttons = {}

        self.selected = None
        self.legal_moves = []

        self.draw_board()
        self.render()

        self.root.mainloop()

    # =========================
    # BOARD UI
    # =========================
    def draw_board(self):
        for r in range(8):
            for f in range(8):
                color = LIGHT if (r + f) % 2 == 0 else DARK

                btn = tk.Button(
                    self.root,
                    width=6,
                    height=3,
                    bg=color,
                    command=lambda x=f, y=r: self.on_click(x, y)
                )

                btn.grid(row=7 - r, column=f)
                self.buttons[(f, r)] = btn

    # =========================
    # CLICK HANDLER
    # =========================
    def on_click(self, f, r):
        sq = self.to_sq(f, r)

        piece = self.board.board.get(sq)

        # =========================
        # 1. jeśli klikamy ruch
        # =========================
        for m in self.legal_moves:
            if m["to"] == sq:

                self.board.move_piece(m)

                # reset wyboru
                self.selected = None
                self.legal_moves = []

                self.render()
                return

        # =========================
        # 2. wybór figury
        # =========================
        if piece and piece[0] == self.board.turn:
            self.selected = sq

            self.legal_moves = [
                m for m in self.board.generate_moves(self.board.turn)
                if m["from"] == sq
            ]
        else:
            # kliknięcie pustego pola / złej figury
            self.selected = None
            self.legal_moves = []

        self.render()

    # =========================
    # RENDER
    # =========================
    def render(self):
        for (f, r), btn in self.buttons.items():
            sq = self.to_sq(f, r)
            piece = self.board.board.get(sq)

            text = PIECE_UNICODE.get(piece, "") if piece else ""
            btn.config(text=text)

            # highlight moves
            if any(m["to"] == sq for m in self.legal_moves):
                btn.config(bg="yellow")
            else:
                btn.config(
                    bg=LIGHT if (f + r) % 2 == 0 else DARK
                )

    # =========================
    # HELPERS
    # =========================
    def to_sq(self, f, r):
        return chr(ord("a") + f) + str(r + 1)


if __name__ == "__main__":
    ChessGUI()