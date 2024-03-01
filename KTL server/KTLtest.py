import sys
sys.path.append('..')
from Hardware.AndoOSA_AQ6315E import AndoOSA_AQ6315E

def scan():
    osa = AndoOSA_AQ6315E(addr="GPIB1::1::INSTR")
    osa.connect()
    osa.Single()
    print('Scanned')

import signal, sys, time, Ice

Ice.loadSlice('KtlIce.ice')
import Demo

class KTLKeyword:
    
    ''' A simple KTL Keyword class with read/write functions. 
        Usage: keyword = KTLKeyword(keywordname, keywordtype) '''
    
    def __init__(self, name, type):
        
        self.type = type
        self.name = name
        self.value = None
        
    
    def str2val(self):
        
        ''' Converts returned string values to desired types '''
        
        if (self.type != None):
            
            if self.type == 'STRING': self.value = self.strvalue
            if self.type in ['INT', 'ENUM']: 
                self.value = int(self.strvalue)
            if self.type in ['FLOAT', 'DOUBLE']:
                self.value = float(self.strvalue)
            if self.type == 'BOOLEAN': 
                if self.strvalue == 'False': self.value = 0
                if self.strvalue == 'True': self.value = 1
            
            # Need to implement: 'ENUMM','FLOAT_ARRAY','INT_ARRAY','MASK'

        else:
            self.value = None

    def printstring(self, prefix=''):
        ''' print values '''
        
        print(prefix+'%s : %s (%s)' % (self.name, self.strvalue, self.type))
        
    def setstr(self, strvalue):
        ''' Gets string values and stores as 
            self.strvalue as a string and 
            self.value as a corresponding type. '''
            
        self.strvalue = strvalue
        self.str2val()
        self.printstring(prefix='       Stored value  ')
           
    def readstr(self):
        ''' Reads string values '''
        return self.strvalue
    
    def gettype(self):
        ''' Reads type '''
        return self.type
    
    def read(self):
        ''' Reads values '''
        return self.value
    

class HelloI(Demo.Hello):
    def __init__(self):
        self._num = 0
        self.keys_to_monitor = ['KEYTEST','ICENCALL','TEMP','DISP3STA', 'ICESTA']
        self.logfile = 'log.log'
        
        
        self.keytest  = KTLKeyword('KEYTEST', 'BOOLEAN')
        self.icencall = KTLKeyword('ICENCALL', 'INT')
        self.temp     = KTLKeyword('TEMP', 'INT')
        self.disp3sta = KTLKeyword('DISP3STA', 'ENUM')
        self.icesta   = KTLKeyword('ICESTA', 'ENUM')
        
        self._keywords = [self.keytest, self.icencall, self.temp, self.disp3sta, self.icesta]
        
        print('ICE server starts ...')
        
    
    def initialkeywords(self, keywords, current):
        
        for i, keyword in enumerate(keywords):
        
            self._keywords[i].setstr(keyword.value)

        print('Initial keyword values are stored')
        
        for keyword in self._keywords:
            keyword.printstring()
                
 
    def logwrite(self, value):
        with open(self.logfile, 'a') as f:
            f.write(value)

    
    def modifiedkeyword(self, key, current):
        
        index = self.keys_to_monitor.index(key.name)
        self._keywords[index].setstr(key.value)
        print(' Keyword <%s> changed to %s' % (key.name, key.value))

        if (index == 0):
            if key.value == 'True':
                scan()
            else:
                print('not scanning')

        #print('(String)    Keyword <%s> changed to ' % (key.name), self._keywords[index].readstr())
        #print('(Converted) Keyword <%s> changed to %s' % (key.name, str(self._keywords[index].read())))
        
                
    
    def keylist(self, current):
        return self.keys_to_monitor
    
    def shutdown(self, current):
        current.adapter.getCommunicator().shutdown()
        

with Ice.initialize(sys.argv, 'config.server') as communicator:
    signal.signal(signal.SIGINT, lambda signum, frame: communicator.shutdown())

    #
    # The communicator initialization removes all Ice-related arguments from argv
    #
    if len(sys.argv) > 1:
        print(sys.argv[0] + ": too many arguments")
        sys.exit(1)

    adapter = communicator.createObjectAdapter("Hello")
    adapter.add(HelloI(), Ice.stringToIdentity("hello"))
    adapter.activate()
    communicator.waitForShutdown()
    