import socket
import threading
import os
import sys
import tkinter as tk
from tkinter import simpledialog
import emoji

#number of users in chatroom
numUsers = 0

##############
# Server
##############
class Server(threading.Thread):
    def __init__(self, host, port):
        #close or open connection
        self.connections = []
        self.host = "127.0.0.1"
        self.port = 1060
        super().__init__()

    def run(self):
        #attempt to connect socket and port
        serverSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serverSock.bind(("127.0.0.1", 1060))
        serverSock.listen(1)
        #announce in terminal what we are listening on
        print('Connected on:', serverSock.getsockname())
        #attempt to connect user(s) to server
        while True:
            sc, sockname = serverSock.accept()
            print('user connects from {} to {}'.format(sc.getpeername(), sc.getsockname()))
            #new thread
            server_socket = ServerSocket(sc, sockname, self)
            server_socket.start()
            # Add thread to  connections
            self.connections.append(server_socket)
            print('Server gets messages from user from:', sc.getpeername())

    def messageSend(self, message, source):
        #sends all other users usernames message
        for connection in self.connections:
            if connection.sockname != source:
                connection.send(message)

    def remove_connection(self, connection):
        #remove connnnection from server socket
        self.connections.remove(connection)


class ServerSocket(threading.Thread):
    #support socket connection
    def __init__(self, sc, sockname, server):
        self.sc = sc
        self.sockname = sockname
        self.server = server
        super().__init__()

    def run(self):
        #return user message
        while True:
            message = self.sc.recv(1024).decode('ascii')
            if message == "no":
                return
            elif message:
                #send users message
                self.server.messageSend(message, self.sockname)
            else:
                self.sc.close()
                server.remove_connection(self)
                return
    def send(self, message):
        #Send user message to server.
        self.sc.sendall(message.encode('ascii'))

##############
# Client
##############
class Send(threading.Thread):
    def __init__(self, socket, name):
        self.socket = socket
        self.username = name
        super().__init__()

class Receive(threading.Thread):
    #get threads from server
    def __init__(self, socket, name):
        self.socket = socket
        self.username = name
        self.messages = None
        super().__init__()

    def run(self):
        #gets messages from server and displays on GUI
        while True:
            message = self.socket.recv(1024).decode('ascii')
            #check message is valid
            if message and self.messages and len(message) > 0:
                    self.messages.insert(tk.END, message)

#GUI support for client and server
class ChatroomGUI:
    #get ports/hosts
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.username = None
        self.messages = None

    #Starting up the client server connection
    def start(self):
        #Connect host and port
        print("Connecting to " + str(self.host) + ":" + str(self.port))
        self.socket.connect((self.host, self.port))
        print(emoji.emojize("Success! :thumbs_up:"))

        #Get name from user
        self.username = simpledialog.askstring( "Input", "What is your name?", parent=tk.Tk())

        #threads
        send = Send(self.socket, self.username)
        receive = Receive(self.socket, self.username)
        #start thread connections
        send.start()
        receive.start()

        #announce that another user joined chatroom
        self.socket.sendall("{} has joined. Say hi!".format( self.username).encode("ascii"))
        print("\rNote: you can leave the chatroom by typing 'q'!\n")
        return receive


    def send(self, msgTextBox):
        #message from user written in textbox in GUI
        message = msgTextBox.get()
        #remove message from textbox after user hits send
        msgTextBox.delete(0, tk.END)
        #place message (if valid, meaning there is a message) in gui box
        if len(message) > 0:
            self.messages.insert(tk.END, "{}: {}".format( self.username, emoji.emojize(message)))

        # quit classroom: user must type "q" 
        if message == "q":
            #send to socket that user is leaving chat
            self.socket.sendall("{} has left the chat.".format(
                self.username).encode("ascii"))
            #close socket
            self.socket.close()
            os._exit(0)
        else:
            self.socket.sendall("{}: {}".format(self.username, emoji.emojize(message)).encode("ascii"))

def main(host, port):
    #GUI of program
    client = ChatroomGUI(host, port)
    receive = client.start()

    #Create window for gui
    window = tk.Tk()

    #dimensions of window
    window.geometry("300x200")

    #Title
    window.title("Socket Server Chatroom")

    #Box of TEXT messages
    MsgBox = tk.Frame(master=window)
    messages = tk.Listbox(master=MsgBox)
    messages.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
    client.messages = messages
    receive.messages = messages
    MsgBox.grid(row=0, column=3)

    #Textbox for input
    colOne = tk.Frame(master=window)
    #accept single-line text strings from a user.
    msgTextBox = tk.Entry(master=colOne)
    msgTextBox.pack(side=tk.RIGHT, expand=True)
    #input of text message
    msgTextBox.bind("<Return>", lambda x: client.send(msgTextBox))
    msgTextBox.insert(0, "Type here!")
    colOne.grid(row=6, column=3)

    #Send button
    sendMsgButton = tk.Button(
        master=window,
        text="Send",
        width=8,
        command=lambda: client.send(msgTextBox)
    )
    sendMsgButton.grid(row=6, column=1)

    #deploy
    window.mainloop()

#make it so you can only call for server starting up once
def counter():
    global numUsers
    if numUsers == 0:
        (Server("127.0.0.1", int(1060))).start()
        addCounter()
def addCounter():
    global numUsers
    numUsers = numUsers + 1
    return numUsers

#start up program
if __name__ == '__main__':
    #start up server on socket 127.0.0.1 and port 1060
    counter()
    #get input from user(s)
    socketValue = simpledialog.askstring("Input", "Type socket value:", parent=tk.Tk())
    portValue = simpledialog.askstring("Input", "Type port value:", parent=tk.Tk())
    #start main with users given socket and port values
    #main((socketValue), int(portValue))
    main("127.0.0.1", int(1060))
