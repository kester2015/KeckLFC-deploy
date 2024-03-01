//
// Copyright (c) ZeroC, Inc. All rights reserved.
//

#pragma once

module Demo
{
    class Keyword
    {
        string name;
        string type;
        string value;
    }
    
    sequence<Keyword> KeywordSequence;    
    sequence<string> KeyNameSequence;
    

    interface Lfc
    {
        void initialkeywords(KeywordSequence keywords);
        KeyNameSequence keylist();
        void modifiedkeyword(string name, string value);
        string receive(string name);
        int errorstate();
        void shutdown();
    }
}
