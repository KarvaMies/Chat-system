import socket
import threading

HOST = "localhost"
PORT = 50007

# Creating a socket object and connecting to the server
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

invalid_nickname = True
while invalid_nickname:
    nickname = input("Enter your nickname: ")
    if nickname.startswith("/"):
        print("Invalid nickname. Try another one.")
    else:
        invalid_nickname = False

try:
    client.connect((HOST, PORT))
except ConnectionRefusedError:
    print("The server is not running. Please try again later.")
    exit()
except:
    print("An error has occurred. Shutting down...1")
    exit()

# Send nickname to the server
client.send(nickname.encode("utf-8"))


# Handles receiving messages from the server
def receive():
    while True:
        try:
            data = client.recv(1024).decode("utf-8")
            print(data)
        except:
            exit()  # Happens only if user intentionally exits the client


# Handles sending messages to the server
def send():
    try:
        client.send(nickname.encode("utf-8"))
        while True:
            message = input()

            # Send the message to the server
            if (
                message == "/disconnect"
                or message == "/dc"
                or message == "/quit"
                or message == "/exit"
            ):
                client.send("!disconnect".encode("utf-8"))
                client.shutdown(socket.SHUT_RDWR)
                client.close()
                print("Disconnecting from the server...")
                break
            elif message.startswith("/pm") or message.startswith("/dm"):
                client.send(f"{message}".encode("utf-8"))
            elif message == "/h" or message == "/help":
                client.send("!help".encode("utf-8"))
            else:
                client.send(f"{message}".encode("utf-8"))
    except (KeyboardInterrupt, EOFError):
        client.send("!disconnect".encode("utf-8"))
        client.close()
        print("Disconnected from server.")
    except OSError:
        print("The server has shut down. Exiting the client.")
        exit()
    except:
        print("An error has occurred. Shutting down...")
        exit()


# Start the receive and send threads
receive_thread = threading.Thread(target=receive)
receive_thread.start()

send_thread = threading.Thread(target=send)
send_thread.start()
