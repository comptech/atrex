CC = g++ 

../ctheta.so : calctheta.cpp
	${CC}  -ansi -fPIC -pedantic -shared  -o $@ $? -lc

../ctheta.dll : calctheta.cpp
	${CC}  -ansi -fPIC -pedantic -shared  -o $@ $? 
