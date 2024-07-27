import signal, sys, time, Ice

Ice.loadSlice('KtlIce.ice')
import Demo

sys.path.append('../')

icetest_mode = False
use_mock = False

#import random, threading
if not use_mock:
    print("KeckLFC starts")
    from KeckLFC import *
else:
    print("mockKeckLFC starts")
    from mockKeckLFC import *



class LfcI(Demo.Lfc):

    def __init__(self):

        #== List of the KTL keywords that should be monitored
        #self.keyword_names = ['ICEINT','ICEBOOL','ICEENUM','ICESTRING', 'ICESTA']
        if icetest_mode:
            keyword_names, keyword_types = parse_xml('testLFC.xml.sin')
        else:
            keyword_names, keyword_types = parse_xml('LFC.xml.sin')

        self.keyword_names = keyword_names

        #== Define mockKeckLFC class object as mkl
        if use_mock:
            self.mkl = mockKeckLFC()
        else:
            self.mkl = KeckLFC()

        print('ICE server starts ...\n')

        #self.ncalls = 0

    def modifiedkeyword(self, name, value, current):
        ''' This function is used by the dispatcher. 
        KTL dispatcher communicates with ICE when keyword value is changed. '''

        self.mkl[name] = value
        #self.mkl.__setitem__(name, value) # = value
        print(' Keyword <%s> changed to %s' % (name, value))

    def receive(self, name, current):
        ''' This function is used by the dispatcher.
        Sends the keyword values stored in KeckLFC class to the dispatcher'''

        val = self.mkl[name]
        return str(val)  #self.mkl.__getitem__(name) #str(self.mkl.keywords[name]) #self.ncalls

    def keylist(self, current):
        ''' This function is used by the dispatcher '''
        return self.keyword_names

    def cleanup(self, current):
        print('cleaning up')
        # self.mkl.stop_clock()
        if self.mkl.arduino != None: 
            self.mkl.arduino.disconnect()
            print('arduino disconnected!')

        # the command below shuts down the server. maybe we don't want that
        # when the dispatcher shuts down
        # current.adapter.getCommunicator().shutdown()
    
    def shutdown(self, current):
        ''' currently this is not used - dispatcher shutting down the server '''
        current.adapter.getCommunicator().shutdown()


with Ice.initialize(sys.argv, 'config.server') as communicator:
    signal.signal(signal.SIGINT, lambda signum, frame: communicator.shutdown())

    #
    # The communicator initialization removes all Ice-related arguments from argv
    #
    if len(sys.argv) > 1:
        print(sys.argv[0] + ": too many arguments")
        sys.exit(1)

    adapter = communicator.createObjectAdapter("Lfc")
    adapter.add(LfcI(), Ice.stringToIdentity("lfc"))
    adapter.activate()
    communicator.waitForShutdown()
