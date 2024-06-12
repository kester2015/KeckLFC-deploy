## How to test keyword read/write

* Important files:

1. `nslfcd`: this is the dispatcher code.
2. `LFCm.xml.sin`: this is the full xml file, where KTL keywords are defined. Several parameters that are not inputs of the KTL dispatcher (such as normal polling rate, fast polling rate) are included.
> Feel free to implement new keywords here
3. `LFC.xml.sin`: this is another xml file, a trimmed version of `LFCm.xml.sin`, used as input for the KTL dispatcher. Do not edit this directly, always edit `LFCm.xml.sin`.
4. `copy_xml.py`: this is a script for generating `LFC.xml.sin` from `LFCm.xml.sin`, and transferring the xml files and `nslfcd` dispatcher code to irastrocombbuild. This makes sure that the xml files in the Windows laptop and in the irastrocombbuild are the same.
5. `server.py`: this is the ICE server file.

* How to prepare read/write tests:

0. Implement keywords in `LFCm.xml.sin` and related functions in `KeckLFC.py`.
> All the keywords that are listed in `LFCm.xml.sin` should have the corresponding method defined in `KeckLFC.py`.
> KTLXML documentation: https://spg.ucolick.org/KTLXML/
1. Transfer most up-to-date dispatcher and xml files to irastrocombbuild, by running `copy_xml.py`. 
2. Open two terminals in irastrocombbuild. (`ssh combbld@irastrocombbuild` in the PowerShell)
3. In one of the terminals, go to `/kroot/src/kss/astrocomb/`, and compile the dispatcher by `make install`.


Now you are ready to test! If you haven't made changes in `LFCm.xml.sin` or `nslfcd`, these steps 0-3 can be skipped.

* How to test read/write:

1. Run the ICE server first, in Windows machine, by: `python server.py` (the `server.py` file in the current directory)
2. When you see the message, ICE server starts ..., it's ready to start the dispatcher. In irastrocombbuild, run
`/kroot/rel/default/sbin/nslfcd  -c /kroot/rel/default/data/nslfc/nslfc_3.conf`
If the ICE connection is successful, you'll see the messages "Keyword KEYWORDNAME is connected to ICE". 
3. To test keyword read, in another irastrocombbuild terminal, run
`show -s nslfc KEYWORDNAME`
Note that it may take up to the keyword read period to store the device value to the dispatcher.
4. To test keyword write, run
`modify -s nslfc KEYWORDNAME=newvalue`

## Details on keywords

Useful references:  
https://spg.ucolick.org/DFW/keyword.html  
https://spg.ucolick.org/KTLXML/  

KTL keywords in the dispatcher are defined as DFW.Keyword.Basic classes, and different types of keywords are defined as subclasses of it, DFW.Keyword.KEYWORDTYPE (DFW.Keyword.Integer, DFW.Keyword.String, ...). In the dispatcher code, I defined subclasses of them, `IntegerIce, DoubleIce, EnumeratedIce, StringIce, BooleanIce, DoubleArrayIce`, which inherit from the DFW.Keyword.KEYWORDTYPE classes. Each keywords' `read()`, `write()`, `postwrite()`, `update()` are modified to communicate with the ICE server. 

All the KTL keyword values passed by the dispatcher are in string formats. When a user modifies the keyword value, `modifiedkeyword()` is invoked in `server.py`, setting the keyword value (`__setitem()__`) method. The string format keyword values are converted to desired keyword types here by `convert_type()`. Then they are fed to the keyword functions in the write block. If the write block returns 0, the value is stored in the keyword dictionary, `self.keywords`.

When accessing the keyword values stored in the KeckLFC class in the dictionary, simply : `self.keywords[KEYWORDNAME]`. The array keyword is stored as list (was originally string with spaces... this is updated!)


## How ICE connection works

The `server.py` python script in this directory does following:

1. reads list of keywords from `LFCm.xml.sin` xml file,
2. starts KeckLFC, which has all the functions corresponding to the keywords defined.
3. establishes ICE connection of each keyword when KTL dispatcher (ICE client) starts running.
   
   The dispatcher can be run in astrocombbuild (for now) by:
   `/kroot/rel/default/sbin/nslfcd  -c /kroot/rel/default/data/nslfc/nslfc_3.conf`

### Detailed explanation on how ICE connection works:

When the KTL dispatcher (ICE client) is started, the dispatcher also reads list of keywords from the same xml file `LFCm.xml.sin` living in the astrocomb server.
(** so the `LFCm.xml.sin` files in the two computers should be identical!)

In the dispatcher startup, 
In `setupKeywords()` (in KTL), each KTL keyword class is modified such that
    - `read()` method is called periodically, which invokes `receive()` method in the LfcI class. Then it calls the associated function in KeckLFC with input value=None and stores the returned value.
    - when a new keyword value is written from the user side, `write()` method is called in KTL, which in turn invokes `modifiedkeyword()` method in the LfcIclass. Then the keyword value from KTL is translated (convert_type in KeckLFC) and stored in KeckLFC.


For a successful ICE connection with the KTL layer,
1. The server (this laptop) and the client (astrocomb server) should share the same keyword list file (LFC.xml.sin).
2. The functions that correspond to each keyword should be defined in KeckLFC. Even if the middle layer development (functions corresponding to KTL keywords) is incomplete, the functions still need to be defined. In that case, just do:
    
     `def KEYWORD_NAME(self, value=None): return`





## KTL keywords and linking to the KeckLFC class

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
