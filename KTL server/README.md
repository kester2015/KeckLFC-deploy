## How to test keyword read/write

Important files:

1. `nslfcd`: this is the dispatcher code.
2. `LFCm.xml.sin`: this is the full xml file, where KTL keywords are defined. Several parameters that are not inputs of the KTL dispatcher (such as normal polling rate, fast polling rate) are included.
3. `LFC.xml.sin`: this is another xml file, a trimmed version of `LFCm.xml.sin`, used as input for the KTL dispatcher. Do not edit this directly, always edit `LFCm.xml.sin`.
4. `copy_xml.py`: this is a script for generating `LFC.xml.sin` from `LFCm.xml.sin`, and transferring the xml files and `nslfcd` dispatcher code to irastrocombbuild.
5. `server.py`: this is the ICE server file.

How to prepare read/write tests:

0. Implement keywords in `LFCm.xml.sin` and related functions in `KeckLFC.py`.
1. Transfer most up-to-date dispatcher and xml files, by running `copy_xml.py`. 
2. Open two terminals in irastrocombbuild. (`ssh combbld@irastrocombbuild` in the PowerShell)
3. In one of the terminals, go to `/kroot/src/kss/astrocomb/`, and compile the dispatcher by `make install`.

Now you are ready to test!

How to test read/write:

1. Run the ICE server first, in Windows machine, by: `python server.py` (the `server.py` file in the current directory)
2. When you see the message, ICE server starts ..., it's ready to start the dispatcher. In irastrocombbuild, run
`/kroot/rel/default/sbin/nslfcd  -c /kroot/rel/default/data/nslfc/nslfc_3.conf`
If the ICE connection is successful, you'll see the messages "Keyword KEYWORDNAME is connected to ICE". 
3. To test keyword read, run
`show -s nslfc KEYWORDNAME`

Note that it make take up to the keyword read period to store the device value to the dispatcher.
4. To test keyword write, run
`modify -s nslfc KEYWORDNAME=newvalue`





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


## How ICE connection works

The `server.py` python script in this directory does following:

1. reads list of keywords from `LFC.xml.sin` xml file,
2. starts KeckLFC, which has all the functions corresponding to the keywords defined.
3. establishes ICE connection of each keyword when KTL dispatcher (ICE client) starts running.
   
   The dispatcher can be run in astrocombbuild (for now) by:
   `/kroot/rel/default/sbin/nslfcd  -c /kroot/rel/default/data/nslfc/nslfc_3.conf`

* Detailed explanation on how ICE connection works:
When the KTL dispatcher (ICE client) is started, the dispatcher also reads list of keywords from the same xml file "LFC.xml.sin" living in the astrocomb server.
(** so the LFC.xml.sin files in the two computers should be identical!)
In setupKeywords (in KTL), each KTL keyword class is modified such that
    - when the keyword is read (periodically), "receive" method in the LfcI class is called which then calls the associated function in KeckLFC with input value=None and stores the returned value.
    - when the keyword value is modified from the KTL side, callback function is invoked in KTL. Each keyword's callback function is linked to "modifiedkeyword" method in the LfcIclass. Then the keyword value from KTL is translated (convert_type in KeckLFC) and stored in KeckLFC.


For a successful ICE connection with the KTL layer,
1. The server (this laptop) and the client (astrocomb server) should share the same keyword list file (LFC.xml.sin).
2. The functions that correspond to each keyword should be defined in KeckLFC. Even if the middle layer development (functions corresponding to KTL keywords) is incomplete, the functions still need to be defined. In that case, just do:
    
     `def KEYWORD_NAME(self, value=None): return`

## Testing the ICE connection

1. First run the `server.py` to start the server
2. Start the dispatcher in irastrocombbuild (for now) by:
   `/kroot/rel/default/sbin/nslfcd  -c /kroot/rel/default/data/nslfc/nslfc_3.conf`
   If the connection is successful, you'll see the messages
   ```Keyword KEYWORDNAME connected to ICE```
3. To test if the keyword is stored in the KTL, open a terminal in irastrocombbuild and try:
    ```show -s nslfc KEYWORDNAME```
4. To test keyword write,
    ```modify -s nslfc KEYWORDNAME=value```


