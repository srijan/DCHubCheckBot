#!/usr/bin/env python2
# @author: Srijan Choudhary

from botclass import *
from func import *
import socket
import select
import redis
from netaddr import IPNetwork
import string

rc = redis.StrictRedis()
socket.setdefaulttimeout(0.02)

class HubCheckBot(PyBot):
    botnick = "HubCheckBot"
    HOST = "172.16.3.117"
    PORT = 411
    botif = "eth0"
    botip = "172.16.3.117"
    debug = 1
    sharesize = '1501200000000'
    ownernick = "n0w0nd3r"
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    nicklist = []
    oplist = []

    def initBot(self,host,port):
        self.HOST = str(host)
        self.PORT = port
        self.serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def check(self):
        try:
            self.serversocket.connect((self.HOST,self.PORT))
        except Exception,e:
            self.serversocket.close()
            return False
        ready = select.select([self.serversocket],[],[],1)
        if ready[0]:
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
        self.serversocket.close()
        return False

    def getHubDetails(self):
        hub = dict({'active': True, 'name': "", 'users': 0, 'ops': 0})
        try:
            self.serversocket.connect((self.HOST,self.PORT))
        except Exception,e:
            self.serversocket.close()
            hub['active'] = False
            return hub
        ready = select.select([self.serversocket],[],[],1)
        if ready[0]:
            while True:
                t = readsock(self.serversocket)
                #print t
                if t != '':
                    if t[0] == '$':
                        hubmsg = t.split()
                        if hubmsg[0] == '$Lock':
                            self.serversocket.send('$Key '+lock2key2(hubmsg[1]) + '|' + '$ValidateNick ' + self.botnick + '|')
                        if hubmsg[0] == '$HubName':
                            hub['name'] = string.join(hubmsg[1:])
                        if hubmsg[0] == '$Hello':
                            self.serversocket.close()
                            return hub
                            #self.serversocket.send('$Version 0.785|$MyINFO $ALL '+self.botnick+'$ $100$bot@bot.com$'+str(self.sharesize)+'|$GetNickList|')
                        """
                        if hubmsg[0]=='$NickList':
                            nicklist = hubmsg[1].split("$$")
                            hub['users'] = len(nicklist)
                        if hubmsg[0]=='$OpList':
                            oplist = hubmsg[1].split("$$")
                            hub['ops'] = len(oplist)
                            self.serversocket.close()
                            return hub
                        if hubmsg[0]=='$Search':
                            self.serversocket.close()
                            return hub
                        """
        self.serversocket.close()
        hub['active'] = False
        return hub

def checkHub(host,port):
    hcb = HubCheckBot()
    hcb.initBot(host,port)
    return hcb.check()


subnetList = [
                "172.16.1.0/24",    "172.16.2.0/24",    "172.16.3.0/24",
                "172.16.4.0/24",    "172.16.5.0/24",    "172.16.6.0/24",
                "172.16.7.0/24",    "172.16.8.0/24",    "172.16.9.0/24",
                "172.16.10.0/24",   "172.16.11.0/24",   "172.16.12.0/24",
                "172.16.13.0/24",   "172.16.14.0/24",   "172.16.15.0/24",
                "172.16.16.0/24",   "172.16.17.0/24",   "172.16.18.0/24",
                "172.16.19.0/24",   "172.16.20.0/24",   "172.17.1.0/24",
                "172.17.2.0/24",    "172.17.3.0/24",    "172.17.4.0/24",
                "172.17.5.0/24",    "172.17.6.0/24",    "172.17.7.0/24",
                "172.17.8.0/24",    "172.17.9.0/24",    "172.17.10.0/24",
                "172.17.11.0/24",   "172.17.12.0/24",   "172.17.13.0/24"
             ]

def addToDb(ip):
    print "Adding ",ip
    rc.sadd("hublist",ip)

def generateMainList():
    for subnet in subnetList:
        for ip in IPNetwork(subnet).iter_hosts():
            if checkHub(ip,411):
                addToDb(ip)

def checkMainList():
    h = HubCheckBot()
    for ip in rc.smembers("hublist"):
        h.initBot(ip,411)
        hub = h.getHubDetails()
        print ip,"\t:\t",hub['name'],
        if hub['active']:
            print " (Online)"
        else:
            print " (Offline)"


checkMainList()

#print checkHub("172.16.12.39",411)
#generateMainList()
