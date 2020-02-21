#!/usr/bin/env python3

import socket
import os
import os.path
from os import path
import selectors
import time
HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
PORT = 65432      # Port to listen on (non-privileged ports are > 1023)
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    # bind() is used to associate the socket with a specific network interface and port number:
    s.bind((HOST, PORT))
    print("Server on Host: " + HOST + ", on Port: " + str(PORT))
    s.listen()
    while (True):
        # accept the connection and address
        conn, addr = s.accept()
        with conn:
            print("Connected to/by", addr)
            while True:
                # accept connections from outside
                data = conn.recv(1024)
                if not data:
                    break
                recvCommand = data.decode().split(" ")
                recvWord = recvCommand[0]
                print("\nCOMMAND FROM CLIENT: ", recvCommand)
                if (recvWord == "LIST"):
                    print("Listing files in client directory...")
                    files = [f for f in os.listdir('.') if os.path.isfile(f)]
                    message = '\n'.join(files)
                    message = message.encode()
                    conn.sendall(message)
                elif (recvWord == "RETRIEVE"):
                    print("Client asked to Retrieve files!")
                    filetoSend = recvCommand[1]
                    # check if file is in server
                    if (path.exists(filetoSend)):
                        f = open(filetoSend, 'rb')
                        l = f.read(1024)
                        while (l):
                            conn.sendall(l)
                            l = f.read(1024)
                        conn.sendall("EOF".encode())
                        # removes file from server
                        os.remove(filetoSend)
                        f.close()
                    else:
                        print("File", str(filetoSend),
                              " doesnt exist on server.")
                        message = "File doesn't exist on server."
                        # Does not exist
                        conn.sendall("DNEIS".encode())
                elif (recvWord == "STORE"):
                    print("Client asked for Store.")
                    fileToStore = recvCommand[1]
                    f = open(recvCommand[1], 'wb')
                    while (True):
                        # receive data and write it to file
                        data = conn.recv(1024)
                        print("Server receiving data...")
                        print('data=%s', (data))
                        if not data:
                            break
                        # EOF sigals that the whole file has been retrieved
                        if data.decode()[-3:] == "EOF":
                            rawFile = data.decode()
                            ClippedFile = rawFile[:-3]
                            data = ClippedFile.encode()
                            f.write(data)
                            f.close()
                            break
                elif (recvWord == "QUIT"):
                    print("Client asked for Quit.")
                    print("Server has disconnected")
                    exit()
                else:
                    print("Invalid command.")
exit()