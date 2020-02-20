#!/usr/bin/env python3
# msg.encode() //change to bytes
# msg.decode() //puts rerp(data.decode())

import socket
import os  # for listen command
import argparse


HOST = '127.0.0.1'  # The server's hostname or IP address
PORT = 65432        # The port used by the server

print("Client has been boosted up.")

getCommand = None
getStatement = None
quitProg = None
connect = 0
failedToConnect = True


def getInput():
    global getCommand
    global getStatement
    print("__________________________________________________")
    if (failedToConnect):
        getCommand = input(
            "Please tell me what you would like to do:\n - CONNECT \n - QUIT\n")
    elif (failedToConnect == False):
        getCommand = input(
            "Please tell me what you would like to do:\n - RETRIEVE  \n - LIST \n - STORE \n - QUIT\n")
    print("__________________________________________________")

    # For commands such as Connect, retrieve, and store that has
    # more than one worded command
    getStatement = getCommand.split(" ")
    # print("Client asked for: ", getCommand)


getInput()

while(True):

    # CLOSE CONNECTION
    if (getCommand == "QUIT"):
        break  # disconect from sever
    elif (getStatement[0] == "CONNECT" and len(getStatement) == 3):

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:

            # Server Address converted to it
            SP = int(getStatement[2])
            # Check if input is CONNECT <IP ADDRESS> <Int>
            if (isinstance(SP, int)):
                failedToConnect = False
                try:
                    s.settimeout(5)
                    s.connect((getStatement[1], SP))
                    print("Connecting...")

                except:
                    failedToConnect = True
                    print("Failed to connect.")
                    getInput()

                if(not failedToConnect):
                    print("Successfully Connected!")

                while (not failedToConnect):

                    getInput()

                    if (getCommand == "QUIT"):
                        s.sendall(getCommand.encode())
                        s.shutdown(socket.SHUT_RDWR)
                        s.close()
                        print("Client was disconnected.")
                        exit()

                    elif (getCommand == "LIST"):
                        # change command to bytes
                        s.sendall(getCommand.encode())
                        print("\nFILES FROM SERVER:")
                        data = s.recv(1024)
                        # Decode and print the list of files
                        files = data.decode()
                        files = files.split('\n')
                        for f in files:
                            print("  + ", f)
                        print("\n")

                    elif (getStatement[0] == "RETRIEVE"):
                        if (len(getStatement) == 2):
                            s.sendall(getCommand.encode())
                            FileRequested = getStatement[1]  # make a string?

                            # wb indicates that the file is opened for writing in binary mode.
                            f = open(FileRequested, 'wb')
                            print("File requested is: ", f)
                            print("File recieved is: ", s.recv(1024))
                            # see if file is in server
                            if (s.recv(1024) != "1"):
                                print('receiving data...')
                                data = s.recv(1024)
                                print("data: ", data)
                                # if not data:
                                #    break
                                # write data to file
                                f.write(data)
                                f.close()
                            else:
                                print("Server has no such file.")
                        else:
                            print("Retrieve command is: RETRIEVE <filename>")

                    elif (getStatement[0] == "STORE"):
                        if (len(getStatement) == 2):
                            s.sendall(getCommand.encode())
                            f = open(getStatement[1], 'rb')
                            l = f.read(1024)
                            while(l):
                                s.sendall(l)
                                l = f.read(1042)
                            s.sendall("EOF".encode())
                            f.close()
                            print(" File stored by server.")
                            os.remove(getStatement[1])
                        else:
                            print("Store command is: STORE <fileName>")
                    else:
                        print("invalid statement.")

    else:
        getInput()

print("Client was disconnected.")
