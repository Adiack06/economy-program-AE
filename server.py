import socket
import json
import os
import threading
if os.path.isfile("queued_packets.json"):
    with open("queued_packets.json", "r") as f:
        player_queues = json.loads(f.read())
else:
    player_queues = {}

def recv_data(s):
    data = b""
    while not b"\n" in data:
        d = s.recv(1024)
        if not d:
            break
        data += d
    try:
        print(data)
        data = json.loads(data.decode("utf-8"))
    except json.decoder.JSONDecodeError:
        print("JSON decode error")
        return None
    return data

def handle_client(conn):
    with conn:
        print(f"Connected by {addr}")
        whoami = recv_data(conn)
        if not whoami or not whoami.get("whoami"):
            print("Invalid start packet, disconnecting")
            return

        whoami = whoami.get("whoami")
        print(f"{addr} identified as {whoami}")

        queue = player_queues.get(whoami, [])
        conn.send(json.dumps(queue).encode("utf-8") + b"\n")
        player_queues[whoami] = [] # assume everything went smoothly...

        while True:
            req = recv_data(conn)
            if not req or (type(req) == str and req == "exit"):
                break
            player = req["player"]
            if not player in player_queues:
                player_queues[player] = []
            player_queues[player].append(req)

            with open("queued_packets.json", "w") as f:
                f.write(json.dumps(player_queues))

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind(("0.0.0.0", 7896))
    s.listen()
    threads = []
    while True:
        conn, addr = s.accept()
        t = threading.Thread(target=handle_client, args=(conn,))
        t.start()
        threads.append(t)
            
