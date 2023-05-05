import socket
import threading

HOST = "localhost"
PORT = 50007

# Creating a socket object and starting a server on it
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()
print(f"[SERVER] Server started")


# Handles each client connection
def handle_client(conn, addr, nickname):
    global clients
    nickname_not_set = True
    addr0 = addr[0]
    addr1 = addr[1]
    print(f"[NEW CONNECTION] {nickname} connected from {addr}")

    conn.send(f"[SERVER] Welcome, {nickname}!\n".encode("utf-8"))
    conn.send(
        f"[SERVER] For list of available commands use /h or /help\n".encode("utf-8")
    )

    while True:
        try:
            # Data from client
            data = conn.recv(1024).decode("utf-8")
        except ConnectionResetError:
            # Client disconnected unexpectedly
            for client in clients:
                if client[1] == nickname:
                    clients.remove(client)
                    break
            print(
                f"[DISCONNECTED] User '{nickname}' from {addr0}:{addr1} has disconnected"
            )
            broadcast(f"[SERVER] User '{nickname}' has disconnected")
            print_active_users()
            break

        # If no data is received, client disconnected
        if not data:
            if (conn, nickname) in clients:
                clients.remove((conn, nickname))
                print(
                    f"[DISCONNECTED] User '{nickname}' from {addr0}:{addr1} has disconnected"
                )
                broadcast(f"[SERVER] User '{nickname}' has disconnected")
                print_active_users()
            break

        # Filter entering nickname when connecting
        if nickname == data and nickname_not_set:
            nickname_not_set = False

        # Check for disconnect command from client
        elif data.startswith("!disconnect"):
            clients.remove((conn, nickname))
            print(
                f"[DISCONNECTED] User '{nickname}' from {addr0}:{addr1} has disconnected"
            )
            broadcast(
                f"[SERVER] User '{nickname}' has disconnected",
                None,
            )
            print_active_users()

        # Check for private message
        elif data.startswith("/pm") or data.startswith("/dm"):
            print(f"[DEBUG] someone tries to disconnect")
            parts = data.split()
            target = parts[1]
            message = " ".join(parts[2:])

            target_conn = None
            for client in clients:
                if client[1] == target:
                    target_conn = client[0]
                    break

            # Check if target is connected
            if target_conn is None:
                conn.send(
                    f"[SERVER] {target} is not connected to the server.\n".encode(
                        "utf-8"
                    )
                )
            else:
                target_conn.send(
                    f"[PRIVATE MESSAGE] From {nickname}: {message}\n".encode("utf-8")
                )
                print(f"[PRIVATE MESSAGE] From {nickname} to {target}: {message}")

        elif data.startswith("!help"):
            target_conn = None
            for client in clients:
                if client[1] == nickname:
                    target_conn = client[0]
                    break

            target_conn.send(f"List of available commands:\n".encode("utf-8"))
            target_conn.send(
                f"/disconnect - Disconnects you from the server\n".encode("utf-8")
            )
            target_conn.send(f"/dc - Disconnects you from the server\n".encode("utf-8"))
            target_conn.send(
                f"/quit - Disconnects you from the server\n".encode("utf-8")
            )
            target_conn.send(
                f"/exit - Disconnects you from the server\n".encode("utf-8")
            )
            target_conn.send(
                f"/pm <nickname> <message> - Sends message privately to another user\n".encode(
                    "utf-8"
                )
            )
            target_conn.send(
                f"/dm <nickname> <message> - Sends message privately to another user\n".encode(
                    "utf-8"
                )
            )
            target_conn.send(f"/help - Shows this list\n".encode("utf-8"))
            target_conn.send(f"/h - Shows this list\n".encode("utf-8"))

        else:
            if not data.isspace():
                broadcast(f"{nickname}: {data}", conn)
                print(f"[NEW MESSAGE] {nickname}: {data}")

    conn.close()


# Broadcast new messages to all connected clients
def broadcast(msg, sender_conn=None):
    for client in clients:
        if client[0] != sender_conn:
            client[0].send(msg.encode("utf-8"))


def print_active_users():
    message = ""

    print(f"[ACTIVE USERS] {len(clients)}: ", end="")
    for i, client in enumerate(clients):
        if len(clients) == 1:
            print(client[1])
            message += client[1]
        elif i == len(clients) - 1:
            print(f"& {client[1]}")
            message += "& " + client[1]
        elif i == len(clients) - 2:
            print(f"{client[1]} ", end="")
            message += client[1] + " "
        else:
            print(f"{client[1]}, ", end="")
            message += client[1] + ", "

    broadcast(f"[SERVER] {len(clients)} active user(s): " + message)


# List of all connected clients
clients = []

# Let the clients to connect to the server and create a new thread for each client
while True:
    conn, addr = server.accept()

    # Ask for nickname
    nickname = conn.recv(1024).decode("utf-8")

    clients.append((conn, nickname))

    thread = threading.Thread(target=handle_client, args=(conn, addr, nickname))
    thread.start()

    # Notify current clients about the new client
    for client in clients:
        if client[0] != conn:
            client[0].send(
                f"[SERVER] New user '{nickname}' joined the server".encode("utf-8")
            )
    print_active_users()
