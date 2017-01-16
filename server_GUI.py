from datetime import datetime
from tkinter import *
import socket
import threading

host = ""
port = ""
buffer_size = 1024
client_dict = {}
tag = ""

while port == "":
    try:
        port = int(input("Port >> "))
    except ValueError:
        print("Invalid")
    else:
        if port > 65535 or port < 0:
            print("Port must be 0-65535")
            port = ""  # Reset
        elif str(port) == "":
            print("Invalid")

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

host = socket.gethostbyname(socket.gethostname())
if host == "127.0.0.1":  # Try a different way
    host = socket.gethostbyname(socket.getfqdn())

s.bind((host, port))

try:
    s.listen()
except TypeError:
    s.listen(5)  # Win7 needs a max number of failed connections

root = Tk()
root.title("Server | {}:{}".format(host, port))
root.geometry("775x655")

def addtotext(widget, text, self_message=False, connection_flag=False, config_message=False):
    timestamp = datetime.now().strftime("%H:%M")
    text = "{} | {}".format(timestamp, text)  # Add timestamp

    f.write("{}\n".format(str(text)))  # Chat log

    if connection_flag == True:
        tag = "connection"
    elif self_message == True:
        tag = "self_message"
    elif config_message == True:
        tag = "server_config"
    else:
        tag = ""

    #  Adds a line to a text widget, makes it un-editable and then scrolls to the bottom
    widget.configure(state="normal")
    widget.insert("end", "\n{}".format(text), tag)
    widget.configure(state="disabled")
    widget.see(END)

def send_message_from_box():
    message = msg_entry.get()
    msg_entry.delete(0, "end")
    if message.rstrip() != "":
        addtotext(message_area, "You: {}".format(message), True)
        send_all("", "Server-User: {}".format(message))

def send_all(in_client, out_message):
    for c in client_dict.keys():  # For each client
        if c != in_client:  # If it is not the one that sent the msg
            try:
                c.send(str.encode(out_message))  # Send the message
            except BrokenPipeError:  # For Linux
                c.close()  # Will trigger connection exception

def kick():
    name_map = {v: k for k, v in client_dict.items()}  # Swap names and client obj
    user = kick_entry.get()
    kick_entry.delete(0, "end")
    try:
        client_to_kick = name_map[user]  # Get client object
        client_to_kick.send(str.encode("[Server Message] YOU HAVE BEEN KICKED BY THE SERVER"))  # Send the message
        kick_msg = "[Server Message] {} kicked from server".format(user)
        addtotext(message_area, kick_msg, connection_flag=True)
        send_all("", kick_msg)
    except KeyError:
        addtotext(message_area, "[Kick message] {} not recognized".format(user), connection_flag=True)

def handler(client, addr):
    nickname_done = False  # Nickname set = False
    ip_port = "{}:{}".format(addr[0], addr[1])  # Looks like "127.0.0.1:1234"
    while True:
        try:
            r_msg = client.recv(buffer_size)  # Recieve message

            if r_msg:  # If there is text
                decoded = r_msg.decode("utf-8")
                if nickname_done == False:  # If nickname not set
                    nick_splt = decoded.split(" ")  # Split it
                    client_dict[client] = " ".join(nick_splt[1:])  # Add to dict
                    addtotext(message_area, "[Server Message] {} set nickname to {}".format(ip_port, client_dict[client]), connection_flag=True)
                    nickname_done = True  # Nick has been set
                    out_msg = "[Server Message] {} joined".format(client_dict[client])  # Tell all clients
                    client.send(str.encode("[Server Message] Connection successful\n"))  # Tell the client (\n for newline, looks cleaner for client)
                    addtotext(message_area, "[Server Message] Client {} ({}) connection successful".format(client_dict[client], ip_port), connection_flag=True)


                else:  # If nick already set
                    # r_msg decoded so a) it will print and b) it wont get double encoded
                    addtotext(message_area, "{}: {}".format(client_dict[client], decoded))
                    out_msg = "{}: {}".format(client_dict[client], decoded)

                send_all(client, out_msg)

        except (ConnectionResetError, ConnectionAbortedError):
            try:
                drop_msg = "[Server Message] Client {} ({}) dropped".format(client_dict[client], ip_port)
                client_dict.pop(client)  # Remove client from dict
                send_all(client, drop_msg)
            except KeyError:  # Client kicked/broke before fully connected
                drop_msg = "[Server Message] Unknown client ({}) dropped before full connection".format(ip_port)
                # No need to send everyone else this message

            addtotext(message_area, drop_msg, connection_flag=True)
            client.close()
            break  # End process

def client_checking():
    while True:
        client,addr = s.accept()
        addtotext(message_area, "[Server Message] Accepted connection from: {}:{}".format(addr[0], addr[1]), connection_flag=True)
        client_handler = threading.Thread(target=handler,args=(client,addr))
        client_handler.daemon = True
        client_handler.start()

def main():
    client_checking_thrd = threading.Thread(target=client_checking)
    client_checking_thrd.daemon = True
    client_checking_thrd.start()
    addtotext(message_area, "[!] Server started on {}:{}".format(host, port), config_message=True)
    root.mainloop()

#  create a Frame for the Text and Scrollbar
txt_frm = Frame(root, width=775, height=600)
txt_frm.grid(row=0, columnspan=2)
#  ensure a consistent GUI size
txt_frm.grid_propagate(False)
#  implement stretchability
txt_frm.grid_rowconfigure(0, weight=1)
txt_frm.grid_columnconfigure(0, weight=1)
#  create a Text widget
message_area = Text(txt_frm, borderwidth=3, relief="sunken", state="disabled")
message_area.config(font=("consolas", 12), undo=True, wrap='word')
message_area.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)
#  create a Scrollbar and associate it with txt
scrollb = Scrollbar(txt_frm, command=message_area.yview)
scrollb.grid(row=0, column=1, sticky="nsew")
message_area["yscrollcommand"] = scrollb.set

msg_entry = Entry(root, width=20)
msg_entry.grid(row=2, sticky="E")

root.bind("<Return>", lambda event: send_message_from_box())  # Bind return to send msg
btn_send = Button(root, text="Send", command=send_message_from_box, width=20)
btn_send.grid(row=2, column=1, sticky="W")

kick_entry = Entry(root, width=20)
kick_entry.grid(row=3, sticky="E")

btn_kick = Button(root, text="Kick", command=kick, width=20)
btn_kick.grid(row=3, column=1, sticky="W")

 # Add colours to message_area
message_area.tag_configure("self_message", foreground="blue")
message_area.tag_configure("connection", foreground="red")
message_area.tag_configure("server_config", foreground="purple")

if __name__ == '__main__':
    with open ("chatlog.txt", "w") as f:
        main()
    # Once all loops are broken
    try:
        root.destroy()
    except TclError:
        pass  # Root already destroyed
    quit()
