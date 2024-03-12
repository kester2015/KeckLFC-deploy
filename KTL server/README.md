## How ICE connection works

The `server.py` python script in this directory does following:

1. reads list of keywords from "LFC.xml.sin" xml file,
2. starts KeckLFC, which has all the functions corresponding to the keywords defined.
3. establishes ICE connection of each keyword when KTL dispatcher (ICE client) starts running.
   
   The dispatcher can be run in astrocombbuild (for now) by:
   /kroot/rel/default/sbin/nslfcd  -c /kroot/rel/default/data/nslfc/nslfc_3.conf

* Detailed explanation on how ICE connection works:
When the KTL dispatcher (ICE client) is started, the dispatcher also reads list of keywords from the same xml file "LFC.xml.sin" living in the astrocomb server.
(** so the LFC.xml.sin files in the two computers should be identical!)
In setupKeywords (in KTL), each KTL keyword class is modified such that
- when the keyword is read (periodically), "receive" method in the LfcI class is called which then calls the associated function in KeckLFC with input value=None and stores the returned value.
- when the keyword value is modified from the KTL side, callback function is invoked in KTL. Each keyword's callback function is linked to "modifiedkeyword" method in the LfcIclass. Then the keyword value from KTL is translated (convert_type in KeckLFC) and stored in KeckLFC.


For a successful ICE connection with the KTL layer,
1. The server (this laptop) and the client (astrocomb server) should share the same keyword list file (LFC.xml.sin).
2. The functions that correspond to each keyword should be defined in KeckLFC. Even if the middle layer development (functions corresponding to KTL keywords) is incomplete, the functions still need to be defined. In that case, just do:
      --> def KEYWORD_NAME(self, value=None): return 

## Testing the ICE connection

1. First run the `server.py` to start the server
2. Start the dispatcher in irastrocombbuild (for now) by:
   /kroot/rel/default/sbin/nslfcd  -c /kroot/rel/default/data/nslfc/nslfc_3.conf
   If the connection is successful, you'll see the messages
   ```Keyword KEYWORDNAME connected to ICE```
3. To test if the keyword is stored in the KTL, open a terminal in irastrocombbuild and try:
    ```show -s nslfc KEYWORDNAME```
4. To test keyword write,
    ```modify -s nslfc KEYWORDNAME=value```


## Generating KTL keywords and linking to the KeckLFC class

### 1. KTL keywords csv file
Fill in the csv file (keywords.csv) with KTL keywords to implement,
run `python write_xml.py` to generate the xml file named LFC.xml.sin

### 2. Implement functions in KeckLFC.py
In `mockKeckLFC.py`, the mockKeckLFC class reads the xml file, stores the keyword names and values as dictionaries in `self.keywords`.
The functions are defined as the same name as the keyword.

``` ruby
    def KEYWORD(self, value=None):
        if value == None: 
            # This is called periodically
            # Insert some function to execute when this keyword is being read and return the value
            # If you don't want the KeckLFC class to modify this keyword, no need to return a value               
            return 
        
        else:
            # This is called when user modifies the keyword
            # Insert some function to execute when user modifies this keyword
            # If it's successful, return 0
            return 0 # return 
```
