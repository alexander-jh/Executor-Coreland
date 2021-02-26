Project:	Project 2
Author:		Alexander Hoke
Date:		02/10/2021

------------------------------------- INCLUDED -----------------------------------------
Makefile				-	Build file for dynamic library.
lib_token.hpp			-	Header file for external lib
lib_token.cpp			-	Source code for external lib
lib_token.so 			-	Dynamicly compiled library
Core.py 				-	Supplied enumeration file
Main.py   				-	Executes the Parser
Scanner.py 				-	Script links external lib and executes
						-	scanner functions
Parser.py 				-	Consumers tokens from scanner

----------------------------------- INSTRUCTIONS ----------------------------------------
The lib_token.so library is pre-compiled in std-linux and is included so unless you're 
running via a different a OS/distro you *shouldn't* have to recompile. However, if there
are linker errors just run ```make``` to rebuild the library with appropriate linkage. 

If you do have to/choose to recompile the dynamic library Makefile is included just run:
```make```
```make clean```

Full compiler options (annotations below):
```g++ -Wall -shared -fPIC -std=c++11 lib_token.cpp lib_token.hpp -o lib_token.so 
		-lboost_regex```
	-Wall		Enables additional compiler flags
	-shared		Directs compiler that object files are shared enabling linking
	-fPIC		Genereates position-independent code which is machine code
			   which can be executed agnostic of memory addressing
	-std=c++11	Specify C++ version, unfortunately the most modern version
			   on std-linux is 11. Advantage of 11 is addition of auto,
			   lambda functions, direct looping over iterators, smart
			   pointers, and variable argument functions yet >=14 is 
			   optimal.
	-lboost_regex	Links the Boost/Regex.hpp library. Boost contains a variety
			   of open source libraries which are portable and not
			   OS dependent. While C++11 does introduce the std::regex 
			   library, it won't compile with GCC version < 4.9. 

To run the base program simply run:
```python3 Main.py <<*file_name*>>```
or
```./tester.sh```
if it fails to execute due to permissions
```chmod +x tester.sh```


----------------------------------- METHODOLOGY ------------------------------------------
For the sake of this project, an external C++11 library implements core functions using the standard Python CTypes wrapper in the Scanner.py class file. More information regarding
that implementation available in previous project readme.