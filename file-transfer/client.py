
import socket, sys, re, time, os
sys.path.append("../lib")       # for params
import params

switchesVarDefaults = (
    (('-s', '--server'), 'server', "127.0.0.1:50001"),
    (('-d', '--delay'), 'delay', "0"),
    (('-?', '--usage'), "usage", False), # boolean (set if present)
    )


progname = "fileTransferClientl"
paramMap = params.parseParams(switchesVarDefaults)

server, usage  = paramMap["server"], paramMap["usage"]

if usage:
    params.usage()

try:
    serverHost, serverPort = re.split(":", server)
    serverPort = int(serverPort)
except:
    print("Can't parse server:port from '%s'" % server)
    sys.exit(1)

s = None
for res in socket.getaddrinfo(serverHost, serverPort, socket.AF_UNSPEC, socket.SOCK_STREAM):
    af, socktype, proto, canonname, sa = res
    try:
        print("creating sock: af=%d, type=%d, proto=%d" % (af, socktype, proto))
        s = socket.socket(af, socktype, proto)
    except socket.error as msg:
        print(" error: %s" % msg)
        s = None
        continue
    try:
        print(" attempting to connect to %s" % repr(sa))
        s.connect(sa)
    except socket.error as msg:
        print(" error: %s" % msg)
        s.close()
        s = None
        continue
    break

if s is None:
    print('could not open socket')
    sys.exit(1)

while True:
    print("Enter file you wish to send or 'QUIT' to exit:")
    fileName = os.read(0, 1024).decode()
    fileName = fileName.strip()
    filePath = ("files/" + fileName)
    #Check if user wants to exit program
    if fileName != "QUIT":
        #Check if file exists
        if os.path.exists(filePath):
            print("Sending %s" % fileName)
            
            #Framing file name
            fnLength = str(len(fileName)) + ":"
            fnLengthByte = bytearray(fnLength.encode())
            message = fnLengthByte + bytearray(fileName.encode())
            while len(message):
                sent = s.send(message)
                message = message[sent:]

            #Wait for server response to check if file exists
            reply = s.recv(100).decode()
            #File already exists. Server said NO
            if reply == "N":
                print("File already exists")
                continue
            #Server did not say Yes or No so it is an unknown response. Exit
            elif reply != "Y":
                print("Unknown response")
                continue

            #Server reponse was yes so we send rest of data.
            file = open(filePath, "r")
            data = file.read()
            #Check for empty file
            if(len(data) == 0):
                print("File is Empty!")
                continue
            dataLengthByte = bytearray((str(len(data)) + ":").encode()) 
            message = dataLengthByte + bytearray(data.encode())
            while len(message):
                sent = s.send(message)
                message = message[sent:]
            

        else:
            print("File not found...")
            continue
    else:
        print("Exiting..")
        s.close()
        sys.exit(0)
