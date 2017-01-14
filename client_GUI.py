from tkinter import *
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

root = Tk()
root.title("Client")
root.geometry("600x650")

def addtotext(widget, text, self_message=False, important=False):
    tag = ""

    message_area.tag_configure("connection", foreground="red")
    message_area.tag_configure("self_message", foreground="blue")

    if self_message == True:
        tag = "self_message"
    elif important == True:
        tag = "connection"
    else:
        tag = ""

    #  Adds a line to a text widget, makes it un-editable and then scrolls to the bottom
    widget.configure(state="normal")
    widget.insert("end", "\n{}".format(text), tag)
    widget.configure(state="disabled")
    widget.see(END)

def send():
    message = msg_entry.get().encode("utf-8")
    if message != "":
        addtotext(message_area, "You: {}".format(message.decode("utf-8")), True)
        s.send(message)
    msg_entry.delete(0, "end")

def msg_handler():
    while True:
        try:
            data = s.recv(buffer_size)
            if data:
                if data.decode("utf-8") == "YOU HAVE BEEN KICKED BY THE SERVER":
                    addtotext(message_area, "You have been kicked by the server", False, True)
                    raise ConnectionResetError
                else:
                    addtotext(message_area, "{}".format(data.decode("utf-8")))

        except ConnectionResetError:
            s.close()
            addtotext(message_area, "Connection to server lost", False, True)
            break

def main():
    message_handler = threading.Thread(target=msg_handler)
    message_handler.daemon = True  # Thread is killed when main ends
    message_handler.start()
    root.mainloop()

#  create a Frame for the Text and Scrollbar
txt_frm = Frame(root, width=600, height=600)
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
scrollb.grid(row=0, column=1, sticky='nsew')
message_area['yscrollcommand'] = scrollb.set

msg_entry = Entry(root, width=20)
msg_entry.grid(row=2, sticky="E")

root.bind("<Return>", lambda event: send())  # Bind return to send msg
btn_send = Button(root, text="Send", command=send, width=20)
btn_send.grid(row=2, column=1, sticky="W")

if __name__ == '__main__':
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    addtotext(message_area, "Connected to server", False, True)
    s.send("NICK {}".format(nick).encode("utf-8"))
    addtotext(message_area, "Name sent", False, True)
    main()
    # Once all loops are broken
    root.destroy()
    quit()
