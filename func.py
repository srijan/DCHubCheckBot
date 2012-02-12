#!/usr/bin/env python
### fumc.py version 0.1 
###

import socket, array, fcntl, struct

#convert string to hex
def toHex(s):
    lst = []
    for ch in s:
        hv = hex(ord(ch)).replace('0x', '')
        if len(hv) == 1:
            hv = '0'+hv
        lst.append(hv)
    
    return reduce(lambda x,y:x+y, lst)


def findfreeport(startport, endport):
        serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)   
        port = startport
        while port < endport:
                try:
                        serversocket.bind(('localhost', port))
                # You may want: serversocket.bind((socket.gethostname(), port))
                except socket.error as e:
                        if e.errno==98:
                                port = port+1
                        else:
                                raise
                                
                else:
                        break
        serversocket.close()
        print "Found port", port
        return port


def get_ip_address(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,  # SIOCGIFADDR
        struct.pack('256s', ifname[:15])
    )[20:24])

def lock_to_key(lock):
        # "lock" must be the exact lock character sequence, not the whole command.
# i.e. if the command is $Lock blah pk=bleh|, lock should be "blah"

        "Decrypts lock to key."
        key = {}
        for i in xrange(1, len(lock)):
                key[i] = ord(lock[i]) ^ ord(lock[i-1])
                key[0] = ord(lock[0]) ^ ord(lock[len(lock)-1]) ^ ord(lock[len(lock)-2]) ^ 5
        for i in xrange(0, len(lock)):
                key[i] = ((key[i]<<4) & 240) | ((key[i]>>4) & 15)
                out = ""
        for i in xrange(0, len(key)):
                if key[i] in (0, 5, 36, 96, 124, 126):
                        out += "/%%DCN%03d%%/" % (key[i],)
        else:
                out += chr(key[i])
        return out

def lock2key2(lock):
        "Generates response to $Lock challenge from Direct Connect Servers"
        #print 'Generating $Key from: '+lock
        lock = array.array('B', lock)
        ll = len(lock)
        key = list('0'*ll)
        for n in xrange(1,ll):
            key[n] = lock[n]^lock[n-1]
        key[0] = lock[0] ^ lock[-1] ^ lock[-2] ^ 5
        for n in xrange(ll):
            key[n] = ((key[n] << 4) | (key[n] >> 4)) & 255
        result = ""
        for c in key:
            if c in (0, 5, 36, 96, 124, 126):
                result += "/%%DCN%.3i%%/" % c
            else:
                result += chr(c)
        return result

def readsock_counted(sock,count):
        buff = ""
        sock.settimeout(0.13)
        while True:
            try:
                while True:
                    t = sock.recv(1)
                    buff += t
                    #print '\n len='+str(len(buff))
                    #print info on each 10k
                    lb=len(buff)
                    if lb%10000==0: print "Already got "+str(lb)+" of "+str(count)
                    
                    
                    if len(buff)>=count: return buff
                    
            except socket.timeout:
            
                pass    # ?????????, ?? ????? ?? ????????? ?????
            except socket.error, msg:
                return    # ???????????? ?????? ??????
        # ????? ? buff ????? ????? ?????, ?????? ? ??? ????? ??????? ?????????...
        return buff

def readsock_counted_debug(sock,count):
        buff = ""
        sock.settimeout(0.13)
        while True:
            try:
                while True:
                    t = sock.recv(1)
                    buff += t
                    #print '\n len='+str(len(buff))
                    #print info on each 10k
                    lb=len(buff)
                    if lb%(10*1024)==0:
                        print "Already got "+str(lb)+" of "+str(count)+" "+str(100*lb/count)+"% completed"
                        #print buff
                    
                    if len(buff)>=count: return buff
                    
            except socket.timeout:
            
                pass    # ?????????, ?? ????? ?? ????????? ?????
            except socket.error, msg:
                return    # ???????????? ?????? ??????
        # ????? ? buff ????? ????? ?????, ?????? ? ??? ????? ??????? ?????????...
        return buff


def readsock(sock):
        buff = ""
        sock.settimeout(0.13)
        while True:
            try:
                while True:
                    t = sock.recv(1)
                    if t != '|': buff += t
                    else: return buff
            except socket.timeout:
            
                pass    # ?????????, ?? ????? ?? ????????? ?????
            except socket.error, msg:
                return    # ???????????? ?????? ??????
        # ????? ? buff ????? ????? ?????, ?????? ? ??? ????? ??????? ?????????...
        return buff
