#
# Makefile - Project 1
#	Author: Alexander Hoke
#	Date:	01/19/21
#

CC		= g++
OPT		= -std=c++11 -Wall -shared -fPIC
BOOST	= -lboost_regex
LIB		= lib_token

all: lib_token

lib_token:
	$(CC) $(OPT) $(STD) $(LIB).cpp $(LIB).hpp -o $(LIB).so $(BOOST)
	rm -rf *.o *.a

zip:
	zip -r Scanner lib_token.cpp lib_token.hpp lib_token.so Core.py Main.py \
	Scanner.py readme.txt tester.sh Correct/* Error/*

clean:
	rm -rf *.o *.a *.gch *.so