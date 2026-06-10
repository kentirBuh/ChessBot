# Modul polaczenia JSON Lines

Ten katalog mozna wyslac innym druzynom jako minimalny kod transportu TCP.
Plik `connection.py` nie zalezy od naszego silnika szachowego.

## Protokol

- Transport: TCP
- Kodowanie: UTF-8
- Format: JSON Lines
- Jedna wiadomosc to jeden obiekt JSON zakonczony `\n`
- Serwer gra bialymi, klient gra czarnymi

Przykladowa ramka ruchu:

```json
{"piece":"P","from":"e2","to":"e4"}
```

Promocja:

```json
{"piece":"P","from":"e7","to":"e8","promotion":"Q"}
```

## Uzycie po stronie serwera

```python
from connection import wait_for_client

peer, address = wait_for_client("0.0.0.0", 5050)

try:
    peer.send({"piece": "P", "from": "e2", "to": "e4"})
    frame = peer.recv()
finally:
    peer.close()
```

## Uzycie po stronie klienta

```python
from connection import connect_to_server

peer = connect_to_server("127.0.0.1", 5050)

try:
    frame = peer.recv()
    peer.send({"piece": "P", "from": "e7", "to": "e5"})
finally:
    peer.close()
```

## API

- `wait_for_client(host, port)` - uruchamia serwer TCP, czeka na jedno polaczenie i zwraca `(peer, address)`.
- `connect_to_server(host, port)` - laczy sie z serwerem TCP i zwraca `peer`.
- `peer.send(dict)` - wysyla slownik jako pojedyncza linie JSON.
- `peer.recv()` - odbiera pojedyncza linie JSON i zwraca slownik.
- `peer.close()` - zamyka plik buforujacy oraz socket.

Odbiorca powinien utrzymywac lokalny stan planszy i po odebraniu ramki przesunac figure z pola `from` na `to`. Roszada, bicie w przelocie i promocja wynikaja z lokalnego stanu planszy oraz opcjonalnego pola `promotion`.
