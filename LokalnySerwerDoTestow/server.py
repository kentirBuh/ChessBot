from connection import wait_for_client

def main():
    print("Czekam na bota...")

    peer, addr = wait_for_client("127.0.0.1", 5050)
    print("Bot podłączony:", addr)

    # startowa pozycja - tylko test (pion e2-e4)
    moves = [
        {"piece":"P","from":"e2","to":"e4"},
        {"piece":"P","from":"e7","to":"e5"},
        {"piece":"N","from":"g1","to":"f3"},
    ]

    try:
        for m in moves:
            print("SERWER -> BOT:", m)
            peer.send(m)

            reply = peer.recv()
            print("BOT -> SERWER:", reply)

    finally:
        peer.close()

if __name__ == "__main__":
    main()