import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from connection import wait_for_client
from board import Board
from engine import Engine

def main():
    print("Czekam na bota...")

    peer, addr = wait_for_client("127.0.0.1", 5050)
    print("Bot podłączony:", addr)

    board = Board()
    engine = Engine()

    try:
        while True:
            move = engine.choose_move(board)
            print("Bialy:", move)

            if not move:
                print("Koniec gry - brak legalnych ruchow.")
                break

            board.move_piece(move)
            peer.send(move)

            try:
                reply = peer.recv()
            except ConnectionError:
                print("Bot rozlaczony.")
                break

            print("Czarny:", reply)
            board.move_piece(reply)

    finally:
        peer.close()

if __name__ == "__main__":
    main()