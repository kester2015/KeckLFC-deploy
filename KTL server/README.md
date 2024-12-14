# Comb KTL service Overview

The software controlling the LFC (KeckLFC) lives in the Windows machine, and this is interfaced with the KTL service “comb” (running in IRASTROCOMB server) via the ICE. 

The `server.py` file in this directory is the ICE server script. 
The KTL dispatcher "comb" is the ICE client.

A user can access the LFC-related keywords via "comb" KTL dispatcher (ICE client),
which then talks to the ICE server to poll or modify keyword values.

To operate the comb through the KTL, the ICE server should be running and the ICE connection should be established. 

The dispatcher and the ICE server are still in the development phase, and are currently running with limited keywords (as of Aug 16th, 2024). 

# Establishing the ICE connection

Normally, the ICE server and the dispatcher (ICE client) should be always running and connected via ICE. This can be checked from the KTL side using the ICESTA keyword by

->**show -s comb icesta**<-

If it says “Connected”, the ICE server and the dispatcher connection is normal. Ready to use show/modify commands to read/set the LFC status.

If it says **“Disconnected”**, this is because either the ICE server is not running, or the ICE server is running but the ICE connection is lost (this can happen when the ICE server is restarted). If the ICE server is not running, someone has to start the ICE server from the LFC laptop (nothing can be done from the KTL side). This can be done by Jinhao or Yoo Jung (as of Aug 16th, 2024). If the ICE server is running but the ICE connection is lost, a KTL user can retry the connection by

->**modify -s comb icesta=3**<-

Then after a few seconds, try the show command again to check the status. 

To make sure if the ICE connection is successful, ICECLK keyword can be useful,

->**show -s comb iceclk**<-

This keyword is updated every 15 seconds. This keyword value should be real-time (<15 seconds) if the ICE connection is established.

If for some reason these commands do not work, one may try restarting the dispatcher (see the dispatcher basics section below). If none of these work contact Yoo Jung (hoping that doesn’t happen)

# Notes for developers

### Important files in the LFC windows laptop

1. `combd.sin`: this is the dispatcher code.
2. `LFC.xml.sin`: this is the full xml file, where KTL keywords are defined. 
3. `server.py`: this is the ICE server file.
4. `KTLIce.ice`, `config.server`, (`config.client` in irastrocombbuild): ICE related files


### Starting the server
Simply start the ICE server by
``` 
python server.py
```

### Starting the dispatcher
Log in to irastrocomb and start the dispatcher
``` 
ssh combbld@irastrocomb
astrocomb start comb
```

### Making changes to keywords 

The keywords are defined in `LFC.xml.sin` file in this directory.
Always make sure that 
1. corresponding methods of all the keywords in `LFC.xml.sin` file are defined in `KeckLFC.py`.
2. `LFC.xml.sin` file in this directory (the file used by ICE server) and `LFC.xml.sin` file in irastrocombbuild server (/kroot/src/kss/astrocomb/comb/ktlxml/LFC.xml.sin) are the same and are deployed to irastrocomb (the file used by KTL dispatcher, the ICE client).

To deploy changes in `LFC.xml.sin`, follow these steps:
1. copy `LFC.xml.sin` file to irastrocombbuild
``` 
scp LFC.xml.sin combbld@irastrocombbuild:/kroot/src/kss/astrocomb/comb/ktlxml/LFC.xml.sin
```
2. log in to irastrocombbuild and make install
``` 
ssh combbld@irastrocombbuild
cd /kroot/src/kss/astrocomb/comb/
make install
```
3. deploy to irastrocomb
``` 
kdeploy -a
```
4. log into irastrocomb and restart the dispatcher
``` 
ssh combbld@irastrocomb
astrocomb restart comb
```


### Making changes to dispatcher code

The KTL dispatcher code is `combd.sin`.
Edit the file and copy to irastrocombbuild
``` 
scp combd.sin combbld@irastrocombbuild:/kroot/src/kss/astrocomb/comb/dispatcher/combd.sin`
```
and do the same make install and kdeploy steps


### Details on keywords

Useful references:  
https://spg.ucolick.org/DFW/keyword.html  
https://spg.ucolick.org/KTLXML/  

KTL keywords in the dispatcher are defined as DFW.Keyword.Basic classes, and different types of keywords are defined as subclasses of it, DFW.Keyword.KEYWORDTYPE (DFW.Keyword.Integer, DFW.Keyword.String, ...). In the dispatcher code, I defined subclasses of them, `IntegerIce, DoubleIce, EnumeratedIce, StringIce, BooleanIce, DoubleArrayIce`, which inherit from the DFW.Keyword.KEYWORDTYPE classes. Each keywords' `read()`, `write()`, `postwrite()`, `update()` are modified to communicate with the ICE server. 

All the KTL keyword values passed by the dispatcher are in string formats. When a user modifies the keyword value, `modifiedkeyword()` is invoked in `server.py`, setting the keyword value (`__setitem()__`) method. The string format keyword values are converted to desired keyword types here by `convert_type()`. Then they are fed to the keyword functions in the write block. If the write block returns 0, the value is stored in the keyword dictionary, `self.keywords`.

When accessing the keyword values stored in the KeckLFC class in the dictionary, simply : `self.keywords[KEYWORDNAME]`. The array keyword is stored as list (was originally string with spaces... this is updated!)


### How ICE connection works

The `server.py` python script in this directory does following:

1. reads list of keywords from `LFCm.xml.sin` xml file,
2. starts KeckLFC, which has all the functions corresponding to the keywords defined.
3. establishes ICE connection of each keyword when KTL dispatcher (ICE client) starts running.
   

### Detailed explanation on how ICE connection works:

When the KTL dispatcher (ICE client) is started, the dispatcher also reads list of keywords from the same xml file `LFC.xml.sin` living in the astrocomb server.
(** so the `LFC.xml.sin` files in the two computers should be identical!)

In the dispatcher startup, 
In `setupKeywords()` (in KTL), each KTL keyword class is modified such that
    - `read()` method is called periodically, which invokes `receive()` method in the LfcI class. Then it calls the associated function in KeckLFC with input value=None and stores the returned value.
    - when a new keyword value is written from the user side, `write()` method is called in KTL, which in turn invokes `modifiedkeyword()` method in the LfcIclass. Then the keyword value from KTL is translated (convert_type in KeckLFC) and stored in KeckLFC.


For a successful ICE connection with the KTL layer,
1. The server (this laptop) and the client (astrocomb server) should share the same keyword list file (LFC.xml.sin).
2. The functions that correspond to each keyword should be defined in KeckLFC. Even if the middle layer development (functions corresponding to KTL keywords) is incomplete, the functions still need to be defined. In that case, just do:
    
     `def KEYWORD_NAME(self, value=None): return`



### KTL keywords and linking to the KeckLFC class

In `KeckLFC.py`, the KeckLFC class reads the xml file `LFC.xml.sin`, stores the keyword names and values as dictionaries in `self.keywords`.
The functions are defined as the same name as the keyword.

``` ruby
    def KEYWORD(self, value=None):
        if value == None: 
            # This is called periodically (keyword read)
            # Insert some function to execute when this keyword is being read and return the value
            # If you don't want the KeckLFC class to modify this keyword (such as ICESTA, the keyword showing the status of the ICE connection), no need to return a value               
            return 
        
        else:
            # This is called when user modifies the keyword (keyword write)
            # Insert some function to execute when user modifies this keyword
            # If it's successful, return 0
            return 0 # return 
```
