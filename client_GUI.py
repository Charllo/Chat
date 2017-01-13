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

def addtotext(widget, text):
    #  Adds a line to a text widget, makes it un-editable and then scrolls to the bottom
    widget.configure(state="normal")
    widget.insert("end", "\n{}".format(text))
    widget.configure(state="disabled")
    widget.see(END)

def send():
    message = msg_entry.get().encode("utf-8")
    if message != "":
        addtotext(message_area, "You: {}".format(message.decode("utf-8")))
        s.send(message)
    msg_entry.delete(0, "end")

def msg_handler():
    while True:
        try:
            data = s.recv(buffer_size)
            if data:
                addtotext(message_area, "{}".format(data.decode("utf-8")))
        except ConnectionResetError:
            addtotext(message_area, "Connection to server lost")
            break

def main():
    message_handler = threading.Thread(target=msg_handler)
    message_handler.daemon = True  # Thread is killed when main ends
    message_handler.start()
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

btn_send = Button(root, text="Send", command=send, width=20)
btn_send.grid(row=3)


if __name__ == '__main__':
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    s.send("NICK {}".format(nick).encode("utf-8"))
    main()
