from datetime import datetime
from tkinter import *
import socket
import threading
import ipaddress

host = ""
port = ""
nick = ""
buffer_size = 1024
tag = ""

# TinyIP Stuff  ################################################################
# Wew
asciiDict = {'0':'0','1':'1','2':'2','3':'3','4':'4','5':'5','6':'6','7':'7',
'8':'8','9':'9','!':'10','@':'11','£':'12','$':'13','%':'14','^':'15','&':'16',
'*':'17','(':'18',')':'19','€':'20','#':'21','-':'22','=':'23','_':'24',
'+':'25','q':'26','w':'27','e':'28','r':'29','t':'30','y':'31','u':'32',
'i':'33','o':'34','p':'35','[':'36',']':'37','Q':'38','W':'39','E':'40',
'R':'41','T':'42','Y':'43','U':'44','I':'45','O':'46','P':'47','{':'48',
'}':'49','a':'50','s':'51','d':'52','f':'53','g':'54','h':'55','j':'56',
'k':'57','l':'58',';':'59','A':'60','S':'61','D':'62','F':'63','G':'64',
'H':'65','J':'66','K':'67','L':'68',':':'69','|':'70','`':'71','z':'72',
'x':'73','c':'74','v':'75','b':'76','n':'77','m':'78',',':'79','.':'80',
'å':'81','~':'82','Z':'83','X':'84','C':'85','V':'86','B':'87','N':'88',
'M':'89','<':'90','>':'91','?':'92','±':'93','§':'94','€':'95','¢':'96',
'ß':'97','Ω':'98','ç':'99'}

def Int2IP(ipnum):  # I have no idea how this works but it does
    o1 = int(int(ipnum) / 16777216) % 256
    o2 = int(int(ipnum) / 65536) % 256
    o3 = int(int(ipnum) / 256) % 256
    o4 = int(int(ipnum)) % 256
    return "{}.{}.{}.{}".format(o1, o2, o3, o4)

def TinyIP(ADDRESS):
    IPDict = list(ADDRESS)
    output = []

    for IP in IPDict:
        output.append(asciiDict[IP])

    output = "".join(output)
    
    return str(Int2IP(output))
###############################################################################

# - - - Input + Input checking - - - #
while host == "":
    host = input("IP   >> ")
    try:
        socket.inet_aton(host)  # Throws a socket error if IP is illegal
    except socket.error:
        host = TinyIP(host)

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

while nick == "":
    nick = input("Name >> ")
    if nick == "":
        print("Invalid")
# - - - - - - - - - - - - - - - - - - #

root = Tk()
root.title("Client | Connected to {}:{}".format(host, port))
root.geometry("775x630")

def disable_sending():
    btn_send.config(state="disabled")
    root.bind("<Return>", lambda event: disable_sending())  # Rebind to do nothing

def addtotext(widget, text, self_message=False, important=False):
    timestamp = datetime.now().strftime("%H:%M")
    text = "{} | {}".format(timestamp, text)  # Add timestamp

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

def send_message_from_box():
    message = msg_entry.get()
    msg_entry.delete(0, "end")
    if message.rstrip() != "":
        try:
            addtotext(message_area, "You: {}".format(message), True)
            s.send(str.encode(message))
        except (ConnectionResetError, OSError):  # Needed after being kicked
            s.close()

def msg_handler():
    while True:
        try:
            data = s.recv(buffer_size)
            if data:
                decoded = data.decode("utf-8")
                split = decoded.split(" ")
                if decoded == "[Server Message] YOU HAVE BEEN KICKED BY THE SERVER":
                    addtotext(message_area, "[Server Message] You have been kicked by the server", important=True)
                    raise ConnectionResetError
                # If it's an official server message
                elif str(split[0])+str(split[1]) == "[ServerMessage]":
                    addtotext(message_area, str(decoded), important=True)
                else:
                    addtotext(message_area, str(decoded))

        except (ConnectionResetError, OSError):
            s.close()
            disable_sending()
            addtotext(message_area, "[Client] Connection to server lost", important=True)
            break

def main():
    root.bind("<Return>", lambda event: send_message_from_box()) # Bind return to send msg
    btn_send.config(state="normal")  # Connected, so user can send messages now
    message_handler = threading.Thread(target=msg_handler)
    message_handler.daemon = True  # Thread is killed when main ends
    message_handler.start()
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
scrollb.grid(row=0, column=3, sticky='nsew')
message_area['yscrollcommand'] = scrollb.set

msg_entry = Entry(root, width=20)
msg_entry.grid(row=2, sticky="E")

# Only enable after connection made and nickname sent
btn_send = Button(root, text="Send", command=send_message_from_box, width=20, state="disabled")
btn_send.grid(row=2, column=1, sticky="W")

# Add colours to message_area
message_area.tag_configure("connection", foreground="red")
message_area.tag_configure("self_message", foreground="blue")

if __name__ == '__main__':
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((host, port))
    except OSError:
        addtotext(message_area, "[Client] Socket attempted to connect to an unreachable network", important=True)
        root.mainloop()
    except ConnectionRefusedError:
        addtotext(message_area, "[Client] No connection could be made", important=True)
        root.mainloop()
    else:
        addtotext(message_area, "[Client] Connected to server", important=True)
        s.send("NICK {}".format(nick).encode("utf-8"))
        addtotext(message_area, "[Client] Name sent", important=True)
        main()
        # Once all loops are broken
        try:
            root.destroy()
        except TclError:
            pass  # Root already destroyed
        quit()
