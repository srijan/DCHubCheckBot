#!/usr/bin/env python2
# @author: Srijan Choudhary

from botclass import *
from func import *
import socket
import select
import redis
from netaddr import IPNetwork
import string
import time
import signal

rc = redis.StrictRedis()
socket.setdefaulttimeout(0.05)

class TimeoutException(Exception):
    pass

def timeout_handler(signum,frame):
    raise TimeoutException()

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

        old_handler = signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(600)   # trigger alarm in 10 mins

        try:
            while True:
                ready = select.select([self.serversocket],[],[],1)
                #print "select.select"
                if ready[0]:
                    t = readsock(self.serversocket)
                    if t != '':
                        if t[0] == '$':
                            #print t
                            hubmsg = t.split()
                            if hubmsg[0] == '$Lock':
                                self.serversocket.send('$Key '+lock2key2(hubmsg[1]) + '|' + '$ValidateNick ' + self.botnick + '|')
                            if hubmsg[0] == '$Hello':
                                self.serversocket.close()
                                return True
                else:
                    break
        except TimeoutException:
            print "Unending loop detected.. Exiting.."
        finally:
            signal.signal(signal.SIGALRM, old_handler)

        signal.alarm(0)
        self.serversocket.close()
        return False

    def getHubDetails(self):
        hub = dict({'active': False, 'name': "", 'users': 0, 'ops': 0})
        try:
            self.serversocket.connect((self.HOST,self.PORT))
        except Exception,e:
            self.serversocket.close()
            return hub

        old_handler = signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(10)   # trigger alarm in 10 seconds

        try:
            while True:
                ready = select.select([self.serversocket],[],[],1)
                if ready[0]:
                    t = readsock(self.serversocket)
                    if t != '':
                        if t[0] == '$':
                            #print t
                            hubmsg = t.split()
                            if hubmsg[0] == '$Lock':
                                self.serversocket.send('$Key '+lock2key2(hubmsg[1]) + '|' + '$ValidateNick ' + self.botnick + '|')
                                hub['active'] = True
                            if hubmsg[0] == '$HubName':
                                hub['name'] = string.join(hubmsg[1:])
                                hub['active'] = True
                            if hubmsg[0] == '$Hello':
                                hub['active'] = True
                                break
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
                else:
                    break
        except TimeoutException:
            print "Unending loop detected.. Exiting.."
        finally:
            signal.signal(signal.SIGALRM, old_handler)

        signal.alarm(0)
        self.serversocket.close()
        return hub


subnetList = [
                "172.16.1.0/24",    "172.16.2.0/24",    "172.16.3.0/24",
                "172.16.4.0/24",    "172.16.5.0/24",    "172.16.6.0/24",
                "172.16.7.0/24",    "172.16.8.0/24",    "172.16.9.0/24",
                "172.16.10.0/24",   "172.16.11.0/24",   "172.16.12.0/24",
                "172.16.13.0/24",   "172.16.14.0/24",   "172.16.15.0/24",
                "172.16.16.0/24",   "172.16.17.0/24",   "172.16.18.0/24",
                "172.16.19.0/24",   "172.16.20.0/24"#,   "172.17.1.0/24",
                #"172.17.2.0/24",    "172.17.3.0/24",    "172.17.4.0/24",
                #"172.17.5.0/24",    "172.17.6.0/24",    "172.17.7.0/24",
                #"172.17.8.0/24",    "172.17.9.0/24",    "172.17.10.0/24"#,
                #"172.17.11.0/24",   "172.17.12.0/24",   "172.17.13.0/24"
             ]
fileName = '/srv/http/hublist.txt'

def checkHub(host,port):
    hcb = HubCheckBot()
    hcb.initBot(host,port)
    return hcb.check()

def addToDb(ip):
    print "Adding ",ip
    rc.zadd("hublist",1,ip)

def generateMainList():
    for subnet in subnetList:
        for ip in IPNetwork(subnet).iter_hosts():
            if checkHub(ip,411):
                addToDb(ip)

def checkMainList():
    h = HubCheckBot()
    serverList = ["","Auto Updated HubList",""]
    for entry in rc.zrevrange("hublist",0,-1,'withscores'):
        ip = entry[0]
        score = entry[1]
        print ip,score
        h.initBot(ip,411)
        hub = h.getHubDetails()
        #serverLine = "dchub://" + str(ip) + "/\t[Score " + str(score) + "]\t("
        serverLine = "dchub://" + str(ip) + "/\t("
        if hub['active']:
            serverLine += "On"
            #rc.zincrby("hublist",ip,0.1)
        else:
            serverLine += "Off"
        serverLine += "line)\t" + hub['name']
        serverList.append(serverLine)
    serverList.append("")
    serverList.append("Last updated at: "+time.strftime('%I:%M %p, %b %d, %Y'))
    serverList.append("Anyone interested in the code can look here: https://github.com/srijan/DCHubCheckBot")
    print time.strftime('%I:%M %p, %b %d, %Y'), '-- MARK --'
    f = open(fileName, "w")
    for s in serverList:
        f.write(s)
        f.write('\n')
    f.close()

count = 0
while True:
    if count == 6:
        generateMainList()
        count = 0
    checkMainList()
    count+=1
    time.sleep(600)

#print checkHub("172.16.12.39",411)
#generateMainList()
