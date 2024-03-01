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
