
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


#define PORT 5000 
#define MAXLINE 1024 