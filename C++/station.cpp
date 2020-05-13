// ./station East_Station 4003 4004 4002 4008 4006


// Server program 
#include <arpa/inet.h> 
#include <errno.h> 
#include <netinet/in.h> 
#include <signal.h> 
#include <stdio.h> 
#include <stdlib.h> 
#include <strings.h> 
#include <sys/socket.h> 
#include <sys/types.h> 
#include <unistd.h>
#include <unistd.h>
#include <string.h>
#include <sys/select.h>

#include <typeinfo>
#include <iterator>
#include <string>
#include <iostream>
#include <fstream>

using namespace std;

#define MAXLINE 1024
#define MAXSTATIONS 100

int max(int x, int y) 
{ 
    if (x > y) 
        return x; 
    else
        return y; 
} 


int main(int argc, char const *argv[]) 
{   
    // ARGUMENTS____________________________________________________________
    
    string stationName = argv[1];
    int PORT = stoi(argv[2]);
    int UDP_port = stoi(argv[3]);
    string neighbours[argc-4];
    
    for(int i=4; i<argc; i++){
        neighbours[i-4] = stoi(argv[i]);
    }
    
    // READING STATION INFO_________________________________________________
    string text;
    int routeCount = 0;
    
    string flname = "tt-" + stationName + ".txt";
    cout << "____________________________txt file name \n";
    cout << flname + "\n";
    
    
    ifstream MyReadFile(flname);
    while(getline (MyReadFile, text)){
        cout << text + "\n"
        routeCount = routeCount + 1;
    }
    MyReadFile.close();
    
    string routes[routeCount];
    
    
    cout << "____________________________" + routeCount; 
    
    
    // NETWORKING____________________________________________________________
    char msg[] = "HTTP/1.1 200 OK\r\nContent-Type: text/html; charset=ISO-8859-4 \r\n\r\n<h1>This is the msg from the server</h1>";
    
    int listenfd, connfd, udpfd, nready, maxfdp1; 
    char buffer[MAXLINE]; 
    pid_t childpid; 
    fd_set rset; 
    ssize_t n; 
    socklen_t len; 
    const int on = 1; 
    struct sockaddr_in cliaddr, servaddr; 
    void sig_chld(int); 
    char *message = "Hello, you connected to me!";
  
    /* create listening TCP socket */
    listenfd = socket(AF_INET, SOCK_STREAM, 0); 
    bzero(&servaddr, sizeof(servaddr)); 
    servaddr.sin_family = AF_INET; 
    servaddr.sin_addr.s_addr = htonl(INADDR_ANY); 
    servaddr.sin_port = htons(PORT); 
  
    // binding server addr structure to listenfd 
    bind(listenfd, (struct sockaddr*)&servaddr, sizeof(servaddr)); 
    listen(listenfd, 10); 
  
    /* create UDP socket */
    udpfd = socket(AF_INET, SOCK_DGRAM, 0); 
    // binding server addr structure to udp sockfd 
    bind(udpfd, (struct sockaddr*)&servaddr, sizeof(servaddr)); 
  
    // clear the descriptor set 
    FD_ZERO(&rset); 
  
    // get maxfd 
    maxfdp1 = max(listenfd, udpfd) + 1; 
    for (;;) { 
  
        // set listenfd and udpfd in readset 
        FD_SET(listenfd, &rset); 
        FD_SET(udpfd, &rset); 
  
        // select the ready descriptor 
        nready = select(maxfdp1, &rset, NULL, NULL, NULL); 
  
        // if tcp socket is readable then handle 
        // it by accepting the connection 
        if (FD_ISSET(listenfd, &rset)) { 
            len = sizeof(cliaddr); 
            connfd = accept(listenfd, (struct sockaddr*)&cliaddr, &len); 
            if ((childpid = fork()) == 0) { 
                close(listenfd); 
                bzero(buffer, sizeof(buffer)); 
                printf("Message From TCP client: "); 
                read(connfd, buffer, sizeof(buffer));
                puts(buffer); 
                send(connfd, msg, strlen(msg), 0);
                close(connfd); 
                exit(0);
            } 
            close(connfd);
            break;
        } 
        // if udp socket is readable receive the message. 
        if (FD_ISSET(udpfd, &rset)) { 
            len = sizeof(cliaddr); 
            bzero(buffer, sizeof(buffer)); 
            printf("\nMessage from UDP client: "); 
            n = recvfrom(udpfd, buffer, sizeof(buffer), 0, 
                         (struct sockaddr*)&cliaddr, &len); 
            puts(buffer); 
            sendto(udpfd, (const char*)message, sizeof(buffer), 0, 
                   (struct sockaddr*)&cliaddr, sizeof(cliaddr)); 
        } 
    } 
} 