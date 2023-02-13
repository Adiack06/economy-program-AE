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
        data = json.loads(data.decode("utf-8"))
    except json.decoder.JSONDecodeError:
        print("JSON decode error")
        return None
    return data

def handle_client(conn):
    with conn:
        print(f"Connected by {addr}")
        whoami = recv_data(conn)
        if not whoami or not whoami.get("country"):
            print("Invalid start packet, disconnecting")
            return

        whoami = whoami.get("country")
        print(f"{addr} identified as {whoami}")

        queue = player_queues.get(whoami, [])
        conn.send(json.dumps({"queue_len": len(queue)}).encode("utf-8") + b"\n")
        for packet in queue:
            conn.send(json.dumps(packet).encode("utf-8") + b"\n")

        req = recv_data(conn)
        player = req["player"]
        if not player in player_queues:
            player_queues[player] = []
        player_queues[player].append(req)

        with open("queued_packets.json", "w") as f:
            f.write(json.dumps(player_queues))

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind(("0.0.0.0", 7894))
    s.listen()
    threads = []
    while True:
        conn, addr = s.accept()
        t = threading.Thread(target=handle_client, args=(conn,))
        t.start()
        threads.append(t)
            
