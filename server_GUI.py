from tkinter import *
import socket
import threading

# Kicking a client is a bit buggy

host = ""
port = ""
buffer_size = 1024
client_dict = {}

while host == "":
    host = input("IP >> ")
    if host == "":
        print("Invalid")

while port == "":
    port = int(input("Port >> "))
    if str(port) == "":
        print("Invalid")

root = Tk()
root.title("Server")
root.geometry("600x650")

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

s.bind((host, port))
s.listen(5)

def addtotext(widget, text, self_message=False, connection_flag=False):
    tag = ""

    message_area.tag_configure("connection", foreground="red")
    message_area.tag_configure("self_message", foreground="blue")

    if connection_flag == True:
        tag = "connection"
    elif self_message == True:
        tag = "self_message"
    else:
        tag = ""

    #  Adds a line to a text widget, makes it un-editable and then scrolls to the bottom
    widget.configure(state="normal")
    widget.insert("end", "\n{}".format(text), tag)
    widget.configure(state="disabled")
    widget.see(END)

def send_message(input_message="", kicked_client=""):
    if input_message != "" and kicked_client != "":
        kicked_client.send(str.encode(input_message))  # Send the message

    else:
        message = msg_entry.get().encode("utf-8")
        addtotext(message_area, "You: {}".format(message.decode("utf-8")), True)
        out_msg = "SERVER: {}".format(message.decode("utf-8"))
        for c in client_dict.keys():  # For each client
            c.send(str.encode(out_msg))  # Send the message
        msg_entry.delete(0, "end")

def send_all(in_client, out_message):
    for c in client_dict.keys():  # For each client
        if c != in_client:  # If it is not the one that sent the msg
            c.send(str.encode(out_message))  # Sent the message

def kick():
    name_map = {v: k for k, v in client_dict.items()}
    user = kick_entry.get()
    kick_entry.delete(0, "end")
    client_to_kick = name_map[user]
    send_message("YOU HAVE BEEN KICKED BY THE SERVER", client_to_kick)
    addtotext(message_area, "{} kicked from server".format(user), False, True)
    send_all("", "{} kicked from server".format(user))

def handler(client, addr):
    nickname_done = False  # Nickname set = False
    ip_port = "{}:{}".format(addr[0], addr[1])  # Looks like "127.0.0.1:1234"
    while True:
        try:
            r_msg = client.recv(buffer_size)  # Recieve message

            if r_msg:  # If there is text
                if nickname_done == False:  # If nickname not set
                    nick_msg = r_msg.decode("utf-8")  # Decode it
                    nick_splt = nick_msg.split(" ")  # Split it
                    client_dict[client] = " ".join(nick_splt[1:])  # Add to dict
                    addtotext(message_area, "{} set nick to {}".format(ip_port, client_dict[client]), False, True)
                    nickname_done = True  # Nick has been set
                    out_msg = "{} joined".format(client_dict[client])  # Tell all clients

                else:  # If nick already set
                    # r_msg decoded so a) it will print and b) it wont get double encoded
                    addtotext(message_area, "{}: {}".format(client_dict[client], r_msg.decode("utf-8")))
                    out_msg = "{}: {}".format(client_dict[client], r_msg.decode("utf-8"))

                send_all(client, out_msg)

        except (ConnectionResetError, ConnectionAbortedError):
            out_msg = "Client {} ({}) dropped".format(client_dict[client], ip_port)
            addtotext(message_area, out_msg, False, True)
            client_dict.pop(client)  # Remove client from dict
            send_all(client, out_msg)
            break  # End process

def client_checking():
    while True:
        client,addr = s.accept()
        addtotext(message_area, "Accepted connection from: {}:{}".format(addr[0], addr[1]), False, True)
        client_handler = threading.Thread(target=handler,args=(client,addr))
        client_handler.daemon = True
        client_handler.start()

def main():
    client_checking_thrd = threading.Thread(target=client_checking)
    client_checking_thrd.daemon = True
    client_checking_thrd.start()
    addtotext(message_area, "Server started", False, True)
    root.mainloop()


#  create a Frame for the Text and Scrollbar
txt_frm = Frame(root, width=600, height=600)
txt_frm.grid(row=0)
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
scrollb.grid(row=0, column=1, sticky='nsew')
message_area['yscrollcommand'] = scrollb.set

msg_entry = Entry(root, width=20)
msg_entry.grid(row=2)

btn_send = Button(root, text="Send", command=send_message, width=20)
btn_send.grid(row=3)

kick_entry = Entry(root, width=20)
kick_entry.grid(row=4)

btn_kick = Button(root, text="Kick", command=kick, width=20)
btn_kick.grid(row=5)

if __name__ == '__main__':
    main()
    quit()
