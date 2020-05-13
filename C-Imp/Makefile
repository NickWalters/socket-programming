#Compilation flags
CC		= cc -std=c99
CFLAGS	= -Wall -Werror -pedantic
#Compilation variables/dependencies
SOURCE	= server.c

#Compile the program
c_server : $(SOURCE) $(HEADERS)
	$(CC) $(CFLAGS) -o c_server $(SOURCE)

clobber :
	rm -f c_server