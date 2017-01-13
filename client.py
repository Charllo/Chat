import socket
import threading

host = ""
port = ""
nick = ""
buffer_size = 1024

while host == "":
    host = input("IP >> ")
    if host == "":
        print("Invalid")

while port == "":
    port = int(input("Port >> "))
    if str(port) == "":
        print("Invalid")

while nick == "":
    nick = input("Name >> ")
    if nick == "":
        print("Invalid")

def msg_handler():
    while True:
        try:
            data = s.recv(buffer_size)
            if data:
                print("\n\nRecieved: {}".format(data.decode("utf-8")))
                # Input still trailing from before, so just print the prompt again
                print("\nMessage to send >> ", end="")  # Remove end so input is in same place
        except ConnectionResetError:
            print("\nConnection to server lost")
            break

def main():
    message_handler = threading.Thread(target=msg_handler)
    message_handler.daemon = True  # Thread is killed when main ends
    message_handler.start()
    while True:
        try:
            to_send = input("\nMessage to send >> ").encode("utf-8")
            s.send(to_send)
        except KeyboardInterrupt:
            break

    print("\nClosing connection")
    s.close()
    quit()

if __name__ == '__main__':
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    s.send("NICK {}".format(nick).encode("utf-8"))
    main()
