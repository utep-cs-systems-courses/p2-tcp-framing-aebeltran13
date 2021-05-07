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
            print("-Waiting for request-")
            filename = ""
            buff = self.conn.recv(100).decode()

            frameLen, dataLen = split(buff)
            filenameLen = buff[:frameLen-1]
            #drop the frame size data so only message is left
            buff = buff[frameLen:dataLen]
            #Get the actual message by comparing the file size and data index.
            while(buff):
                if len(buff) < dataLen-frameLen:
                    buff += self.conn.recv(100).decode()
                else:
                    filename = buff[:dataLen]
                    buff = buff[dataLen:]

            print("Checking for |%s|" % filename)
            if os.path.exists(filename):
                self.conn.send(b"N")
                sys.exit(1)

            #File exists so we reply with a Y to signal the client to send the data
            self.conn.send(b"Y")
            print("File does not exist. Starting to write.")
            fileData = ""
            buff = self.conn.recv(100).decode()

            frameLen, dataLen = split(buff)
            fileDataLen = buff[:frameLen-1]
            buff = buff[frameLen:dataLen]
            while(buff):
                if len(buff) < dataLen-frameLen:
                    buff += self.conn.recv(100).decode()
                else:
                    fileData = buff[:dataLen]
                    buff = buff[dataLen:]

            print("\"\"\"\n",fileData,"\n\"\"\"")
            lock.acquire()
            try:
                fd = os.open(filename, os.O_CREAT | os.O_WRONLY)
                os.write(fd,fileData.encode())
                os.close(fd)
            except:
                print("Failed to create file")

            lock.release()
            sys.exit(0)

def split(msg):
    size = ""
    while(msg[0].isdigit()):
        size += msg[0]
        msg = msg[1:]

    if size.isnumeric():
        frameLen = len(size) + 1 #+1 is the ':'
        dataLen = int(size) + (len(size) + 1)
        return frameLen, dataLen
    else:
        return 0, 0