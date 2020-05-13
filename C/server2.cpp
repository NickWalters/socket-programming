#include "server.h"

using namespace std;

#define MAXLINE 1024
#define BUFFER_SIZE   1024
#define MAX_STATIONS 100

int PORT = 0; /* TCP */
int UDP_PORT = 0;
string stationName = "";
const char *neighbours[MAX_STATIONS];


int max(int x, int y) 
{ 
	if (x > y) 
		return x; 
	else
		return y; 
} 



int main(int argc, char *argv[]) 
{ 
	if(argc < 2){
			fprintf(stderr,"ERROR, no port provided\n");
			exit(1);
	}
	else{
		for(int i=1; i<argc; ++i){
			if(i==0){
				continue;
			}
			if(i == 1){
				stationName = argv[1];
				cout << ("Station Name is: " + stationName);
			}
			if(i == 2){
				PORT = atoi(argv[2]);
			}
			if(i == 3){
				UDP_PORT = atoi(argv[3]);
			}
		}
	}
	
	int listenfd, connfd, udpfd, nready, maxfdp1; 
	char buffer[MAXLINE]; 
	pid_t childpid; 
	fd_set rset; 
	ssize_t n; 
	socklen_t len; 
	/* const int on = 1; */
	struct sockaddr_in cliaddr, servaddr; 
	string message = "Hello Client"; 
	void sig_chld(int);
	
  
	/* create listening TCP socket */
	listenfd = socket(AF_INET, SOCK_STREAM, 0);
	if (listenfd < 0) {
		perror("ERROR opening socket");
	} 
	bzero((char *) &servaddr, sizeof(servaddr)); 
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
				write(connfd, *message, sizeof(buffer)); 
				close(connfd); 
				exit(0); 
			} 
			close(connfd); 
		} 
		// if udp socket is readable receive the message. 
		if (FD_ISSET(udpfd, &rset)) { 
			len = sizeof(cliaddr); 
			bzero(buffer, sizeof(buffer)); 
			printf("\nMessage from UDP client: "); 
			n = recvfrom(udpfd, buffer, sizeof(buffer), 0, 
						 (struct sockaddr*)&cliaddr, &len); 
			puts(buffer); 
			sendto(udpfd, *message, sizeof(buffer), 0, 
				   (struct sockaddr*)&cliaddr, sizeof(cliaddr)); 
		} 
	} 
} 
