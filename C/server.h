
// Server program 
#include <stdio.h> 
#include <stdlib.h>
#include <string.h> 
#include <strings.h> 
#include <arpa/inet.h> 
#include <errno.h> 
#include <netinet/in.h> 
#include <signal.h> 
#include <sys/socket.h> 
#include <sys/types.h> 
#include <unistd.h> 
#include <sys/stat.h>
#include <sys/time.h>
#include <errno.h>
#include <sys/wait.h>
#include <signal.h>

#include <iostream>
#include <string>
#include <fstream>


#define MAXLINE 1024
#define BUFFER_SIZE   1024
#define MAX_STATIONS 100

