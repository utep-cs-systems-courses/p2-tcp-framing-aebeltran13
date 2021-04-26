
import socket, sys, re, os
sys.path.append("../lib")       # for params
import params
import threading
from workerThread import Worker

switchesVarDefaults = (
    (('-l', '--listenPort') ,'listenPort', 50001),
    (('-?', '--usage'), "usage", False), # boolean (set if present)
    )



progname = "fileTransferServer"
paramMap = params.parseParams(switchesVarDefaults)

listenPort = paramMap['listenPort']
listenAddr = ''       # Symbolic name meaning all available interfaces

if paramMap['usage']:
    params.usage()

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((listenAddr, listenPort))
s.listen(1)        #This will allow only one outstanding request
# s is a factory for connected sockets

'''
lock = threading.Lock()
#Change directory to where received files will be written to
os.chdir("./receivedFiles")
'''

print("waiting for client:")
os.chdir("./receivedFiles") #This is where files will be written to
while True:
    conn, addr = s.accept()  # wait until incoming connection request (and accept it)
    worker = Worker(conn, addr)
    worker.start()

