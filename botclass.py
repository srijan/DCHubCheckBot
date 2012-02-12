#!/usr/bin/env python
# -*- coding: cp1251 -*-
### botclass.py
### bot class definition v 0.1 alpha
from func import *
class PyBot:
    ### default settings
    HOST='hub'
    PORT=411
    debug=0
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sharesize=1024*1024*1024*100
    botnick = 'DefaultBot'
    botpassword='password'
    botip='127.0.0.1'
    ownernick='dr-evil'
    nicklist = []
    oplist=[]
    #Basic Message to chat
    def saytochat(self,message):
        self.serversocket.send('<'+self.botnick+'> '+message+'|')
        
    def saytochat_me(self,message):
        #we using /me for client parsing
        self.serversocket.send('<'+self.botnick+'> '+'/me '+message+'|')
        
    def saycommand(self,command):
        self.serversocket.send(command+'|')
        
        
    #Basic login to hub method. If we got any $Search - than everything is done
    def login(self):
        self.serversocket.connect((self.HOST,self.PORT))
        if self.debug==1: print 'Connection established'
        while 1:
            t=readsock(self.serversocket)
            if self.debug==1: print t
            if t!='':
                if t[0]=='$':
                    #we got message starting with $ (for example $Lock)
                    hubmsg=t.split()
                    if hubmsg[0]=='$Lock':
                        #we have $Lock message
                        self.serversocket.send('$Key '+lock2key2(hubmsg[1])+'|'+'$ValidateNick '+self.botnick+'|')
                        #if self.debug==1: print 'Sending $Key '+lock2key2(hubmsg[1])+'|'+'$ValidateNick '+self.botnick+'|'
                    if self.debug==1: print 'Got '+hubmsg[0]
                    if hubmsg[0]=='$Hello':
                        #we got $Hello so we need to answer with $Version <version>|$MyINFO <info string>|$GetNickList|
                        self.serversocket.send('$Version 1,0091|$MyINFO $ALL '+self.botnick+' simple python bot$ $100$bot@bot.com$'+str(self.sharesize)+'|$GetNickList|')
                    if hubmsg[0]=='$GetPass':
                            self.serversocket.send('$MyPass '+self.botpassword+'|')
                    if hubmsg[0]=='$NickList':
                            nicklist = hubmsg[1].split("$$")
                    if hubmsg[0]=='$OpList':
                            oplist = hubmsg[1].split("$$")
                            print 'Currently  '+str(len(nicklist))+' users online, including '+str(len(oplist))+ ' Operators'
                    if hubmsg[0]=='$Search':
                        #it seems that we have succesfully loggen on to hub :)
                        if self.debug >= 1:
                            print "Login complete."
                        
                        return
                
            
            
            
        return
    def processownercommands(self):
        return
    
    
    def workloop(self):
        #do things
        return    
       
    
    
    
