import socket, sys, re, os
sys.path.append("../lib")
import params
import threading
from threading import Thread

lock = threading.Lock()

class Worker(Thread):
    def __init__(self, conn, addr):
        Thread.__init__(self)
        self.conn = conn
        self.addr = addr

    def run(self):
        print("Connection made by: ", self.addr)
        while True:
            try:
                print("-Waiting for request-")
                clientMessage = conn.recv(1024).decode()
                message = clientMessage.split(':;:') #split file name from data
                fileName = message[0].decode()
                fileData = message[1].decode()
                print("-File Received!-")
            except:
                print("-File transfer FAILED-")
                sys.exit(1)

            lock.acquire()

            try:
                newFile = open(fileName, "w")
                newFile.write(fileData)
                newFile.close()
            except:
                print("Failed to create file")

            lock.release()
            sys.exit(0)
