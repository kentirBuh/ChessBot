# bot.py
from connection import connect_to_server
from board import Board
from engine import Engine

HOST = "127.0.0.1"
PORT = 5050

def main():
    peer = connect_to_server(HOST, PORT)

    board = Board()
    engine = Engine()

    try:
        while True:
            msg = peer.recv()
            print("Biały:", msg)

            board.move_piece(msg)

            move = engine.choose_move(board)
            print("Czarny:", move)

            if move:
                board.move_piece(move)
                peer.send(move)

    finally:
        peer.close()


if __name__ == "__main__":
    main()