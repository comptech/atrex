CC = g++ 

../ctheta.so : calctheta.cpp
	${CC}  -ansi -fPIC -pedantic -shared  -o $@ $? -lc



../ctheta.dll : ./calctheta.cpp
	#g++  -ansi -fPIC -pedantic -shared	-o $@ $?
	cl /D_USRDLL /D_WINDLL calctheta.cpp /link /dll /out:..\ctheta.dll