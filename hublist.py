#!/usr/bin/env python2
# @author: Srijan Choudhary

from botclass import *
from func import *
import socket

socket.setdefaulttimeout(0.02)

class HubCheckBot(PyBot):
    botnick = "HubCheckBot"
    HOST = "172.16.3.117"
    PORT = 411
    botif = "eth0"
    botip = "172.16.3.117"
    debug = 1
    ownernick = "n0w0nd3r"
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def initBot(self,host,port):
        self.HOST = host
        self.PORT = port

    def check(self):
        try:
            self.serversocket.connect((self.HOST,self.PORT))
        except Exception:
            return False
        while True:
            t = readsock(self.serversocket)
            if t != '':
                if t[0] == '$':
                    hubmsg = t.split()
                    if hubmsg[0] == '$Lock':
                        self.serversocket.send('$Key '+lock2key2(hubmsg[1]) + '|' + '$ValidateNick ' + self.botnick + '|')
                    if hubmsg[0] == '$Hello':
                        self.serversocket.close()
                        return True


def checkHub(host,port):
    hcb = HubCheckBot()
    hcb.initBot(host,port)
    return hcb.check()

print checkHub("172.16.12.39",411)
